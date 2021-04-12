import requests
import re
from decouple import config
from pprint import pprint
import json
from flask import Flask, request, Response
from flask_sslify import SSLify
import numpy as np

cmc_token = config('CMCKEY')
telegram_token = config('TELEGRAMKEY')
app = Flask(__name__)
sslify = SSLify(app)


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return None


def get_cmc_data(crypto):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'ZAR'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}

    r = requests.get(url, headers=headers, params=params).json()
    price = r["data"][crypto]["quote"]["ZAR"]["price"]
    write_json(r)

    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    pattern = r'/[a-zA-Z]{2,4}'
    ticker = re.findall(pattern, txt)
    if ticker:
        symbol = ticker[0][1:].upper()
    else:
        symbol = ''
    
    return chat_id, symbol


def send_message(chat_id, text):
    url = "https://api.telegram.org/bot{}/sendMessage".format(telegram_token)
    payload = {'chat_id': chat_id, 'text': text}

    r = requests.post(url, json=payload)
    return r


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message(msg)

        if not symbol:
            send_message(chat_id, 'Wrong Data')
            return Response('Ok', status=200)
        
        price = get_cmc_data(symbol)
        send_message(chat_id, price)
        # write_json(msg, filename='telegram_req.json')

        return Response('Ok', status=200)
    else:
        return "<h1>CoinMarketCap Bot<h1>"


def main():
    print("ZAR: {}".format(get_cmc_data('BTC')))


if __name__ == "__main__":
    # main()
    app.run()