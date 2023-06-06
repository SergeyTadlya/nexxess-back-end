from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from telegram import Bot

from .Helper import SettingsHelper

from ..handlers import MessageHandler, CallbackHandler

import logging
import json


logger = logging.getLogger(__name__)


@csrf_exempt
def main(request):
    api_token = SettingsHelper.get_bot_token()
    bot = Bot(token=api_token)

    if request.method == 'POST':
        data = json.loads(request.body)

        if 'message' in data:
            message_handler = MessageHandler(bot, data)
            message_handler.handle_request()

            # Message logger credentials
            telegram_username = data['message']['from']['username']
            telegram_user_id = ' (' + str(data['message']['from']['id']) + ') - '

            if 'text' in data['message'].keys():
                user_message = data['message']['text']
                logger.info('Message: ' + telegram_username + telegram_user_id + user_message)

            elif 'successful_payment' in data['message'].keys():
                amount = '(' + str(data['message']['successful_payment']['total_amount'] / 100)
                currency = ' ' + data['message']['successful_payment']['currency'] + ' '
                invoice_payload = data['message']['successful_payment']['invoice_payload'] + ')'

                logger.info('Successful payment: ' + telegram_username + telegram_user_id + amount + currency + invoice_payload)

            else:
                logger.info('Message: ' + telegram_username + telegram_user_id + 'Not text')

        elif 'callback_query' in data:
            callback_handler = CallbackHandler(bot, data)
            callback_handler.handle_request()

            # Callback logger credentials
            telegram_username = data['callback_query']['from']['username']
            telegram_user_id = ' (' + str(data['callback_query']['from']['id']) + ') - '
            user_callback_data = ' (' + data['callback_query']['data'] + ')'

            button_title = ''
            inline_keyboard = data["callback_query"]["message"]["reply_markup"]["inline_keyboard"]
            for i in range(len(inline_keyboard)):
                for j in range(len(inline_keyboard[i])):
                    for key, value in inline_keyboard[i][j].items():
                        if value == data['callback_query']['data']:
                            button_title = inline_keyboard[i][j]['text']

            logger.info('Callback: ' + telegram_username + telegram_user_id + button_title + user_callback_data)

        elif 'pre_checkout_query' in data:
            callback_handler = CallbackHandler(bot, data)
            callback_handler.handle_request()

            # Payment logger credentials
            telegram_username = data['pre_checkout_query']['from']['username']
            telegram_user_id = str(data['pre_checkout_query']['from']['id'])
            pre_checkout_query_id = data['pre_checkout_query']['id']

            logger.info('Callback: ' + telegram_username + ' (' + telegram_user_id + ') - ' + pre_checkout_query_id)

    return HttpResponse('')
