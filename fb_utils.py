"""
    contains utility functions for grabbing facebook data
"""
import re
import os
import json
import requests
import time
from time import sleep
from selenium import webdriver
from dateutil.parser import parse
from datetime import datetime as dt
from colorama import Fore, Style, init
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
init(convert=True)

m = re.compile(
    r'https?:\/\/([a-zA-z]*?\.?)facebook\.com\/(profile\.php\?id=(?P<id>\d*)|(?P<userid>[a-zA-z0-9\._]*))')

p = re.compile(r'.*((fbid=)|(hash=)|(posts\/)|(videos\/))(?P<id>\d*)')

def get_numaric_id(url):
    num_id = re.findall(r'user\.php\?id=([0-9]*)',url)
    if num_id:
        return num_id[0]
    else:
        return None

def id_from_url(link):
    """
        extracts the username/id for a facebook url
    """
    try:
        for name, value in m.match(link).groupdict().items():
            if name == 'id' and value is not None:
                return value
            if name == 'userid' and value is not None:
                return value
        return None
    except:
        return None

def get_fb_broswer(USERNAME, PASSWORD, PROFILE_NUM, log=print):
    BROWSER_PATH_BASIC = os.environ.get('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\'
    PROFILE_NUM = "Profile 12"
    BROWSER_PATH = BROWSER_PATH_BASIC + PROFILE_NUM
    import pdb; pdb.set_trace()
    browser_argument = "user-data-dir=" + BROWSER_PATH
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(browser_argument)
    # chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='C://chromedriver.exe')
    time.sleep(7)
    driver.maximize_window()
    driver.get("https://www.facebook.com")
    time.sleep(3)
    log("facebook id is:        " + USERNAME)
    log("facebook pass is:        " + PASSWORD)
    login_status = True
    try:
        try:
            check = driver.find_element_by_css_selector('div.linkWrap.noCount')
            if check:
                print('Driver Logged in!')
                return driver
        except:
            try:
                check = driver.find_element_by_css_selector('div.ow4ym5g4')
                if check:
                    print('Driver Logged in!')
                    return driver
            except:
                pass

        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email")))
        email_field.clear()
        email_field.send_keys(USERNAME)
        pass_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pass")))
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        pass_field.send_keys(Keys.ENTER)
        log("loging in")
        login_status=False
        sleep(5)
    except Exception as ex:
        print (ex)
        log( "logged in already")
    # login layout 2
    if login_status:
        try:
            try:
                check = driver.find_element_by_css_selector('div.linkWrap.noCount')
                if check:
                    print('Driver Logged in!')
                    return driver
            except:
                pass
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email")))
            email_field.clear()
            email_field.send_keys(USERNAME)
            pass_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "pass")))
            pass_field.clear()
            pass_field.send_keys(PASSWORD)
            pass_field.send_keys(Keys.ENTER)
            log("loging in")
            login_status=False
            sleep(5)
        except Exception as ex:
            print (ex)
            log( "logged in already")
    return driver

def link_cleaner(link):
    """
        cleans a facebook link ie remove trailing query values and paths
    """
    return m.match(link).group(0)


def dtsg_grabber(driver):
    try:
        pg_source = driver.page_source
        # fb_dtsg = re.findall(r'\"name\":\"fb_dtsg\",\"value\":\"[0-9A-Za-z-_:]*', pg_source)[0].replace('"name":"fb_dtsg","value":"','')
        fb_dtsg = re.findall(r'{\"token\":\"[0-9A-Za-z-_:]*', pg_source)[0].replace('{"token":"','')
    except:
        fb_dtsg = ''

    return fb_dtsg

def get_session(driver, log=print):
    my_cookies = driver.get_cookies()
    session = requests.Session()
    headers = {
                'authority': 'www.facebook.com',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': '*/*',
                'origin': 'https://www.facebook.com',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': '',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
    session.headers.update(headers)
    try:
        for x in my_cookies:
            if x['name']=='c_user':
                user_id = x['value']
                log("User ID grabbed Successfully: "+ str(user_id))

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

        log(f"{Fore.LIGHTGREEN_EX}----- Session Created Successfully -----")
        log(f"{Fore.LIGHTGREEN_EX}User numaric ID  :: {user_id}")
    except Exception as ex:
        log(f"{Fore.RED}ISSUE in logging in SESSION!   " + ex)

    return session, user_id

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

