from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from telegram import Bot

from .Helper import SettingsHelper

from ..handlers import MessageHandler, CallbackHandler

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
                print('Message from: ' + str(data['message']['from']['id']) + ' - ' + data['message']['text'] + '\n')
            else:
                print('Message from: ' + str(data['message']['from']['id']) + ' - Not text\n')

        elif 'callback_query' in data:
            callback_handler = CallbackHandler(bot, data)
            callback_handler.handle_request()

            if 'text' in data['callback_query']['message'].keys():
                print('Callback from: ' + str(data['callback_query']['from']['id']) + ' - ' + data['callback_query']['data'] + '\n')
            else:
                print('Callback from: ' + str(data['callback_query']['from']['id']) + ' - Not text\n')

    return HttpResponse('Main')
