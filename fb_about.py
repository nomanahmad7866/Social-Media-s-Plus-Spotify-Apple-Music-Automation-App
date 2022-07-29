import re
import json
import base64
import requests
from time import sleep
from fb_utils import is_date
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from datetime import datetime as dt
init(convert=True)
import urllib
import urllib.parse
import random


################# Creating random user agent to dutch facebook ###############
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
software_names = [SoftwareName.ANDROID.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1000)

#Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()
notify_headers = {'Content-type': 'application/json'}
sleep_array = [2,4,3,5,6]


def hover_about_sections(session, section, about_params={}, about_data={}):

    numeric_id = about_params.get('numeric_id')
    collection_token = section.get('id')

    random_sleep = random.randint(0,5)
    sleep(random_sleep)

    headers = {
        'Connection': 'keep-alive',
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Origin': 'https://www.facebook.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.facebook.com',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    if collection_token:
        section_token = about_params.get('section_token', '')
        decoded_token = base64.b64decode(collection_token).decode()

        raw_token_arr = decoded_token.split(':')
        raw_token = raw_token_arr[1] + ':' + raw_token_arr[2]
        app_section_token = 'ProfileCometAppSectionFeed_timeline_nav_app_sections__' + raw_token

    if section.get('name').lower() == 'work and education':
        print(Fore.GREEN + " ********* Getting Work and Education **********")
        all_works_headlines = []
        all_edu_headlines = []
        all_works_list = []
        all_edu_list = []
        try:
            body = {
            '__user': about_params.get('user_id'),
            '__a': '1',
            '__comet_req':'1',
            'fb_dtsg': about_params.get('fb_dtsg'),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
            'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
            'server_timestamps': 'true',
            'doc_id': '3563206513758935'
            }

            response = session.post('https://www.facebook.com/api/graphql/', headers=headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while grabbing Tokens ***')
            else:
                data = response.text
                data = data.split('\r')
                required_data = [dt for dt in data if '"title":{"text":"Work"}'.lower() in dt.lower()][0]
                if required_data:
                    required_data = required_data.strip()
                    data_json = json.loads(required_data)
                    work_edu_sections = data_json['data']['activeCollections']['nodes'][0].get('style_renderer').get('profile_field_sections')

                    for work_edu_section in work_edu_sections:
                        if work_edu_section.get('field_section_type') == 'work':
                            works_list = work_edu_section['profile_fields'].get('nodes')
                            if works_list:
                                all_works_headlines = [work['title'].get('text', '') for work in works_list]
                                for work in works_list:
                                    designation = ''
                                    company_name = ''
                                    work_tenure = ''
                                    work_description = ''
                                    work_location = ''
                                    work_headline = work['title'].get('text', '')
                                    work_arr = work_headline.split(' at ')
                                    if len(work_arr) > 1:
                                        designation = work_arr[0]
                                        company_name = work_arr[1]

                                    main_list_items = work.get('list_item_groups',[])
                                    all_list_items = []
                                    if main_list_items:
                                        for ww in main_list_items:
                                            items_to_add = ww['list_items']
                                            all_list_items.extend(items_to_add)
                                        low_counter = 0
                                        med_counter = 0
                                        for single_item in all_list_items:
                                            if single_item.get('heading_type') == 'LOW':
                                                low_counter = low_counter + 1
                                            elif single_item.get('heading_type') == 'MEDIUM':
                                                med_counter = med_counter + 1

                                        if len(all_list_items) == 1:
                                            if low_counter == 1:
                                                str_is_date = is_date(all_list_items[0]['text'].get('text').split(' - ')[0])
                                                if str_is_date:
                                                    work_tenure = all_list_items[0]['text'].get('text')
                                                else:
                                                    work_location = all_list_items[0]['text'].get('text')
                                            if med_counter == 1:
                                                work_description = all_list_items[0]['text'].get('text')

                                        elif len(all_list_items) == 2:
                                            if low_counter == 1:
                                                str_is_date = is_date(all_list_items[0]['text'].get('text').split(' - ')[0])
                                                if str_is_date:
                                                    work_tenure = all_list_items[0]['text'].get('text')
                                                else:
                                                    work_location = all_list_items[0]['text'].get('text')

                                            elif low_counter == 2:
                                                str_is_date = is_date(all_list_items[0]['text'].get('text').split(' - ')[0])
                                                if str_is_date:
                                                    work_tenure = all_list_items[0]['text'].get('text')
                                                    work_location = all_list_items[1]['text'].get('text')
                                                else:
                                                    work_location = all_list_items[0]['text'].get('text')
                                                    work_tenure = all_list_items[1]['text'].get('text')

                                            if med_counter == 1:
                                                work_description = all_list_items[1]['text'].get('text')

                                        elif len(all_list_items) == 3:
                                            if low_counter == 1:
                                                str_is_date = is_date(all_list_items[0]['text'].get('text').split(' - ')[0])
                                                if str_is_date:
                                                    work_tenure = all_list_items[0]['text'].get('text')
                                                else:
                                                    work_location = all_list_items[0]['text'].get('text')

                                            if low_counter == 2:
                                                str_is_date = is_date(all_list_items[0]['text'].get('text').split(' - ')[0])
                                                if str_is_date:
                                                    work_tenure = all_list_items[0]['text'].get('text')
                                                    work_location = all_list_items[1]['text'].get('text')
                                                else:
                                                    work_location = all_list_items[0]['text'].get('text')
                                                    work_tenure = all_list_items[1]['text'].get('text')

                                            if med_counter == 1:
                                                work_description = all_list_items[2]['text'].get('text')

                                    work_data = {
                                                'designation' : designation,
                                                'company_name' : company_name,
                                                'work_tenure' : work_tenure,
                                                'work_description' : work_description,
                                                'work_location' : work_location,
                                                'work_headline' : work_headline
                                                }

                                    all_works_list.append(work_data)
                        ####################################  WORKS LIST FINISHED HERE  ####################################


                        elif 'college' in work_edu_section.get('field_section_type') or 'school' in work_edu_section.get('field_section_type') or 'university' in work_edu_section.get('field_section_type'):
                            edu_list = work_edu_section['profile_fields'].get('nodes')
                            if edu_list:
                                [all_edu_headlines.append(edu['title'].get('text', '')) for edu in edu_list]
                                for edu in edu_list:
                                    degree_program = ''
                                    institute_name = ''
                                    study_tenure = ''
                                    study_description = ''
                                    study_headline = edu['title'].get('text', '')
                                    study_arr = study_headline.split(' at ')
                                    if len(study_arr) > 1:
                                        pass
                                    else:
                                        study_arr = study_headline.split(' to ')
                                    if len(study_arr) > 1:
                                        degree_program = study_arr[0].replace('Studies ','').replace('Studied ','').replace('Went ','').replace('Studies','').replace('Studied','').replace('Went','')
                                        institute_name = study_arr[1]

                                    main_list_items = edu.get('list_item_groups',[])
                                    all_list_items = []
                                    if main_list_items:
                                        for ww in main_list_items:
                                            items_to_add = ww['list_items']
                                            all_list_items.extend(items_to_add)

                                        for single_item in all_list_items:
                                            if single_item.get('heading_type') == 'LOW':
                                                study_tenure = single_item['text'].get('text')
                                            elif single_item.get('heading_type') == 'MEDIUM':
                                                ranges_check = single_item['text'].get('ranges')
                                                if not ranges_check:
                                                    study_description = single_item['text'].get('text')

                                    edu_data = {
                                                'degree_program' : degree_program,
                                                'institute_name' : institute_name,
                                                'study_tenure' : study_tenure,
                                                'study_description' : study_description,
                                                'study_headline' : study_headline
                                                }

                                    all_edu_list.append(edu_data)
                        ####################################  EDUCATION LIST FINISHED HERE  ####################################
        except Exception as en:
            print(Fore.LIGHTRED_EX  + " ********* Exception in Work and Education **********")
            print(str(en))
            pass

        about_data['all_works_headlines'] = all_works_headlines
        about_data['all_edu_headlines'] = all_edu_headlines
        about_data['all_works_list'] = all_works_list
        about_data['all_edu_list'] = all_edu_list


    elif section.get('name').lower() == 'places lived':
        all_location = []
        print(Fore.GREEN  + " ********* Getting Places Lived **********")
        body = {
        '__user': about_params.get('user_id'),
        '__a': '1',
        '__comet_req':'1',
        'fb_dtsg': about_params.get('fb_dtsg'),
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
        'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
        'server_timestamps': 'true',
        'doc_id': '3563206513758935'
        }
        try:
            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while Getting Places Lived ***')
            else:
                data = response.text
                data = data.split('\r')
                # required_data = [dt for dt in data if '"title":{"text":"Places lived"}' in dt][0]
                try:
                    required_data = [dt for dt in data if '"title":{"text":"Places Lived"}'.lower() in dt.lower()][0]
                    if required_data:
                        required_data = required_data.strip()
                        data_json = json.loads(required_data)
                        all_locations = data_json['data']['activeCollections']['nodes'][0].get('style_renderer').get('profile_field_sections')[0]['profile_fields'].get('nodes',[])

                        for location in all_locations:
                            city_name = location['title'].get('text', '')
                            location_type = location['field_type']
                            all_location.append({'name': city_name, 'type': location_type})
                except Exception as el:
                    print(" ************************************ ")
                    print(" Exception in places lived ::::  ", str(el))
                    print(" ************************************ ")
                    pass
        except Exception as ep:
            print(" ********* Exception in Places Lived **********")
            print(str(ep))
            pass

        about_data['location'] = all_location


    elif section.get('name').lower() == 'contact and basic info':
        all_social_links = []
        all_contact_list = {}
        print(Fore.GREEN + " ********* Getting Contact and basic info **********")
        gender = ''
        lanuguages = ''
        interested_in = ''
        try:
            body = {
            '__user': about_params.get('user_id'),
            '__a': '1',
            '__comet_req':'1',
            'fb_dtsg': about_params.get('fb_dtsg'),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
            'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
            'server_timestamps': 'true',
            'doc_id': '3563206513758935'
            }

            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while Getting Contact and basic info ***')
            else:
                data = response.text
                data = data.split('\r')
                try:
                    required_data = [dt for dt in data if '"title":{"text":"Contact Info"}'.lower() in dt.lower()][0]
                except Exception as ess:
                    required_data = ''
                    pass

                if required_data:
                    required_data = required_data.strip()
                    data_json = json.loads(required_data)
                    all_contact_sections = data_json['data']['activeCollections']['nodes'][0].get('style_renderer').get('profile_field_sections')
                    for contact_section in all_contact_sections:
                        if contact_section.get('field_section_type') == 'websites_and_social_links':
                            social_links_list = contact_section['profile_fields'].get('nodes')
                            if social_links_list:
                                for social_link_dict in social_links_list:
                                    if social_link_dict.get('field_type') == 'null_state':
                                        continue
                                    username = social_link_dict['title'].get('text','')
                                    platform = social_link_dict['list_item_groups'][0]['list_items'][0]['text'].get('text','')

                                    social_data = {
                                                    'username' : username,
                                                    'platform' : platform
                                                    }
                                    all_social_links.append(social_data)

                        elif contact_section.get('field_section_type') == 'about_contact_info':
                            contacts_links_list = contact_section['profile_fields'].get('nodes')
                            if contacts_links_list:
                                for contact_link_dict in contacts_links_list:
                                    if contact_link_dict.get('field_type') == 'null_state':
                                        continue

                                    contact_data = contact_link_dict['title'].get('text','')
                                    contact_data = contact_data.replace(" ","").strip()
                                    if contact_data.isdigit():
                                        contactnum = contact_data
                                        all_contact_list['contact_num'] = contactnum
                                    if '@' in contact_data:
                                        email = contact_data
                                        all_contact_list['email'] = email

                        ####################################### Social Links Done #######################################

                        elif contact_section.get('field_section_type') == 'basic_info':
                            basic_info_list = contact_section['profile_fields'].get('nodes')
                            for basic_info in basic_info_list:
                                if basic_info.get('field_type') == 'null_state':
                                        continue
                                if basic_info.get('field_type') == 'gender':
                                    gender = basic_info['title'].get('text')

                                elif basic_info.get('field_type') == 'languages':
                                    lanuguages = basic_info['title'].get('text')

                                elif basic_info.get('field_type') == 'interested_in':
                                    interested_in = basic_info['title'].get('text')
                                ############### Basic Info DONE ###############

        except Exception as ec:
            print(" ********* Exception in Contact and basic info **********")
            print(str(ec))
            pass

        about_data['gender'] = gender
        about_data['lanuguages'] = lanuguages
        about_data['interested_in'] = interested_in
        about_data['social_links'] = all_social_links
        about_data['contact'] = all_contact_list


    elif section.get('name').lower() == 'family and relationships':
        relationship = ''
        print(Fore.GREEN +" ********* Getting family and Relationships **********")
        family_members = []
        body = {
        '__user': about_params.get('user_id'),
        '__a': '1',
        '__comet_req':'1',
        'fb_dtsg': about_params.get('fb_dtsg'),
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
        'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
        'server_timestamps': 'true',
        'doc_id': '3563206513758935'
        }

        try:
            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while grabbing family and Relationships Req ***')
            else:
                data = response.text
                data = data.split('\r')
                required_data = [dt for dt in data if '"title":{"text":"Relationship"}'.lower() in dt.lower()][0]
                if required_data:
                    required_data = required_data.strip()
                    data_json = json.loads(required_data)
                    all_family_relation_sections = data_json['data']['activeCollections']['nodes'][0].get('style_renderer').get('profile_field_sections')
                    for family_relation_section in all_family_relation_sections:
                        if family_relation_section.get('field_section_type') == 'relationship':
                            relationship_list = family_relation_section['profile_fields'].get('nodes')
                            if relationship_list[0].get('field_type') == 'relationship':
                                relationship = relationship_list[0]['renderer']['field']['text_content'].get('text')

                        ############### Relationship Status DONE ###############

                        elif family_relation_section.get('field_section_type') == 'family':
                            family_members_list = family_relation_section['profile_fields'].get('nodes')
                            fb_basic_url = 'https://www.facebook.com/'
                            for single_family_member in family_members_list:
                                family_member_name = ''
                                family_member_numeric_id = ''
                                family_member_profile_link = ''
                                family_member_picture_link = ''
                                family_member_relation_type = ''

                                null_check = single_family_member['field_type']
                                if null_check == 'null_state':
                                    continue
                                family_member_name = single_family_member['title'].get('text','')
                                profile_check = single_family_member['title'].get('ranges',[])
                                if profile_check:
                                    family_member_numeric_id = profile_check[0]['entity'].get('id','')
                                if family_member_numeric_id:
                                    family_member_profile_link = fb_basic_url + family_member_numeric_id
                                    family_member_picture_link = 'https://graph.facebook.com/' + family_member_numeric_id + '/picture?width=600'

                                family_member_relation_type = single_family_member['list_item_groups'][0]['list_items'][0]['text'].get('text','')
                                family_member_data = {
                                                        'name' : family_member_name,
                                                        'numeric_id' : family_member_numeric_id,
                                                        'profile_link' : family_member_profile_link,
                                                        'picture_link' : family_member_picture_link,
                                                        'relation_type' : family_member_relation_type
                                                    }

                                family_members.append(family_member_data)

        except Exception as ef:
            print(Fore.LIGHTRED_EX + " ********* Exception in family and Relationships **********")
            print(str(ef))
            pass

        about_data['relationship'] = relationship
        about_data['family_members'] = family_members

    elif 'details about' in section.get('name').lower():
        print(Fore.GREEN +" ********* Getting Details About **********")
        about_me = ''
        nickname = ''
        favourite_quote = ''
        try:
            body = {
            '__user': about_params.get('user_id'),
            '__a': '1',
            '__comet_req':'1',
            'fb_dtsg': about_params.get('fb_dtsg'),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
            'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
            'server_timestamps': 'true',
            'doc_id': '3563206513758935'
            }
            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while grabbing Details About ***')
            else:
                data = response.text
                data = data.split('\r')
                required_data = [dt for dt in data if '"title":{"text":"About '.lower() in dt.lower()][0]
                if required_data:
                    required_data = required_data.strip()
                    data_json = json.loads(required_data)
                    all_details_sections = data_json['data']['activeCollections']['nodes'][0].get('style_renderer').get('profile_field_sections')
                    for details_section in all_details_sections:
                        if details_section.get('field_section_type') == 'about_me':
                            about_me_list = details_section['profile_fields'].get('nodes')
                            if about_me_list[0].get('field_type') == 'about_me':
                                about_me = about_me_list[0]['renderer']['field']['text_content'].get('text')
                        ############### About Me Text DONE ###############


                        elif details_section.get('field_section_type') == 'nicknames':
                            nicknames_list = details_section['profile_fields'].get('nodes')
                            if nicknames_list[0].get('field_type') == 'nicknames':
                                nickname = nicknames_list[0]['title'].get('text')
                        ############### Nick Name DONE ###############


                        elif details_section.get('field_section_type') == 'favorite_quotes':
                            favourite_quotes_list = details_section['profile_fields'].get('nodes')
                            if favourite_quotes_list[0].get('field_type') == 'quotes':
                                favourite_quote = favourite_quotes_list[0]['renderer']['field']['text_content'].get('text')
                        ############### Favourite Quotes DONE ###############
        except Exception as ed:
            print(Fore.RED + " ********* Exception in Getting Details About **********")
            print(str(ed))
            pass

        about_data['about_me'] = about_me
        about_data['nickname'] = nickname
        about_data['favourite_quote'] = favourite_quote


    elif section.get('name').lower() == 'life events':
        print(Fore.GREEN +" ********* Getting Life Events **********")
        life_events = []
        body = {
        '__user': about_params.get('user_id'),
        '__a': '1',
        '__comet_req':'1',
        'fb_dtsg': about_params.get('fb_dtsg'),
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
        'variables': '{"appSectionFeedKey":"' + app_section_token + '","collectionToken":"' + collection_token + '","rawSectionToken":"' + raw_token + '","scale":1,"sectionToken":"' + section_token + '","useDefaultActor":true,"userID":"' + numeric_id + '"}',
        'server_timestamps': 'true',
        'doc_id': '3563206513758935'
        }
        try:
            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '*** Issue while Getting Life Events ***')
            else:
                data = response.text
                data = data.split('\r')
                required_data = [dt for dt in data if ',"year_overview":' in dt.lower()][0]
                if required_data:
                    required_data = required_data.strip()
                    data_json = json.loads(required_data)
                    all_life_events_list = data_json['data']['activeCollections']['nodes'][0].get('style_renderer')['user'].get('timeline_sections').get('nodes', [])
                    for single_life_event in all_life_events_list:
                        year = single_life_event.get('year')
                        life_events_list = []
                        if year:
                            year_overview_nodes = single_life_event['year_overview']['items'].get('nodes', [])
                            if year_overview_nodes:
                                for single_overview_node in year_overview_nodes:
                                    life_event_text = single_overview_node['title'].get('text','')
                                    life_event_url = single_overview_node.get('url','')
                                    life_events_list.append({'life_event_text': life_event_text, 'life_event_url': life_event_url})
                            if life_events_list:
                                life_events.append({'year': year, 'life_events' : life_events_list})

        except Exception as el:
            print(Fore.LIGHTRED_EX + '*** Exception while Getting Life Events ***')
            print(str(el))
            pass


        about_data['life_events'] = life_events


    elif section.get('name') == 'likes':
        all_likes = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '96'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)

            final_likes = []
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Likes **  Request ----------')
                about_data['likesjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['likesjson'] = []
                    return
                else:
                    all_likes.extend(nodes)

                    while end_cursor and len(all_likes) <= 100:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Likes until now  ::  ' + str(len(all_likes)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Likes **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_likes.extend(nodes)

                print('Total Likes Grabbed   :::   ' + str(len(all_likes)))
                sleep(2)
                for dd in all_likes:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_likes.append(final_data)
        except Exception as el:
            print(Fore.LIGHTRED_EX + '---------- Exception in  ** Likes **  Request ----------')
            print(Fore.RED + " " + str(el))
            pass

        about_data['likesjson'] = final_likes
    elif section.get('name') == 'movies':
        all_movies = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '106'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Movies **  Request ----------')
                about_data['moviesjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['moviesjson'] = []
                    return
                else:
                    all_movies.extend(nodes)

                    while end_cursor and len(all_movies) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Movies until now  ::  ' + str(len(all_movies)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Videos **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_movies.extend(nodes)

                print('Total Movies Grabbed   :::   ' + str(len(all_movies)))
                final_movies = []
                for dd in all_movies:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_movies.append(final_data)
        except Exception as em:
            print(Fore.LIGHTRED_EX + '---------- Exception in  ** Movies **  Request ----------')
            print(Fore.RED + " " + str(em))
            pass

        about_data['moviesjson'] = final_movies


    elif section.get('name') == 'television':
        all_tv_shows = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '107'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/', headers = headers,  data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** TV_Shows **  Request ----------')
                about_data['televisionjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['televisionjson'] = []
                    return
                else:
                    all_tv_shows.extend(nodes)

                    while end_cursor and len(all_tv_shows) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'TV_Shows until now  ::  ' + str(len(all_tv_shows)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** TV_Shows **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_tv_shows.extend(nodes)

                print('Total TV_Shows Grabbed   :::   ' + str(len(all_tv_shows)))
                final_television = []
                for dd in all_tv_shows:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_television.append(final_data)
        except Exception as et:
            print(Fore.LIGHTRED_EX + '---------- Exception in  ** TV_Shows **  Request ----------')
            print(str(et))
            pass

        about_data['televisionjson'] = final_television


    elif section.get('name') == 'artists':
        all_artists = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '109'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Music/Artists **  Request ----------')
                about_data['musicjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['musicjson'] = []
                    return
                else:
                    all_artists.extend(nodes)
                    while end_cursor and len(all_artists) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Music/Artists until now  ::  ' + str(len(all_artists)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/', data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Music/Artists **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_artists.extend(nodes)
                print('Total Music/Artists Grabbed   :::   ' + str(len(all_artists)))
                final_music = []
                for dd in all_artists:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_music.append(final_data)
        except Exception as em:
            print(Fore.LIGHTRED_EX + '---------- Exception in  ** Music/Artists **  Request ----------')
            print(str(em))
            pass
        about_data['musicjson'] = final_music

    elif section.get('name') == 'books':
        all_books = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '108'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Books **  Request ----------')
                about_data['booksjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['booksjson'] = []
                    return
                else:
                    all_books.extend(nodes)

                    while end_cursor and len(all_books) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Books until now  ::  ' + str(len(all_books)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/', headers = headers,data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Books **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_books.extend(nodes)

                print('Total Books Grabbed   :::   ' + str(len(all_books)))
                final_books = []
                for dd in all_books:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_books.append(final_data)
        except Exception in ell:
            print(Fore.LIGHTRED_EX + '---------- Exception in ** Books **  Request ----------')
            print(str(ell))
            pass

        about_data['booksjson'] = final_books


    elif section.get('name') == 'teams':
        all_teams = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '110'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }
            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Favorite Teams **  Request ----------')
                about_data['favoriteteamsjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['favoriteteamsjson'] = []
                    return
                else:
                    all_teams.extend(nodes)

                    while end_cursor and len(all_teams) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Favorite Teams until now  ::  ' + str(len(all_teams)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Favorite Teams **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_teams.extend(nodes)
                print('Total Favorite Teams Grabbed   :::   ' + str(len(all_teams)))
                final_teams = []
                for dd in all_teams:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_teams.append(final_data)
        except Exception as et:
            print(Fore.LIGHTRED_EX + '---------- Exception in  ** Favorite Teams **  Request ----------')
            print(str(et))
            pass

        about_data['favoriteteamsjson'] = final_teams
    elif section.get('name') == 'athletes':
        all_athletes = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '119'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }
            response = session.post('https://www.facebook.com/api/graphql/', headers = headers,data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Athletes **  Request ----------')
                about_data['favoriteathletesjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['favoriteathletesjson'] = []
                    return
                else:
                    all_athletes.extend(nodes)

                    while end_cursor and len(all_athletes) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Athletes until now  ::  ' + str(len(all_athletes)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }
                        response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Athletes **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_athletes.extend(nodes)

                print('Total Athletes Grabbed   :::   ' + str(len(all_athletes)))
                final_athletes = []
                for dd in all_athletes:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_athletes.append(final_data)
        except Exception as ath:
            print(Fore.LIGHTRED_EX + '---------- Exception while  ** Athletes **  Request ----------')
            print(str(ath))
            pass

        about_data['favoriteathletesjson'] = final_athletes

    elif section.get('name') == 'restaurants':
        all_restaurants = []
        try:
            category_token = '2409997254'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '73'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/', headers = headers,data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Restaurants **  Request ----------')
                about_data['restaurantsjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['restaurantsjson'] = []
                    return
                else:
                    all_restaurants.extend(nodes)

                    while end_cursor and len(all_restaurants) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Restaurants until now  ::  ' + str(len(all_restaurants)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Restaurants **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_restaurants.extend(nodes)

                print('Total Restaurants Grabbed   :::   ' + str(len(all_restaurants)))
                final_restaurants = []
                for dd in all_restaurants:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''
                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'id':pg_id,
                                    'image':image
                                }
                    final_restaurants.append(final_data)
        except Exception as es:
            print(Fore.LIGHTRED_EX + '---------- Exception  while  ** Restaurants **  Request ----------')
            print(str(es))
            pass
        about_data['restaurantsjson'] = final_restaurants


    elif section.get('name') == 'checkins':
        all_checkins = []
        try:
            category_token = '302324425790'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '103'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token

            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()

            variables = '{"count":8,"scale":1,"search":null,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '4751669571524879'
                    }

            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Checkins **  Request ----------')
                about_data['checkinsjson'] = []
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['checkinsjson'] = []
                    return
                else:
                    all_checkins.extend(nodes)

                    while end_cursor and len(all_checkins) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Checkins until now  ::  ' + str(len(all_checkins)))
                        variables = '{"count":8,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '4751669571524879'
                                }

                        response = session.post('https://www.facebook.com/api/graphql/', headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Checkins **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_checkins.extend(nodes)

                print('Total Checkins Grabbed   :::   ' + str(len(all_checkins)))
                final_checkins = []
                for dd in all_checkins:
                    name = dd['node']['title'].get('text','')
                    category = dd['node']['subtitle_text'].get('text','')
                    try:
                        pg_id = dd['node']['node'].get('id','')
                    except:
                        pg_id = ''

                    if pg_id:
                        image = 'https://graph.facebook.com/' + dd['node']['node'].get('id','') + '/picture?width=600'
                    else:
                        image = ''

                    if '\nVisited on ' in category:
                        category_arr = category.split('\nVisited on ')
                        category = category_arr[0]
                        checkin_date = category_arr[1]
                    else:
                        checkin_date = ''

                    final_data = {
                                    'name':name,
                                    'category':category,
                                    'checkin_date':checkin_date,
                                    'id':pg_id,
                                    'image':image
                                }
                    if name:
                        final_checkins.append(final_data)

        except Exception as ec:
            print(Fore.LIGHTRED_EX + '---------- Exception while  ** Checkins **  Request ----------')
            print(str(ec))
            pass
        about_data['checkinsjson'] = final_checkins

    elif section.get('name') == 'cover_photo':
        print(Fore.LIGHTRED_EX + '---------- Grabbing ** Cover Photo/Albums **  Request ----------')
        all_albums = []
        cover_photo = ''
        try:
            category_token = '2305272732'
            app_collection_token = 'app_collection:' + numeric_id + ':' + category_token + ':' + '6'
            app_section_token = 'app_section:' + numeric_id + ':' + category_token
            app_collection_token_encoded = base64.b64encode(app_collection_token.encode()).decode()
            app_section_token_encoded = base64.b64encode(app_section_token.encode()).decode()
            variables = '{"count":100,"scale":1,"id":"' + app_collection_token_encoded + '"}'
            body = {
                    '__user': about_params.get('user_id'),
                    '__a': '1',
                    'fb_dtsg': about_params.get('fb_dtsg'),
                    'fb_api_caller_class': 'RelayModern',
                    'fb_api_req_friendly_name': 'ProfileCometAppCollectionAlbumsRendererPaginationQuery',
                    'variables': variables,
                    'server_timestamps': 'true',
                    'doc_id': '3284835684898263'
                    }
            response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
            if response.status_code != 200:
                print(Fore.LIGHTRED_EX + '---------- Issue while  ** Albums **  Request ----------')
                about_data['cover'] = ''
            else:
                resp = response.json()
                data = resp['data']['node']['pageItems']
                nodes = data.get('edges',[])
                end_cursor = data['page_info'].get('end_cursor','')
                if not nodes:
                    about_data['cover'] = ''
                    return
                else:
                    all_albums.extend(nodes)
                    while end_cursor and len(all_albums) <= 50:
                        random_sleep = random.randint(0,len(sleep_array)-1)
                        sleep(sleep_array[random_sleep])
                        print(Fore.YELLOW + 'Albums until now  ::  ' + str(len(all_albums)))
                        variables = '{"count":100,"scale":1,"cursor":"' + end_cursor + '","search":null,"id":"' + app_collection_token_encoded + '"}'
                        body = {
                                '__user': about_params.get('user_id'),
                                '__a': '1',
                                'fb_dtsg': about_params.get('fb_dtsg'),
                                'fb_api_caller_class': 'RelayModern',
                                'fb_api_req_friendly_name': 'ProfileCometAppCollectionAlbumsRendererPaginationQuery',
                                'variables': variables,
                                'server_timestamps': 'true',
                                'doc_id': '3284835684898263'
                                }
                        response = session.post('https://www.facebook.com/api/graphql/',headers = headers, data=body)
                        if response.status_code != 200:
                            print(Fore.LIGHTRED_EX + '---------- Issue while  ** Albums **  Request ----------')
                        else:
                            resp = response.json()
                            data = resp['data']['node']['pageItems']
                            nodes = data.get('edges',[])
                            end_cursor = data['page_info'].get('end_cursor','')
                            if not nodes:
                                break
                            else:
                                all_albums.extend(nodes)
                print('Total Albums Grabbed   :::   ' + str(len(all_albums)))
                final_albums = []
                for dd in all_albums:
                    album_name = dd['node']['title'].get('text','')
                    if album_name.lower() == 'cover photos':
                        cover_photo = dd['node']['image'].get('uri','')
                        break
        except Exception as eab:
            print(Fore.LIGHTRED_EX + '---------- Exception while  ** Albums **  Request ----------')
            print(str(eab))
            pass

        about_data['cover'] = cover_photo

############### hover sections ended #########################

#necessary
def tokens_grabber(profile_link, session=requests, log=print):
    # url = 'https://www.facebook.com/' + profile_id + '/about'
    slug = "/" if not "profile.php?id=" in profile_link else "&sk="
    about_link = profile_link + slug + "about"

    res = session.get(about_link)
    if res.status_code != 200:
        log(Fore.LIGHTRED_EX + '*** Issue while grabbing Tokens ***')
    else:
        try:
            raw_token = re.findall(r'\"rawSectionToken\":\"[0-9]*:[0-9]*', res.text)[0].replace('"rawSectionToken":"','')
            log(Fore.LIGHTGREEN_EX + 'Raw Token Grabbed Successfully  ::  ' + raw_token)
        except:

            log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** Raw Token **  --------')
            raw_token = ''


        try:
            collection_token = re.findall(r'\"collectionToken\":\"[0-9A-Za-z]*..', res.text)[0].replace('"collectionToken":"','').replace('"','').replace(',','')
            log(Fore.LIGHTCYAN_EX + 'Collection Token Grabbed Successfully  ::  ' + collection_token)
        except:
            log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** Collection Token **  --------')
            collection_token = ''

        try:
            section_token = re.findall(r'\"sectionToken\":\"[0-9A-Za-z]*..', res.text)[0].replace('"sectionToken":"','').replace('"','').replace(',','')
            log(Fore.LIGHTMAGENTA_EX + 'Section Token Grabbed Successfully  ::  ' + section_token)
        except:
            log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** Section Token **  --------')
            section_token = ''

        try:
            soup = BeautifulSoup(res.text, 'html.parser')
            target_name = soup.title.text
            log(Fore.LIGHTGREEN_EX + 'Name of Target  ::  ' + target_name)
        except:
            target_name = ''
            log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** Name **  --------')
    if collection_token:
        numeric_id = base64.b64decode(collection_token).decode().split(':')[1]
        log(Fore.YELLOW + 'Numeric ID Grabbed Successfully  ::  ' + numeric_id)
    else:
        try:
            numeric_id = raw_token.split(':')[0]
            if numeric_id == '':
                numeric_id  =  re.findall(r'\"userID\":\"[0-9]*..', res.text)[0].replace('"userID":"','').replace('"','').replace(',','')
                log(Fore.LIGHTGREEN_EX + 'Numeric ID Grabbed Successfully  ::  ' + numeric_id)

        except:
            log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** NUMERIC_ID **  --------')
            numeric_id = ''

    if raw_token:
        app_section_token = 'ProfileCometAppSectionFeed_timeline_nav_app_sections__' + raw_token
        log(Fore.LIGHTBLUE_EX + 'APP Section Token Grabbed Successfully  ::  ' + app_section_token)
    else:
        log(Fore.LIGHTRED_EX + '-------- Issue while Grabbing  ** app_section_token **  --------')
        app_section_token = ''

    log(Fore.WHITE + '\n -------------------------------------------------\n')

    about_params = {
                    'target_name': target_name,
                    'raw_token' : raw_token,
                    'collection_token' : collection_token,
                    'section_token' : section_token,
                    'numeric_id' : numeric_id,
                    'app_section_token' : app_section_token
                    }

    return about_params


def about_data_f(session, profile_id,  log=print, link='', ABOUT_DOC_ID ='',about_params={}):
    sections = []
    ACCESS_TOKEN = ""
    about_data_json = {}
    about_filter_json = ""
    target_id = about_params.get('numeric_id')
    fb_dtsg = about_params.get('fb_dtsg')

    body = {
        '__user': about_params.get('user_id'),
        '__a': '1',
        '__comet_req':'1',
        'fb_dtsg': about_params.get('fb_dtsg'),
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'ProfileCometAboutAppSectionQuery',
        'variables': '{"appSectionFeedKey":"' + about_params.get('app_section_token') + '","collectionToken":"' + about_params.get('collection_token') + '","rawSectionToken":"' + about_params.get('raw_token') + '","scale":1,"sectionToken":"' + about_params.get('section_token') + '","useDefaultActor":true,"userID":"' + about_params.get('numeric_id') + '"}',
        'server_timestamps': 'true',
        'doc_id': ABOUT_DOC_ID
        }

    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Origin': 'https://www.facebook.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.facebook.com',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    response = session.post('https://www.facebook.com/api/graphql/', headers = headers,data=body)
    if response.status_code != 200:
        print(Fore.LIGHTRED_EX + '*** Issue while grabbing Tokens ***')
    else:
        data = response.text
        data = data.split('\r')
        dd = data[0].strip()
        dd = json.loads(dd)
        sections = dd['data']['user']['about_app_sections']['nodes'][0].get('all_collections').get('nodes')
        print(Fore.LIGHTMAGENTA_EX + 'Total Section  ::  ' + str(len(sections)))

    all_threads = []
    if sections:
        extra_sections = [  {'name': 'likes', 'id': '', 'url': ''},
                            {'name': 'movies', 'id': '', 'url': ''},
                            {'name': 'television', 'id': '', 'url': ''},
                            {'name': 'artists', 'id': '', 'url': ''},
                            {'name': 'books', 'id': '', 'url': ''},
                            {'name': 'teams', 'id': '', 'url': ''},
                            {'name': 'athletes', 'id': '', 'url': ''},
                            {'name': 'checkins', 'id': '', 'url': ''},
                            {'name': 'athletessss', 'id': '', 'url': ''},
                            {'name': 'restaurants', 'id': '', 'url': ''}]

        sections.extend(extra_sections)
        random.shuffle(sections)
        for section in sections:
            sleep(2)
            if section.get('name').lower() != 'overview':
                try:
                    hover_about_sections(session, section,about_params, about_data_json)
                except Exception as em:
                    print(" ******************** ")
                    print(" **Exception in hover about section ** ", str(em))
                    print(" ******************** ")
                    #### Notification Profiler
                    log(str(em))

    about_data_json['name'] = about_params.get('target_name','')
    #print("about data ", about_data_json)

    return target_id, about_data_json


