from traceback import print_tb
from fb_about import tokens_grabber,about_data_f
from fb_friends import friends_grabber
from datetime import datetime as dt
from colorama import Fore, Style, init
import numpy as np
import time
delays = [7, 4, 6, 2, 10, 19]
delay = np.random.choice(delays)
time.sleep(delay)
init(convert=True)
import random
import base64
import bs4
import re
from bs4 import BeautifulSoup
import pika
import json
import pickle
import requests
from fb_utils import *
from time import sleep
log = print

###########Facebook Doc IDs################
HOVER_DOC_ID= "3345023045577128"
ABOUT_DOC_ID= "3563206513758935"
FRIENDS_DOC_ID: "3823952151004784"
BROWSER_PROFILE = "Profile 2"
#link from app

email = "amanzahid291@gmail.com"
pswrd = "Nomi#Smart123"


def get_fb_info(email,pswrd):
    BROWSER_PROFILE = "Profile 2"
    driver = get_fb_broswer(email, pswrd, BROWSER_PROFILE)
    fb_dtsg = ''
    retries = 0
    while not fb_dtsg and retries<3:
        fb_dtsg = dtsg_grabber(driver)
        if fb_dtsg:
            print(Fore.LIGHTBLUE_EX + 'FB_Dtsg Grabbed Successfully ::  ' + fb_dtsg)
        else:
            fb_dtsg = ""
    session, logged_in_user_id = get_session(driver)

    return driver, session, logged_in_user_id, fb_dtsg




def return_fb_data(username,pswrd,link):
    # link = "https://www.facebook.com/profile.php?id=10002730048864722"
    import pdb; pdb.set_trace()
    link = link_cleaner(link)
    fb_driver, fb_session, logged_in_user_id, fb_dtsg = get_fb_info(username,pswrd)
    fb_driver.quit()
    about_params = tokens_grabber(profile_link=link, session=fb_session)
    about_params['fb_dtsg'] = fb_dtsg
    about_params['user_id'] = logged_in_user_id
    profile_id = id_from_url(link)

    about_data = []
    try:
        import pdb; pdb.set_trace()
        numeric_id, about_data = about_data_f(fb_session, profile_id, log, link, ABOUT_DOC_ID,about_params=about_params)
        friends_data = friends_grabber(fb_session,numeric_id, fb_dtsg, logged_in_user_id,log,FRIENDS_DOC_ID,HOVER_DOC_ID)

        all_friends_list = friends_data
        print("about data grabbed successfully",about_data)
        print("writing data into json file")
        json_object = json.dumps(about_data, indent=4)
        json_object2 = json.dumps(friends_data, indent=4)
        with open("fb_about.json", "w") as outfile:
            outfile.write(json_object)
        with open("fb_friends.json", "w") as outfile:
            outfile.write(json_object)
        if all_friends_list !=[]:
            return about_data, all_friends_list
        else:
            all_friends_list = []
            return about_data, all_friends_list

    except:
        about_data = []
        all_friends_list =[]
        return about_data, all_friends_list



