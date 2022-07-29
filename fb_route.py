
import flask
import time
from flask import jsonify, Flask
log = print

from ge_fb_data import return_fb_data




app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello on cloud'
@app.route('/facebook/<username>/<pswrd>/<link>',  methods= ["GET", 'POST'])

def getstart(username,pswrd,link):
   friends_data = []
   about_data = {}
   import pdb; pdb.set_trace()
   friends_data, about_data = return_fb_data(username,pswrd,link)

   return about_data, friends_data



if __name__ == '__main__':
   app.run(host='localhost',port=5001)




# app.run(host='127.0.0.1', port=150)