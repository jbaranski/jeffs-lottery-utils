import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpectedConditions

logging.getLogger().setLevel(logging.INFO)


@dataclass()
class Lottery:
    output_absolute_path: str
    chrome_driver: WebDriver = field(init=False)

    def __post_init__(self):
        try:
            with open(self.output_absolute_path, 'r') as f:
                self.last_entry = f.readlines()[-1].strip()
        except FileNotFoundError:
            self.last_entry = ''
            logging.info(f'Unable to read last entry because {self.output_absolute_path} does not exist')

    def get_latest_number(self):
        raise NotImplementedError

    def get_historical_numbers(self):
        raise NotImplementedError

    def wait_and_click(self, xpath: str) -> None:
        el = WebDriverWait(self.chrome_driver, 2).until(ExpectedConditions.element_to_be_clickable((By.XPATH, xpath)))
        el.click()

    @staticmethod
    def chrome_driver_factory() -> WebDriver:
        options = {
            'dev': [
                '--window-size=1200,1200',
                '--ignore-certificate-errors'
            ],
            'prod': [
                '--headless',
                '--disable-gpu',
                '--window-size=1920,1200',
                '--ignore-certificate-errors',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--remote-debugging-port=9222'
            ]
        }
        chrome_options = webdriver.ChromeOptions()
        for option in options[os.getenv('CHROME_OPTS', 'prod')]:
            chrome_options.add_argument(option)
        return webdriver.Chrome(options=chrome_options)


@dataclass()
class Powerball(Lottery):
    url = 'https://www.powerball.com/previous-results?gc=powerball'

    def __post_init__(self):
        super().__post_init__()

    def get_latest_number(self) -> None:
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, features='html.parser')
        previous_draw = soup.find_all('a', {'class': 'card'})[0]
        draw_date = previous_draw.find_all('h5', {'class': 'card-title'})[0].get_text(strip=True)
        # Example input: Wed, Nov 27, 2024
        draw_date_parsed = datetime.strptime(draw_date, '%a, %b %d, %Y').strftime('%m/%d/%Y')
        draw_numbers = '|'.join([x.get_text(strip=True) for x in previous_draw.find_all('div', {'class': 'item-powerball'})])
        draw_power_play = previous_draw.find_all('span', {'class': 'multiplier'})[0].get_text(strip=True).upper()
        entry = f'{draw_date_parsed},{draw_numbers},{draw_power_play}\n'
        if entry.strip() != self.last_entry:
            with open(self.output_absolute_path, 'a') as f:
                f.write(entry)
        else:
            logging.info('Last entry matches latest Powerball number fetched')

    def get_historical_numbers(self) -> None:
        self.chrome_driver = Lottery.chrome_driver_factory()
        self.chrome_driver.get(self.url)
        time.sleep(2)
        self.chrome_driver.execute_script('window.stop();')
        self.wait_and_click('//button[@id="onetrust-reject-all-handler"]')
        time.sleep(2)
        self.wait_and_click('//button[@class="fs-close-button fs-close-button-sticky"]')
        time.sleep(2)
        count = 0
        while count < 100:
            try:
                self.wait_and_click('//button[@id="loadMore"]')
                time.sleep(.5)
            except TimeoutException:
                # The load more button is no longer available
                break
            count += 1
        links = self.chrome_driver.find_elements(By.XPATH, '//a[@class="card"]')
        items = []
        for link in links:
            draw_date = link.find_elements(By.XPATH, './/h5[@class="card-title"]')[0].text.strip()
            # Example input: Wed, Nov 27, 2024
            draw_date_parsed = datetime.strptime(draw_date, '%a, %b %d, %Y').strftime('%m/%d/%Y')
            draw_numbers = '|'.join([x.text.strip() for x in link.find_elements(By.XPATH, './/div[contains(@class, "item-powerball")]')])
            draw_power_play = link.find_elements(By.XPATH, './/span[@class="multiplier"]')
            # Continuously hitting load more loads dates without numbers... just stop if we ever hit that
            if len(draw_power_play) == 0 and not draw_numbers:
                break
            draw_power_play = '0X' if len(draw_power_play) == 0 else draw_power_play[0].text.strip().upper()
            items.append(f'{draw_date_parsed},{draw_numbers},{draw_power_play}\n')
        with open(self.output_absolute_path, 'w') as f:
            f.write('date,numbers,power_play\n')
            f.writelines(list(reversed(items)))


@dataclass()
class MegaMillions(Lottery):
    chrome_driver: WebDriver = field(init=False)
    url = 'https://www.megamillions.com/Winning-Numbers/Previous-Drawings.aspx'

    def __post_init__(self):
        super().__post_init__()
        self.chrome_driver = Lottery.chrome_driver_factory()

    def get_latest_number(self) -> None:
        self.chrome_driver.get(self.url)
        previous_draw = self.chrome_driver.find_elements(By.XPATH, '//a[@class="prevDrawItem"]')
        entry = MegaMillions.extract_one_draw(previous_draw[0])
        if entry.strip() != self.last_entry:
            with open(self.output_absolute_path, 'a') as f:
                f.write(entry)
        else:
            logging.info('Last entry matches latest Mega Millions number fetched')

    def get_historical_numbers(self) -> None:
        self.chrome_driver.get(self.url)
        count = 0
        while count < 100:
            try:
                self.wait_and_click('//button[@class="loadMoreBtn button"]')
                time.sleep(.5)
            except TimeoutException:
                # The load more button is no longer available
                break
            count += 1
        links = self.chrome_driver.find_elements(By.XPATH, '//a[@class="prevDrawItem"]')
        items = []
        for link in links:
            items.append(MegaMillions.extract_one_draw(link))
        with open(self.output_absolute_path, 'w') as f:
            f.write('date,numbers,megaplier\n')
            f.writelines(list(reversed(items)))

    @staticmethod
    def extract_one_draw(link: WebElement) -> str:
        draw_date = link.find_elements(By.XPATH, './h5[@class="drawItemDate"]')[0].text.strip()
        draw_numbers = [x.text.strip() for x in link.find_elements(By.XPATH, './ul[@class="numbers"]')[0].find_elements(By.XPATH, './li[contains(@class, "ball")]')]
        draw_megaplier = link.find_elements(By.XPATH, './span[@class="megaplier pastNumMP"]')[0].text.strip().upper()
        return f'{draw_date},{"|".join(draw_numbers)},{draw_megaplier}\n'


def megamillions():
    m = MegaMillions(f'{os.getenv("GITHUB_WORKSPACE")}/numbers/megamillions.csv')
    m.get_latest_number()


def powerball():
    p = Powerball(f'{os.getenv("GITHUB_WORKSPACE")}/numbers/powerball.csv')
    p.get_latest_number()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Unexpected number of arguments')

    kind = sys.argv[1]

    if kind == 'megamillions':
        megamillions()
    elif kind == 'powerball':
        powerball()
    elif kind == 'test':
        megamillions()
        powerball()
    else:
        raise Exception('Unexpected argument')
