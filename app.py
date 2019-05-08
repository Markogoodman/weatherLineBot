import datetime
from flask import Flask, render_template, request, url_for, abort
from bs4 import BeautifulSoup
import requests
import urllib

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

location_map = {
    '1': 'New_Taipei_City',
    '2': 'Taoyuan_City',
    '3': 'Taipei_City'
}


app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('')
# Channel Secret
handler = WebhookHandler('')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    location = str(event.message.text)
    if location not in location_map:
        message = ''
        for key, val in location_map.items():
            message += key + ': ' + val + '\n'
        message = TextSendMessage(text=message)
        line_bot_api.reply_message(event.reply_token, message)
        return
    location = location_map[location]
    url = urllib.request.urlopen('https://www.cwb.gov.tw/V7/forecast/taiwan/' + location + '.htm').read()
    soup = BeautifulSoup(url.decode("utf-8"), 'html.parser')
    tags = soup.find_all(["th", 'td'])
    row = -1
    data = []
    for i, tag in enumerate(tags):
        if i % 5 == 0:
            data.append([])
            row += 1
        data[row].append(tag.text.strip('\n'))
    messages = []
    messages.append(data[0][0])
    for row in data[1:4]:
        s = [row[0], 'Temparature: ' + row[1] + ' ', 'POP: ' + row[4]]
        s = '\n'.join(s)
        messages.append(s)
    message = '\n\n'.join(messages)
    message = TextSendMessage(text=message)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
