#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display

import time
import datetime
import sys
import argparse
import os
import logging

import config_reader

# needs to be set by the user
from credentials import USERNAME
from credentials import PASSWORD
from credentials import STUDIO_ID


def get_weekday(driver, line_cnt):
    try:
        x_path_weekday = f'/html/body/div[4]/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[{line_cnt}]/td/b/span'
        weekday = driver.find_element(By.XPATH, x_path_weekday)
    except NoSuchElementException:
        return None
    return weekday.text.strip()

def x_path_exists(driver, x_path):
    try:
        driver.find_element(By.XPATH, x_path)
    except NoSuchElementException:
        return False
    return True

def get_workout_index(workout_index_list, day, time, type):
    for workout in workout_index_list:
        if workout[1] == day and workout[2] == time and workout[3] == type:
            if workout[4] != "book":
                logger.error(f"Booking not possible for {day}, {time}, {type}")
                sys.exit(1)
            else:
                return workout[0]
    else:
        logging.warning(f"Requested workout doesn't exists: {day}, {time}, {type}")
        logging.warning(f"Following workouts could be found:\n{workout_index_list}\n")
        sys.exit(1)


def login(driver):
    driver.get(f"https://clients.mindbodyonline.com/ASP/ws.asp?studioId={STUDIO_ID}")

    # Wait for the page to load and find the username and password input fields
    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "requiredtxtUserName")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "requiredtxtPassword")))

    # Enter the credentials and submit the form
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

def switch_to_kursplan(driver):
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="tabA7"]')))
    kursplan_button = driver.find_element(By.XPATH, '//*[@id="tabA7"]')
    kursplan_button.click()

def next_week(driver):
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="week-arrow-r"]')))

    week_arrow = driver.find_element(By.XPATH, '//*[@id="week-arrow-r"]')
    week_arrow.click()
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="week-arrow-r"]')))


def get_workout_index_list(driver):
    stopSearching = False
    line_counter = 0
    skip_counter = 0

    workout_index_list = []
    last_weekday = ""

    while not stopSearching:
        if skip_counter > 10:
            stopSearching = True
        try:
            weekday_return = get_weekday(driver, line_counter)
            last_weekday = weekday_return if weekday_return != None else last_weekday

            x_path_time = f'/html/body/div[4]/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[{line_counter}]/td[1]'
            time_field = driver.find_element(By.XPATH, x_path_time)

            x_path_class_type = f'/html/body/div[4]/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[{line_counter}]/td[3]/a'
            class_type = driver.find_element(By.XPATH, x_path_class_type)

            x_path_sign_button = f'/html/body/div[4]/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[{line_counter}]/td[2]/input'
            if x_path_exists(driver, x_path_sign_button):
                booking_button = "book"
            else:
                booking_button = "no booking buttom"

            info = [line_counter, last_weekday, time_field.text.strip(), class_type.text.strip(), booking_button]
            workout_index_list.append(info)

            skip_counter = 0
        except Exception as e:
            skip_counter += 1

        line_counter += 1

    return workout_index_list    

def get_todays_weekday():
    # locale.setlocale(locale.LC_TIME, "de_DE")
    today = datetime.datetime.today()
    weekday_translation_dict = {
        "Monday": "Montag",
        "Tuesday": "Dienstag",
        "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag",
        "Friday": "Freitag",
        "Saturday": "Samstag",
        "Sunday": "Sonntag",
    }

    weekday_name = today.strftime("%A")
    return(weekday_translation_dict[weekday_name])

def sign_up_botton(driver, index):
    try:
        x_path_sign_button = f'/html/body/div[4]/div[5]/div/div/div[2]/div/table/tbody/tr[2]/td/table/tbody/tr[{index}]/td[2]/input'
        sign_button = driver.find_element(By.XPATH, x_path_sign_button)
        sign_button.click()

    except NoSuchElementException:
        logging.error(f"Problems with the booking, sign up botton was not found.")

def submit_botton(driver):
    wait = WebDriverWait(driver, 10)

    try:
        x_path_finalize_booking = f'//*[@id="SubmitEnroll1"]'
        wait.until(EC.presence_of_element_located((By.XPATH, x_path_finalize_booking)))
        finalize_booking = driver.find_element(By.XPATH, x_path_finalize_booking)
        finalize_booking.click()
    except NoSuchElementException:
        logging.error("Problems with the booking, submit botton was not found.")
    except TimeoutException:
        logging.error("Booking could not be finalized. Submit button was pressed but no success")
    

def check_for_success(driver):
    wait = WebDriverWait(driver, 10)
    try:
        x_path_successful_book = '/html/body/div[2]/div[5]/div/div/div[2]/div/div[2]/strong'
        wait.until(EC.presence_of_element_located((By.XPATH, x_path_successful_book)))
        successful_book = driver.find_element(By.XPATH, x_path_successful_book)
        if "You've Booked" in successful_book.text:
            logging.info("Booking was successful!")
        else:
            logging.error("Something went wrong with the booking.")

    except NoSuchElementException:
        weekday = get_todays_weekday()
        logging.error(f"Problems with the booking.. For day: {weekday}")
    except TimeoutException:
        logging.warning("Success element could not be found. Are you already signed up for this class?")

def get_date_in_x_days(days):
    today = datetime.date.today()
    two_weeks = today + datetime.timedelta(days=days)
    return two_weeks


def parse_arguments():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to YAML config file. The config file lists the days, hours and types of workouts you want to book.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-hl', '--headless', action='store_true', help='Enable headless mode')

    args = parser.parse_args()

    config_path = args.config
    debug_mode = args.debug
    headless_mode = args.headless

    if not os.path.isfile(config_path):
        raise argparse.ArgumentTypeError(f'{config_path} does not exist or is not a file')
    
    return config_path, debug_mode, headless_mode


def get_logger(debug_mode):
    file_logging = False

    if debug_mode:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if file_logging:
        file_handler = logging.FileHandler('log_file.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def main():
    config_path, debug_mode, headless_mode = parse_arguments()
    global logger
    logger = get_logger(debug_mode)
    
    desired_bookings = config_reader.BookingConfig(config_path)
    logger.info("Requested bookings:")
    logger.info(desired_bookings)

    if headless_mode:
        display = Display(visible=0, size=(800, 600))
        display.start()
        options = Options()
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)
    else:
        driver = webdriver.Chrome()

    login(driver)
    switch_to_kursplan(driver)
    next_week(driver)
    time.sleep(3)
    next_week(driver)
    workout_index_list = get_workout_index_list(driver)

    weekday_today = get_todays_weekday()
    slot = desired_bookings.get_booking_of_weekday(weekday_today)

    if slot != None:
        desired_day = slot.weekday
        desired_time = slot.hour
        desired_type = slot.type

        date = get_date_in_x_days(14)
        logging.info(f"Try to book workout: {date}, {desired_day}, {desired_time}, {desired_type}")
        workout_index = get_workout_index(workout_index_list, desired_day, desired_time, desired_type)

        sign_up_botton(driver, workout_index)
        submit_botton(driver)
        check_for_success(driver)
    else:
        logging.info("No booking for today desired.")

    driver.quit()
    

if __name__ == "__main__":
    main()
