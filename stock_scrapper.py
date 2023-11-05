# STOCK SCRAPPER
# Libraries
import time
import sqlite3
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService


class StockScrapper:
    def __init__(self) -> None:
        # URL to site
        self.url = "https://pl.investing.com/"

        # List of instruments to get
        self.instruments = {
            "currencies": ["eur-usd", "gbp-usd", "eur-pln", "usd-cad"],
            "equities": ["cdproject", "11bit", "nintendo-ltd", "activision-inc"],
            "commodities": ["gold", "silver", "platinum", "copper"],
        }

        # Creating lists of complete urls
        self.url_list = []

        for market in self.instruments:
            for instrument in self.instruments[market]:
                temp_url = "{0}{1}/{2}-historical-data".format(
                    self.url, market, instrument
                )
                self.url_list.append([instrument, temp_url])

        # Choosing time frame
        self.time_intervals = [
            "Daily",
            "Weekly",
            "Monthly",
        ]

        # Blank data frame with stock data
        self.stock_df = pd.DataFrame()

    def run_scrapper(self):
        """
        Method responsible for running scrapper and returning
        data frame with stock data
        """
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--lang=pl")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--verbose")
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing_for_trusted_sources_enabled": False,
                "safebrowsing.enabled": False,
                "excludeSwitches": "enable-logging",
            },
        )
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")

        # Loading the driver with chromedriver
        chrome_service = ChromeService()
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Downloading data from site for each instrument
        for instrument in self.url_list:
            for interval in self.time_intervals:
                print(
                    "Getting data for instrument: {0} with interval: {1}".format(
                        instrument[0], interval
                    )
                )
                temp_df = self.get_data(
                    driver=driver,
                    instrument_name=instrument[0],
                    url=instrument[1],
                    interval_name=interval,
                    start_year=2010,
                    end_year=2024,
                )
                time.sleep(5)
                self.stock_df = pd.concat([self.stock_df, temp_df], ignore_index=True)

        # Closing selenium driver
        driver.close()

        return self.stock_df

    def get_data(
        self,
        driver,
        instrument_name,
        url,
        interval_name,
        start_year=datetime.today().year - 10,
        end_year=datetime.today().year,
    ):
        """
        Method responsible for scrapping data for whole years from url with declaration of:
        - instrument - name of instrument
        - url - Url to instrument
        - interval - interval od data, e.g. daily, weekly, monthly
        - start_year - starting year for period to get
        - end_year - ending year for period to get
        """
        # Loading site
        driver.get(url)

        # Waiting for page to load
        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, "css-1uccc91-singleValue")
            )
            WebDriverWait(driver, 5).until(element_present)
        except:
            pass

        try:
            element_present = EC.presence_of_element_located(
                (By.CLASS_NAME, "css-1uccc91-singleValue")
            )
            WebDriverWait(driver, 5).until(element_present)
        except:
            pass

        # Accepting cache
        try:
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
        except Exception as e:
            print("Cookies already accepted!")

        # Matching interval to get
        interval = 0

        match interval_name:
            case "Daily":
                interval = 0
            case "Weekly":
                interval = 1
            case "Monthly":
                interval = 2
            case _:
                interval = 0
        # Selecting time interval
        while True:
            # Selecting time frame (one type)
            try:
                # Clicking time frame element
                driver.find_element(By.CLASS_NAME, "css-1uccc91-singleValue").click()

                # Choosing time frame (from html)
                #   react-select-2-option-0 = Daily
                #   react-select-2-option-1 = Weekly
                #   react-select-2-option-2 = Monthly
                time_frame = [
                    "react-select-2-option-0",
                    "react-select-2-option-1",
                    "react-select-2-option-2",
                ]

                driver.find_element(By.CLASS_NAME, "css-1uhu340-menu").find_element(
                    By.ID, time_frame[interval]
                ).click()
                break
            except:
                pass

            # Selecting time frame (second type)
            try:
                # Clicking time frame element
                time_frame_elem = [
                    elem
                    for elem in driver.find_elements(By.CLASS_NAME, "flex-1")
                    if elem.text == "Daily"
                    or elem.text == "Weekly"
                    or elem.text == "Monthly"
                ][0]
                time_frame_elem.click()

                # Choosing time frame (from list)
                #  0 = Daily
                #  1 = Weekly
                #  2 = Monthly
                time_frame = driver.find_elements(
                    By.CLASS_NAME, "historical-data-v2_menu-row-text__ZgtVH"
                )

                time_frame[interval].click()
                break
            except:
                pass

        time.sleep(1)

        # Selecting period of data
        while True:
            # First type of date picking
            try:
                checker = 0
                while checker < 2:
                    # Clicking on date box
                    driver.find_element(
                        By.CLASS_NAME, "DatePickerWrapper_input__UVqms"
                    ).click()

                    # Getting date elements
                    date_elements = driver.find_elements(
                        By.CLASS_NAME, "NativeDateInput_root__lZxBl"
                    )

                    # Selecting end year
                    date_elements[1].find_element(By.TAG_NAME, "input").clear()
                    date_elements[1].find_element(By.TAG_NAME, "input").send_keys(
                        "01.01.{0}".format(end_year - 1)
                    )

                    # Selecting start date
                    date_elements[0].find_element(By.TAG_NAME, "input").clear()
                    date_elements[0].find_element(By.TAG_NAME, "input").send_keys(
                        "01.01.{0}".format(start_year)
                    )

                    # Applying picked dates
                    driver.find_element(
                        By.CLASS_NAME, "HistoryDatePicker_footer__xzpr0"
                    ).find_element(By.TAG_NAME, "button").click()

                    time.sleep(5)
                    checker += 1
                break
            except:
                pass

            # Second type of date picking
            try:
                # Clicking date frame
                driver.find_element(
                    By.XPATH,
                    '//*[@class="flex py-2 px-[14px] gap-[14px] flex-1 border border-solid border-[#CFD4DA] rounded bg-[#FFF] shadow-select items-center "]',
                ).click()

                time.sleep(1)

                # Selecting end date
                end_date = [
                    elem for elem in driver.find_elements(By.TAG_NAME, "input")
                ][2]
                end_date.clear()
                end_date.send_keys("01.00.{0}".format(end_year))

                time.sleep(1)

                # Selecting start date
                start_date = [
                    elem for elem in driver.find_elements(By.TAG_NAME, "input")
                ][1]
                start_date.clear()
                start_date.send_keys("31.12.{0}".format(start_year - 1))

                # Accepting date
                driver.find_element(
                    By.XPATH,
                    '//*[@class="flex py-2.5 pl-4 pr-6 items-center gap-3 rounded bg-v2-blue shadow-button hover:bg-[#116BCC] cursor-pointer"]',
                ).click()
                break
            except:
                pass

        # Waiting for page to load full table
        time.sleep(5)

        # Getting table HTML
        while True:
            # First type of getting table
            try:
                # Getting table element with data
                table_wth_data = [
                    elem
                    for elem in driver.find_elements(By.TAG_NAME, "table")
                    if elem.get_attribute("data-test") == "historical-data-table"
                ][0]
                temp_stock_df = pd.read_html(
                    table_wth_data.get_attribute("outerHTML").replace(",", ".")
                )[0]

                # Currency of downloaded instrument
                intrument_currency = driver.find_element(
                    By.CLASS_NAME, "instrument-metadata_currency__XER9q"
                ).text.split("\n")[1]
                break
            except:
                time.sleep(1)

            # Second type of getting table
            try:
                # Getting table element with data
                table_wth_data = driver.find_element(
                    By.XPATH,
                    '//*[@class="w-full text-xs leading-4 overflow-x-auto freeze-column-w-1"]',
                )
                temp_stock_df = pd.read_html(
                    table_wth_data.get_attribute("outerHTML").replace(",", ".")
                )[0]

                # Currency of downloaded instrument
                intrument_currency = driver.find_element(
                    By.XPATH, '//*[@class="ml-1.5 font-bold"]'
                ).text
                break
            except:
                time.sleep(1)

        # Adding instrument name and its currency to data frame
        temp_stock_df.insert(0, "Instrument", instrument_name)
        temp_stock_df.insert(1, "Currency", intrument_currency)
        temp_stock_df.insert(2, "Interval", interval_name)

        return temp_stock_df

    def create_db(self, stock_df):
        """
        Method responsible for creating sqlite database
        """
        print("CREATING STOCK DATABASE!\n")

        # Creating column with currency_id
        temp_stock_df.insert(1, "currency_id", stock_df["Currency"])

        # Getting unique list od currencies
        currency_list = stock_df["Currency"].unique()

        # Mapping currency column with numbers
        temp_stock_df["currency_id"] = temp_stock_df["currency_id"].map(
            {currency: index + 1 for index, currency in enumerate(currency_list)}
        )

        # Data frame for currency identification
        currency_df = pd.DataFrame(
            [[index + 1, currency] for index, currency in enumerate(currency_list)],
            columns=["currency_id", "currency_name"],
        )

        # Creting column with instrument_id
        temp_stock_df.insert(0, "instrument_id", stock_df["Instrument"])

        # Getting unique list od currencies
        instrument_list = stock_df["Instrument"].unique()

        # Mapping instrument column with numbers
        temp_stock_df["instrument_id"] = temp_stock_df["instrument_id"].map(
            {instrument: index + 1 for index, instrument in enumerate(instrument_list)}
        )

        # Data frame for instrument identification
        instrument_df = pd.DataFrame(
            [
                [index + 1, instrument]
                for index, instrument in enumerate(instrument_list)
            ],
            columns=["instrument_id", "instrument_name"],
        )

        temp_stock_df = temp_stock_df.drop(["Instrument", "Currency"], axis=1)

        sql_insert_currency = [
            """create table if not EXISTS currency (
        currency_id integer PRIMARY key,
        currency_name text 
        );"""
        ]

        for currency in currency_df.values:
            currency_id = currency[0]
            currency_name = currency[1]
            temp_line = """insert into currency (currency_id, currency_name) values ({0}, '{1}');""".format(
                currency_id, currency_name
            )

            sql_insert_currency.append(temp_line)

        sql_insert_intrument = [
            """create table if not EXISTS instrument (
        instrument_id integer PRIMARY key,
        instrument_name text 
        );"""
        ]

        for instrument in instrument_df.values:
            instrument_id = instrument[0]
            instrument_name = instrument[1]
            temp_line = """insert into instrument (instrument_id, instrument_name) values ({0}, '{1}');""".format(
                instrument_id, instrument_name
            )

            sql_insert_intrument.append(temp_line)

        sql_insert_stock = [
            """create table if not EXISTS stock (
        id integer PRIMARY key AUTOINCREMENT,
        instrument_id integer not NULL,
        currency_id integer not null,
        date text not NULL,
        interval text,
        last_price real,
        open_price real,
        max_price real,
        min_price real,
        volume text,
        change text,
        FOREIGN KEY (instrument_id)
            REFERENCES instrument (instrument_id),
        FOREIGN KEY (currency_id)
            REFERENCES currency (currency_id)
        );"""
        ]

        for stock_row in temp_stock_df.fillna("").values:
            instrument_id = stock_row[0]
            currency_id = stock_row[1]
            interval = stock_row[2]
            date = stock_row[3]
            last_price = stock_row[4]
            open_price = stock_row[5]
            max_price = stock_row[6]
            min_price = stock_row[7]
            volume = stock_row[8]
            change = stock_row[9]

            if len(str(last_price).split(".")) == 3:
                last_price = str(last_price)
                last_price = float(
                    last_price.split(".")[0]
                    + last_price.split(".")[1]
                    + "."
                    + last_price.split(".")[2]
                )

            if len(str(open_price).split(".")) == 3:
                open_price = str(open_price)
                open_price = float(
                    open_price.split(".")[0]
                    + open_price.split(".")[1]
                    + "."
                    + open_price.split(".")[2]
                )

            if len(str(max_price).split(".")) == 3:
                max_price = str(max_price)
                max_price = float(
                    max_price.split(".")[0]
                    + max_price.split(".")[1]
                    + "."
                    + max_price.split(".")[2]
                )

            if len(str(min_price).split(".")) == 3:
                min_price = str(min_price)
                min_price = float(
                    min_price.split(".")[0]
                    + min_price.split(".")[1]
                    + "."
                    + min_price.split(".")[2]
                )

            temp_values = (
                "({0}, {1}, '{2}', '{3}', {4}, {5}, {6}, {7}, '{8}', '{9}')".format(
                    instrument_id,
                    currency_id,
                    date,
                    interval,
                    last_price,
                    open_price,
                    max_price,
                    min_price,
                    volume,
                    change,
                )
            )
            temp_line = """insert into stock (instrument_id, currency_id, date, interval, last_price, open_price, max_price, min_price, volume, change) values {0};""".format(
                temp_values
            )

            sql_insert_stock.append(temp_line)

        conn = sqlite3.connect("stock_prices.db")
        c = conn.cursor()

        [c.execute(sql_insert) for sql_insert in sql_insert_stock]

        [c.execute(sql_insert) for sql_insert in sql_insert_intrument]

        [c.execute(sql_insert) for sql_insert in sql_insert_currency]

        conn.commit()
        conn.close()

        print("DATABASE CREATED")
