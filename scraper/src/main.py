import csv
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime

import brotli
import gzip
import pandas as pd
import requests
from bs4 import BeautifulSoup
from empiricaldist import Pmf
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ExpectedConditions
from selenium.webdriver.support.wait import WebDriverWait

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
        def even_odd(nums):
            nums = [1 if int(x) % 2 == 0 else 0 for x in nums.split('|')]
            even = sum(nums)
            odd = 5 - even
            return (even, odd)

        def lo_hi(nums):
            nums = [1 if int(x) <= self.mid else 0 for x in nums.split('|')]
            lo = sum(nums)
            hi = 5 - lo
            return (lo, hi)

        def get_sum(nums):
            return sum([int(x) for x in nums.split('|')])

        def consecutive(nums):
            nums = sorted([int(x) for x in nums.split('|')])
            prev = -sys.maxsize
            count = 0
            consecutives = []
            for num in nums:
                if prev + 1 == num:
                    count += 1
                elif count > 0:
                    consecutives.append(count)
                    count = 0
                prev = num
            if count > 0:
                consecutives.append(count)
            return tuple(consecutives) if consecutives else (0,)

        def format_analysis_items(items):
            arr = []
            for k, v in items:
                if isinstance(k, tuple):
                    key_str = ','.join([str(x) for x in k])
                else:
                    key_str = str(k)
                arr.append({
                    'type': key_str,
                    'pct': f'{format(v * 100, ".2f")}%'
                })
            return arr

        df = pd.read_csv(self.output_absolute_path)
        df['even_odd'] = df['white_balls'].apply(lambda x: even_odd(x))
        df['lo_hi'] = df['white_balls'].apply(lambda x: lo_hi(x))
        df['consecutive'] = df['white_balls'].apply(lambda x: consecutive(x))
        df['sum'] = df['white_balls'].apply(lambda x: get_sum(x))

        df['even_odd_lo_hi'] = df[['even_odd', 'lo_hi']].apply(tuple, axis=1)
        df['even_odd_consecutive'] = df[['even_odd', 'consecutive']].apply(tuple, axis=1)
        df['lo_hi_consecutive'] = df[['lo_hi', 'consecutive']].apply(tuple, axis=1)
        df['even_odd_lo_hi_consecutive'] = df[['even_odd', 'lo_hi', 'consecutive']].apply(tuple, axis=1)

        even_odd_prob = Pmf.from_seq(df['even_odd']).sort_values(ascending=False)
        lo_hi_prob = Pmf.from_seq(df['lo_hi']).sort_values(ascending=False)
        consecutive_prob = Pmf.from_seq(df['consecutive']).sort_values(ascending=False)
        even_odd_lo_hi_prob = Pmf.from_seq(df['even_odd_lo_hi']).sort_values(ascending=False)
        even_odd_consecutive_prob = Pmf.from_seq(df['even_odd_consecutive']).sort_values(ascending=False)
        lo_hi_consecutive_prob = Pmf.from_seq(df['lo_hi_consecutive']).sort_values(ascending=False)
        even_odd_lo_hi_consecutive_prob = Pmf.from_seq(df['even_odd_lo_hi_consecutive']).sort_values(ascending=False)

        sum_bins = pd.cut(df['sum'], bins=range(0, 351, 50))
        sum_prob = Pmf.from_seq(sum_bins).sort_values(ascending=False)

        stats = {
            'updated_date': f'{df.iloc[-1]["date"]}',
            'total_draws': len(df.index),
            'white_balls': {
                'even_odd': format_analysis_items(even_odd_prob.items()),
                'low_high': format_analysis_items(lo_hi_prob.items()),
                'consecutive': format_analysis_items(consecutive_prob.items()),
                'sum_distribution': format_analysis_items(sum_prob.items()),
                'even_odd_lo_hi': format_analysis_items(even_odd_lo_hi_prob.items()),
                'even_odd_consecutive': format_analysis_items(even_odd_consecutive_prob.items()),
                'lo_hi_consecutive': format_analysis_items(lo_hi_consecutive_prob.items()),
                'even_odd_lo_hi_consecutive': format_analysis_items(even_odd_lo_hi_consecutive_prob.items()),
            }
        }

        if 'red_ball' in df.columns:
            red_ball_prob = Pmf.from_seq(df['red_ball']).sort_values(ascending=False)
            stats['red_ball_hotness'] = format_analysis_items(red_ball_prob.items())
        if 'yellow_ball' in df.columns:
            yellow_ball_prob = Pmf.from_seq(df['yellow_ball']).sort_values(ascending=False)
            stats['yellow_ball_hotness'] = format_analysis_items(yellow_ball_prob.items())

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
        time.sleep(2)
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
                time.sleep(1)
                self.wait_and_click('//button[@class="loadMoreBtn button"]')
                time.sleep(1)
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
        # Attempt to avoid detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        r = requests.get(self.url, headers=headers)
        encoding = r.headers.get('content-encoding', '')
        logging.info(f'Content-Encoding={encoding}')
        if 'br' in encoding:
            text = brotli.decompress(r.content).decode('utf-8', errors='ignore')
        elif 'gzip' in encoding:
            text = gzip.decompress(r.content).decode('utf-8', errors='ignore')
        else:
            text = r.text
        soup = BeautifulSoup(text, features='html.parser')
        previous_draw_arr = soup.find_all('a', {'class': 'card'})
        if len(previous_draw_arr) == 0:
            logging.error('Raw response:')
            logging.error(f'Content-Encoding={encoding}')
            logging.error(r.text)
            raise Exception('Unable to find previous draw information on Powerball page')
        previous_draw = previous_draw_arr[0]
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
                time.sleep(1)
                self.wait_and_click('//button[@id="loadMore"]')
                time.sleep(1)
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
