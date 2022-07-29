
#Sspotify postman request
import requests

birdy_uri = "4PULA4EFzYTrxYvOVlwpiQ"

url = "http://127.0.0.1:5011/spotify"

payload='birdy_uri='+ birdy_uri
headers = {
   'Content-Type': 'application/x-www-form-urlencoded'
}
response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

