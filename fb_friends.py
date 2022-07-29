import queue
import requests
import threading
import urllib.parse
from colorama import Fore, Style, init
import json
import re
from datetime import datetime as dt
from time import sleep
import base64
import random

######### Random user agent###############
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
software_names = [SoftwareName.ANDROID.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)
user_agents = user_agent_rotator.get_user_agents()


############################################################### GRABBING FRIENDS ################################################
def friends_grabber(session, target_id, fb_dtsg, user_id, log=print,FRIENDS_DOC_ID='',HOVER_DOC_ID=''):
    friends_privacy = ''
    all_friends = []
    friends_threads = []
    neo_threads = []
    city_node = []
    work_node = []
    education_node = []
    city_node2 = []
    work_node2 = []
    education_node2 = []

    all_friends_ids_set = set()
    len_all_friends_pre = 0
    url = 'https://www.facebook.com/' + target_id + '/friends'

    headers = {
        'authority': 'www.facebook.com',
        'user-agent': user_agent_rotator.get_random_user_agent(),
        'viewport-width': '1024',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'origin': 'https://www.facebook.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': url,
        'accept-language': 'en-US,en;q=0.9,ur;q=0.8',
    }

    # PROXIES_ARRAYS = config_data.get('PROXIES')

    category_token = '2356318349'
    app_collection_token = 'app_collection:' + target_id + ':' + category_token + ':' + '2'
    app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()

    variables = '{"count":8,"scale":1,"id":"' + app_collection_token_encoded + '"}'

    data = {
    '__user': user_id,
    '__a': '1',
    'fb_dtsg': fb_dtsg,
    'fb_api_caller_class': 'RelayModern',
    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
    'variables': variables,
    'server_timestamps': 'true',
    'doc_id': FRIENDS_DOC_ID
    }
    print("debugging friends data")
    response = session.post('https://www.facebook.com/api/graphql/', headers=headers, data=data)
    if response.status_code != 200:
        log('** Request Issue **')
    else:
        ress = response.json()
        if ress.get('data'):
            data = ress['data']['node']['pageItems']
            edges = data.get('edges')
            for edge in edges:
                node_id = edge['node']['node'].get('id')
                friend_name = edge['node']['title'].get('text')
                friend_pic = 'https://graph.facebook.com/' + node_id + '/picture?width=600'
                friend_profile = 'https://www.facebook.com/' + node_id
                friend_node = {'id':node_id, 'name':friend_name, 'picture':friend_pic, 'profile_link':friend_profile}

                if node_id not in all_friends_ids_set:
                    all_friends.append(friend_node)
                    all_friends_ids_set.add(node_id)

            print("getting more friends by scrolling page")
            end_cursor = data['page_info'].get('end_cursor')
            has_next_page = data['page_info'].get('has_next_page')
            check = 0
            while check < 3:
                try:
                    if len(all_friends) == len_all_friends_pre:
                        check = check + 1
                    len_all_friends_pre = len(all_friends)
                    log('--------- Total Friends until Now  ::  ' + str(len(all_friends)) + ' ---------')
                    variables = '{"count":8,"cursor":"' + end_cursor + '","scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'

                    data = {
                    '__user': user_id,
                    '__a': '1',
                    'fb_dtsg': fb_dtsg,
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': FRIENDS_DOC_ID
                    }
                    random_sleep = random.randint(0,4)
                    sleep(random_sleep)
                    response = session.post('https://www.facebook.com/api/graphql/', headers=headers, data=data)
                    if response.status_code != 200:
                        log('** Request Issue **')
                    else:
                        ress = response.json()
                        if ress.get('data'):
                            data = ress['data']['node']['pageItems']
                            edges = data.get('edges')
                            for edge in edges:
                                node_id = edge['node']['node'].get('id')
                                friend_name = edge['node']['title'].get('text')
                                friend_pic = 'https://graph.facebook.com/' + node_id + '/picture?width=600'
                                friend_name = edge['node']['title'].get('text')
                                friend_profile = 'https://www.facebook.com/' + node_id
                                friend_node = {'id':node_id, 'name':friend_name, 'picture':friend_pic, 'profile_link':friend_profile}

                                if node_id not in all_friends_ids_set:
                                    all_friends.append(friend_node)
                                    all_friends_ids_set.add(node_id)
                            end_cursor = data['page_info'].get('end_cursor')
                            has_next_page = data['page_info'].get('has_next_page')
                        else:
                            log("**** Error Response Loop *****")
                            log(ress)
                except:
                    #break
                    continue
        else:
            log("**** Error Response Main *****")
            log(ress)

    log('*** Friends Grabbed Successfully ***\n')




    final_friends_list = [{'id':d['id'], 'numaric_id':d['id'], 'name':d['name'], 'profile':'https://www.facebook.com/'+d['id'], 'picture_link': 'https://graph.facebook.com/v1.0/'+d['id']+'/picture?width=600', 'city':'::'.join(city_node), 'edu' : '::'.join(education_node), 'work' : '::'.join(work_node), 'cityn' : city_node2, 'edun' : education_node2, 'workn' : work_node2} for d in all_friends]

    log(Fore.LIGHTYELLOW_EX + '--------------------------------')
    log(Fore.LIGHTGREEN_EX + 'Total Friends Grabbed  :::  ' + str(len(final_friends_list)))
    log(Fore.LIGHTYELLOW_EX + '--------------------------------')

    if final_friends_list:
        friends_privacy = 'public'
    else:
        friends_privacy = 'private'
    log(Fore.LIGHTMAGENTA_EX + 'Friends Privacy Status  :::  ' + friends_privacy)

    log(Fore.LIGHTGREEN_EX + 'friends final data list  :::  ')
    print(final_friends_list)
    return final_friends_list

