from insta_utils import *
import json
from insta_about import *
import pika
import sys
import threading

from colorama import Fore, Style, init
import requests


# **********************************************************************
def instagram_main(USERNAME, PASSWORD, target_link):
    import pdb; pdb.set_trace()
    target_id = input_checker(target_link)
    BROWSER_PROFILE = 'profile 28'
    username=target_id
    print("getting basic about data....")
    ## Creating session for grabbing data ################
    session = get_session(USERNAME, PASSWORD,BROWSER_PROFILE)
    log(Fore.LIGHTGREEN_EX + "Session createde successfully....")

    basic_info, profile_id = get_basic_info(username , session)
    print("basic about data grabbed succcessfully....")
    print("writing in local file....")
    # print("basic_info data:::", basic_info)

    json_object2 = json.dumps({"insta_user_data":basic_info}, indent=4)
    with open("insta_user_data.json", "w") as outfile:
        outfile.write(json_object2)
    # import pdb;pdb.set_trace()
    return basic_info


# #inputs from app
# link = 'https://www.instagram.com/umair.uy/'
# USERNAME = "nomismart460@gmail.com"
# PASSWORD = "Nomi#Smart123"

# basic_info = instagram_main(USERNAME, PASSWORD, link)

# #reading data from loca file
# Opening JSON file
# f = open('insta_data.json')
# data = json.load(f)
# fileds = data['insta_data'].keys()