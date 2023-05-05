from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from telegram import Bot

from .Helper import SettingsHelper

from ..handlers import MessageHandler
from ..handlers import CallbackHandler

import json


@csrf_exempt
def main(request):
    api_token = SettingsHelper.get_bot_token()
    bot = Bot(token=api_token)

    if request.method == 'POST':
        data = json.loads(request.body)

        if 'message' in data:
            message_handler = MessageHandler(bot, data)
            message_handler.handle_request()
            if 'text' in data['message'].keys():
                print(f"Message from: {data['message']['from']['id']} - {data['message']['text']}")
            else:
                print(f"Message from: {data['message']['from']['id']} - Not text")

        elif 'callback_query' in data:
            callback_handler = CallbackHandler(bot, data)
            callback_handler.handle_request()
            print(f"Message from: {data['callback_query']['from']['id']} - {data['callback_query']['message']['text']}")

    return HttpResponse('Main worked')
