from authentication.helpers.B24Webhook import B24_WEBHOOK
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from telegram_bot.models import User

import requests
import logging


logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def create_bitrix_contact(sender, request, user, **kwargs):  # Function to  create bitrix contact in moment of registration
    try:
        method = "crm.contact.add"
        url = B24_WEBHOOK + method
        payload = {
            'fields': {
                'NAME': user.name,
                'PHONE': [{'VALUE': 'no_phone', 'VALUE_TYPE': 'WORK'}],
                'EMAIL': [{'VALUE': user.email, 'VALUE_TYPE': 'WORK'}],
                'SOURCE_ID': 'WEB'
            }
        }

        response = requests.post(url, json=payload)  # Create contact in bitrix
        contact_id = response.json().get('result')

        if response.status_code == 200:
            user.b24_contact_id = contact_id
            user.save()
        return response.json()

    except Exception as e:
        logger.exception(e)
