import requests

today = requests.get("https://zenquotes.io/api/today")
quote = today.json()[0]['q']
author = today.json()[0]['a']
print(quote + " (" + author + ")")
