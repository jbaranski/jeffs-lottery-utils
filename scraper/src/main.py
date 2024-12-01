import csv
import json
import logging
import os
import sys
import time
from collections import defaultdict
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
    high: int
    special_high: int
    chrome_driver: WebDriver = field(init=False)

    def __post_init__(self):
        try:
            with open(self.output_absolute_path, 'r') as f:
                self.last_entry = f.readlines()[-1].strip()
        except FileNotFoundError:
            self.last_entry = ''
            logging.info(f'Unable to read last entry because {self.output_absolute_path} does not exist')

        self.mid = self.high // 2
        self.special_mid = self.special_high // 2

    def get_latest_number(self):
        raise NotImplementedError

    def get_historical_numbers(self):
        raise NotImplementedError

    def wait_and_click(self, xpath: str) -> None:
        el = WebDriverWait(self.chrome_driver, 2).until(ExpectedConditions.element_to_be_clickable((By.XPATH, xpath)))
        el.click()

    def csv_to_json(self):
        data = []
        with open(self.output_absolute_path, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                row['white_balls'] = [int(x) for x in row['white_balls'].split('|')]
                if 'yellow_ball' in row:
                    row['yellow_ball'] = int(row['yellow_ball'])
                if 'red_ball' in row:
                    row['red_ball'] = int(row['red_ball'])
                data.append(row)
        with open(self.output_absolute_path.replace('.csv', '.json'), 'w') as f:
            json.dump(data, f, indent=2)

    def analysis(self):
        """
        Quick and dirty analysis after the draw is updated
        """
        with open(self.output_absolute_path.replace('.csv', '.json'), 'r') as f:
            data = json.load(f)
            L = len(data)
            even_odd = [0] * 6
            low_high = [0] * 6
            consecutive = defaultdict(int)
            for row in data:
                even_count = 0
                low_count = 0
                consecutive_count = 0
                consecutives = []
                prev_white_ball = -1
                for white_ball in sorted(row['white_balls']):
                    if white_ball % 2 == 0:
                        even_count += 1
                    if white_ball <= self.mid:
                        low_count += 1
                    if prev_white_ball + 1 == white_ball:
                        consecutive_count += 1
                    elif consecutive_count > 0:
                        consecutives.append(consecutive_count)
                        consecutive_count = 0
                    prev_white_ball = white_ball

                if consecutive_count > 0:
                    consecutives.append(consecutive_count)

                LC = len(consecutives)
                if LC > 1:
                    consecutive[','.join([str(x) for x in consecutives])] += 1
                elif LC == 1:
                    consecutive[str(consecutives[0])] += 1
                else:
                    consecutive['0'] += 1
                even_odd[even_count] += 1
                low_high[low_count] += 1
            even_odd = [(x, f'{format((x / L) * 100, ".2f")}%') for x in even_odd]
            low_high = [(x, f'{format((x / L) * 100, ".2f")}%') for x in low_high]

            # consecutive = sorted([(k, v, f'{format((v / L) * 100, ".2f")}%') for k, v in consecutive.items()])
            # print(even_odd)
            # print(low_high)
            # print(consecutive)
            # print()

            consecutive_output = []
            for k, v in consecutive.items():
                consecutive_output.append({
                    'type': k,
                    'count': v,
                    'pct': f'{format((v / L) * 100, ".2f")}%'
                })

            stats = {
                'total_draws': L,
                'white_balls': {
                    'even_odd': [
                        {
                            'type': '0 even/5 odd',
                            'count': even_odd[0][0],
                            'pct': even_odd[0][1]
                        },
                        {
                            'type': '1 even/4 odd',
                            'count': even_odd[1][0],
                            'pct': even_odd[1][1]
                        },
                        {
                            'type': '2 even/3 odd',
                            'count': even_odd[2][0],
                            'pct': even_odd[2][1]
                        },
                        {
                            'type': '3 even/2 odd',
                            'count': even_odd[3][0],
                            'pct': even_odd[3][1]
                        },
                        {
                            'type': '4 even/1 odd',
                            'count': even_odd[4][0],
                            'pct': even_odd[4][1]
                        },
                        {
                            'type': '5 even/0 odd',
                            'count': even_odd[5][0],
                            'pct': even_odd[5][1]
                        }
                    ],
                    'low_high': [
                        {
                            'type': '0 low/5 high',
                            'count': low_high[0][0],
                            'pct': low_high[0][1]
                        },
                        {
                            'type': '1 low/4 high',
                            'count': low_high[1][0],
                            'pct': low_high[1][1]
                        },
                        {
                            'type': '2 low/3 high',
                            'count': low_high[2][0],
                            'pct': low_high[2][1]
                        },
                        {
                            'type': '3 low/2 high',
                            'count': low_high[3][0],
                            'pct': low_high[3][1]
                        },
                        {
                            'type': '4 low/1 high',
                            'count': low_high[4][0],
                            'pct': low_high[4][1]
                        },
                        {
                            'type': '5 low/0 high',
                            'count': low_high[5][0],
                            'pct': low_high[5][1]
                        }
                    ],
                    'consecutive': consecutive_output
                }
            }
            with open(self.output_absolute_path.replace('.csv', '-analysis.json'), 'w') as f:
                f.write(json.dumps(stats, indent=2))

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
class MegaMillions(Lottery):
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
        self.chrome_driver.quit()

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
            f.write('date,white_balls,yellow_ball,megaplier\n')
            f.writelines(list(reversed(items)))
        self.chrome_driver.quit()

    @staticmethod
    def extract_one_draw(link: WebElement) -> str:
        draw_date = link.find_elements(By.XPATH, './h5[@class="drawItemDate"]')[0].text.strip()
        draw_numbers = [x.text.strip() for x in link.find_elements(By.XPATH, './ul[@class="numbers"]')[0].find_elements(By.XPATH, './li[contains(@class, "ball")]')]
        draw_white_balls = '|'.join(draw_numbers[:-1])
        draw_yellow_ball = ''.join(draw_numbers[-1:])
        draw_megaplier = link.find_elements(By.XPATH, './span[@class="megaplier pastNumMP"]')[0].text.strip().upper()
        return f'{draw_date},{draw_white_balls},{draw_yellow_ball},{draw_megaplier}\n'


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
        draw_numbers = [x.get_text(strip=True) for x in previous_draw.find_all('div', {'class': 'item-powerball'})]
        draw_white_balls = '|'.join(draw_numbers[:-1])
        draw_red_ball = ''.join(draw_numbers[-1:])
        draw_power_play = previous_draw.find_all('span', {'class': 'multiplier'})[0].get_text(strip=True).upper()
        entry = f'{draw_date_parsed},{draw_white_balls},{draw_red_ball},{draw_power_play}\n'
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
            draw_numbers = [x.text.strip() for x in link.find_elements(By.XPATH, './/div[contains(@class, "item-powerball")]')]
            draw_white_balls = '|'.join(draw_numbers[:-1])
            draw_red_ball = ''.join(draw_numbers[-1:])
            draw_power_play = link.find_elements(By.XPATH, './/span[@class="multiplier"]')
            # Continuously hitting load more loads dates without numbers... just stop if we ever hit that
            if len(draw_power_play) == 0 and not draw_numbers:
                break
            draw_power_play = '0X' if len(draw_power_play) == 0 else draw_power_play[0].text.strip().upper()
            items.append(f'{draw_date_parsed},{draw_white_balls},{draw_red_ball},{draw_power_play}\n')
        with open(self.output_absolute_path, 'w') as f:
            f.write('date,white_balls,red_ball,power_play\n')
            f.writelines(list(reversed(items)))
        self.chrome_driver.quit()


def megamillions():
    m = MegaMillions(f'{os.getenv("GITHUB_WORKSPACE")}/numbers/megamillions.csv', 70, 25)
    # m.get_historical_numbers()
    m.get_latest_number()
    m.csv_to_json()
    m.analysis()


def powerball():
    p = Powerball(f'{os.getenv("GITHUB_WORKSPACE")}/numbers/powerball.csv', 69, 26)
    # p.get_historical_numbers()
    p.get_latest_number()
    p.csv_to_json()
    p.analysis()


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
