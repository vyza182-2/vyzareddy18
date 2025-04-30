import requests
TOKEN = "7849121719:AAFWOI7q1B3q7z-iElBASUTlRYd2OeJeFNE"
response = requests.get(f"https://api.telegram.org/bot7849121719:AAFWOI7q1B3q7z-iElBASUTlRYd2OeJeFNE/getUpdates").json()
print(response)