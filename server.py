import requests

BOT_TOKEN = '7583600247:AAHpDr9cEsiYOQmSwGqJoSO1mVN_GtcGHgs'
CHAT_ID = '-1002329779058'  # сюда — ID канала

url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
data = {
    'chat_id': CHAT_ID,
    'text': '🌸 Привет от MirumoBot!'
}

response = requests.post(url, data=data)
print(response.json())
