from authentication.helpers.B24Webhook import set_webhook
from bitrix24 import Bitrix24
from services.models import Service, ServiceCategory
from invoices.models import StripeSettings
import stripe





class Category:
    @staticmethod
    def list():
        """set services category list for top menu and service url"""


        return "ok"