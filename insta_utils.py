from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


from datetime import datetime
import json
import re
import os
import logging.handlers
import logging
import requests
import time
from colorama import Fore, Style, init
init(convert=True)
log = logging.info


def input_checker(incoming):
   get_id = re.findall(r"instagram.com/([-a-z_A-Z.0-9]*)", incoming)
   if get_id == []:
       return incoming

   else:
       return get_id[0]


def get_broswer(USERNAME,PASSWORD,BROWSER_PROFILE):
    #BROWSER_PATH = config_data.get('BROWSER_PATH') + config_data[BROWSER_PROFILE].get('profile')
    BROWSER_PATH_BASIC = os.environ.get('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\'
    BROWSER_PATH = BROWSER_PATH_BASIC + BROWSER_PROFILE
    #browser_argument = "user-data-dir=" + BROWSER_PATH
    browser_argument = "user-data-dir=" + BROWSER_PATH
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(browser_argument)
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='C://chromedriver.exe')
    time.sleep(5)
    driver.maximize_window()

    # browser_argument = "user-data-dir=" + BROWSER_PATH
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument(browser_argument)
    #driver = webdriver.Chrome(chrome_options=chrome_options)

    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(6)
    print("Insta id    :::    " + USERNAME)
    print("Insta pass  :::    " + PASSWORD)
    login_status = True
    try:
        try:
            logged_in_check = driver.find_element_by_css_selector('div.ctQZg')
            if logged_in_check:
                print('Logged in Already')
                return driver
        except:
            pass

        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username")))
        email_field.clear()
        email_field.send_keys(USERNAME)
        pass_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password")))
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        pass_field.send_keys(Keys.ENTER)
        print("loging in")
        login_status=False
        time.sleep(5)

    except Exception as ex:
        print (ex)
        print( "logged in already")

    # login layout 2
    if login_status:
        try:
            try:
                logged_in_check = driver.find_element_by_css_selector('div.ctQZg')
                if logged_in_check:
                    print('Logged in Already')
                    return driver
            except:
                pass

            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username")))
            email_field.clear()
            email_field.send_keys(USERNAME)
            pass_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password")))
            pass_field.clear()
            pass_field.send_keys(PASSWORD)
            pass_field.send_keys(Keys.ENTER)
            print("loging in")
            login_status=False
            time.sleep(5)

        except Exception as ex:
            print (ex)
            print( "logged in already")

    return driver

def get_session(username, password, BROWSER_PROFILE):
    driver = get_broswer(username, password, BROWSER_PROFILE)
    my_cookies = driver.get_cookies()
    session = requests.Session()
    session.headers.update({"Accept": "*/*", "Accept-Language": "en-US", "Accept-Encoding": "gzip, deflate, br", "Sec-Fetch-Mode": "cors"})
    try:
        for x in my_cookies:
            required_cookies = {
                "name":x['name'],
                "value":x['value']
                            }

            optional_args={
                "domain":x['domain'],
                "expires":None,
                'rest':{'HttpOnly': None},
                "path":x['path'],
                "secure":x['secure']
                        }
            my_cookie = requests.cookies.create_cookie(**required_cookies,**optional_args)
            session.cookies.set_cookie(my_cookie)

        print(Fore.GREEN + "Session Created Successfully")

        driver.quit()
        driver
    except Exception as ex:
        print(Fore.RED + 'Issue in Session')
        print('Exception  :::  ' + str(ex))
    return session

