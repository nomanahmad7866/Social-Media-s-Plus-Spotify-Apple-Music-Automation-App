import requests as req
import time
from colorama import Fore, Style, init
init(convert=True)


def get_basic_info(username, session):
    print("Grabbing Basic Info!")
    link = "https://i.instagram.com/api/v1/users/web_profile_info/?username="+username
    cookie= session.cookies.get_dict()
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"100\", \"Google Chrome\";v=\"100\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-asbd-id": "198387",
        "x-csrftoken": cookie.get("csrftoken"),
        "x-ig-app-id": "936619743392459",
        "x-ig-www-claim": "hmac.AR3rFdig5D7MLoQgnfAPLGEPH_5CZz4hzpJPOTLIuUUWX9fx",
        "cookie": "ig_did="+cookie.get("ig_did")+"; mid="+cookie.get("mid")+"; ig_nrcb="+cookie.get("ig_nrcb")+"; ds_user_id="+cookie.get("ds_user_id")+"; csrftoken="+cookie.get("csrftoken")+"; sessionid="+cookie.get("sessionid")+"; shbid="+cookie.get("shbid")+"; shbts="+cookie.get("shbts")+"; datr="+cookie.get("datr")+"; rur="+cookie.get("rur"),
        "Referer": "https://www.instagram.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    if session:
        requests = session
    else:
        requests = req

    count = 0
    data = {}
    while count < 3:
        try:
            result = requests.get(link,headers=headers)
            data = result.json()
            break
        except Exception as ex:
            print('Basic Request Issue!')
            print('Trying Again!')
            count = count + 1
            pass
            time.sleep(2)
            print(ex)

    if data:
        pass
    else:
        print('\n')
        print('----------------------')
        print('Profile Doesnot Exists')
        print('----------------------')
        basic_info = {}
        return False, basic_info

    data = data["data"]["user"]

    profile_id = data.get("id")
    name = data.get("full_name")
    profile_pic = data.get("profile_pic_url_hd", "")
    is_private = data.get("is_private")
    biography = data.get("biography", "")
    followers = data.get("edge_followed_by")["count"]
    followings = data.get("edge_follow")["count"]
    media_count = data.get("edge_owner_to_timeline_media")["count"]
    followed_by_viewer = data.get("followed_by_viewer")
    media_data = data.get("edge_owner_to_timeline_media")["edges"]

    first_hash = data.get("edge_owner_to_timeline_media")["page_info"]["end_cursor"]
    more_posts = data.get("edge_owner_to_timeline_media")["page_info"]["has_next_page"]
    total_posts = data.get("edge_owner_to_timeline_media")["count"]

    p_link = "https://www.instagram.com/" + username

    basic_info = {
        'profile_id': profile_id,
        'screen_name': username,
        'name': name,
        'profile_pic': profile_pic,
        'p_link': p_link,
        'is_private': is_private,
        'biography': biography,
        'followers': followers,
        'followings': followings,
        'media_count': media_count,
        'followed_by_viewer': followed_by_viewer,
        'media_data': media_data,
        'first_hash': first_hash,
        'more_posts': more_posts,
        'total_posts': total_posts
    }

    return basic_info, profile_id


