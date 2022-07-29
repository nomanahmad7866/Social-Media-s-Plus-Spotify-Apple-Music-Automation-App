import email

import flask
import json
import time
from flask import jsonify, Flask
from flask import request

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
#Authentication - without user
# client_id = "38120e37f66a427195047b801fce0851"
# secret = "769ce2b54e1d4e70b580d9e21473edcb"
# birdy_uri = "4PULA4EFzYTrxYvOVlwpiQ"

app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello on cloud'

@app.route('/spotify',  methods= ["GET",'POST'])
def spotipy_music():
    play_lists = []
    import pdb; pdb.set_trace()
    client_id = "38120e37f66a427195047b801fce0851"
    secret = "769ce2b54e1d4e70b580d9e21473edcb"
    birdy_uri = request.form.get('birdy_uri')
    #birdy_uri='spotify:artist:2oSONSC9zQ4UonDKnLqksx'
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    results=sp.artist_albums(birdy_uri,album_type='album')
    albums=results['items']
    # while results['next']:
    #     results=sp.next(results)

    albums.extend(results['items'])
    if albums:
        for album in albums:
            play_name = album['name']
            if play_name not in play_lists:
                play_lists.append(play_name)
    else:
        play_lists = "No playlist"
        return play_lists

    return json.dumps(play_lists)

if __name__ == '__main__':
   app.run(host='127.0.0.1',port=5011)


#Sspotify postman request
import requests

# birdy_uri = "4PULA4EFzYTrxYvOVlwpiQ"
# url = "http://127.0.0.1:5011/spotify"

# payload='birdy_uri='+ birdy_uri
# headers = {
#    'Content-Type': 'application/x-www-form-urlencoded'
# }
# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)


