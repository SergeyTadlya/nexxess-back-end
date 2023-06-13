from bitrix24 import Bitrix24
from authentication.helpers.B24Webhook import set_webhook
from invoices.models import LocalInvoice
from telegram_bot.models import User


class BitrixHelper:
    """Class to work with Bitrix."""

    CONTACT_SIGNED_FILES: str = "UF_CRM_1686570886"
    INVOICE_SIGNED_FILE: str = "UF_CRM_1686573344"
    PRODUCT_HOURS_FIELD: str = "PROPERTY_143"

    @staticmethod
    def get_contact(user_id: str):
        """Get Contact info from Bitrix"""

        try:
            user = User.objects.get(pk=user_id)

            url = set_webhook()
            bx24 = Bitrix24(url)
            contact = bx24.callMethod('crm.contact.get', id=user.b24_contact_id)

            return contact
        except Exception as e:
            error_message = f"Contact getting in Invoice payment error: {e}"
            print(error_message)
            return {'status': 'error', 'message': error_message}

    @staticmethod
    def get_invoice(invoice_id: str):
        """Get Invoice info from Bitrix"""

        try:
            invoice = LocalInvoice.objects.get(b24_invoice_id=invoice_id)

            url = set_webhook()
            bx24 = Bitrix24(url)
            invoice = bx24.callMethod('crm.invoice.get', id=invoice.b24_invoice_id)

            return invoice
        except Exception as e:
            error_message = f"Invoice getting in Invoice payment error: {e}"
            print(error_message)
            return {'status': 'error', 'message': error_message}

    @staticmethod
    def get_product(product_id: str):
        """Get Product info from Bitrix"""

        try:
            url = set_webhook()
            bx24 = Bitrix24(url)
            product = bx24.callMethod('crm.product.get', id=product_id)

            return product
        except Exception as e:
            error_message = f"Product getting in Invoice payment error: {e}"
            print(error_message)
            return {'status': 'error', 'message': error_message}

    @staticmethod
    def update_entity(method: str, entity_id: str, fields: dict):
        """Update entity fields"""

        try:
            url = set_webhook()
            bx24 = Bitrix24(url)
            entity = bx24.callMethod(method, id=entity_id, fields=fields)

            return entity
        except Exception as e:
            error_message = f"Update entity in Invoice payment error - {method} - {entity_id}: {e}"
            print(error_message)
            return {'status': 'error', 'message': error_message}
