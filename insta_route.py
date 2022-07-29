import email
from insta_main import instagram_main
import flask
import json
import time
from flask import jsonify, Flask
from flask import request
import requests

# from flask import jsonify
# from flask import Flas

# link = 'https://www.instagram.com/umair.uy/'
# link = 'https://www.instagram.com/umair.uy/'
# USERNAME = "nomismart460@gmail.com"
# PASSWORD = "NomihashSmart123"

app = Flask(__name__)
@app.route('/')

def hello_world():
   return 'Hello on cloud'
@app.route('/instagram/<username>/<pswrd>/<link>',  methods= ["GET", 'POST'])
def getstart(username,pswrd,link):
   #  profile_link = request.form.get('link')
   #  username = request.form.get('email')
   #  pasword = request.form.get('pswrd')
   #link = 'https://www.instagram.com/umair.uy/'
   link = 'https://www.instagram.com/umair.uy/'
   username = "nomismart460@gmail.com"
   pswrd = "Nomi#Smart123"
   insta_data = instagram_main(username, pswrd, link)
   return json.dumps(insta_data)


if __name__ == '__main__':
   app.run(host='127.0.0.1',port=5511)



# link = 'https://www.instagram.com/umair.uy/'
# USERNAME = "nomismart460@gmail.com"
# PASSWORD = "Nomi#Smart123"
# url = "http://127.0.0.1:5511/instagram"
# headers = {
#    'Content-Type': 'application/x-www-form-urlencoded'
# }

# payload='link= '+link+'&email='+USERNAME+'&pswrd='+PASSWORD+''
# response = requests.request("GET", url, headers=headers, data=payload)
# time.sleep()
# print(response.text)





