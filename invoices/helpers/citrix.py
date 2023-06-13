import requests
import json

from telegram_bot.models import User
from .bitrix import BitrixHelper
from invoices.models import RightSignatureSettings, RightSignatureTemplate, RightSignatureDocument, Invoice


class RightSignatureHelper:
    """Class for working with RightSignature API by Citrix."""

    def __init__(self):
        self.settings = RightSignatureHelper.get_settings()
        self.token = self.get_access_token()
        self.api_version = "v2"

    @staticmethod
    def get_settings():
        """Get first active record with settings for RightSignature API"""

        return RightSignatureSettings.objects.filter(is_active=True).first()

    @staticmethod
    def get_template():
        """Get first active record with template for RightSignature API"""

        return RightSignatureTemplate.objects.filter(is_active=True).first()

    def get_code(self):
        """This should do in web browser as a GET request with params, which are used below.
        Then need to manually fill company name, login and password and in url you'll get code"""

        url = f"https://secure.sharefile.com/oauth/authorize"
        params = {
            "client_id": self.settings.client_id,
            "redirect_uri": self.settings.redirect_uri,
            "response_type": "code"
        }

        response = requests.get(url=url, params=params)

        return response

    def get_access_token(self):
        """Get token info from api.

        Returned object example::

            {
                "access_token": "kSGyOMZg7IHUksfevRzc4dPr42mkX1Bd$$m3BMCA9eUSsIRqLpyH4zfAItgSaphDE6",
                "refresh_token": "kSGyOMZg7IHUksfevRzc4dPr42mkX1Bd$$5zw3jTXsB3eXkFjeXSsyZxHghqkY61afWB3qJQ1a",
                "token_type": "bearer",
                "expires_in": 28800,
                "appcp": "sharefile.com",
                "apicp": "sf-api.com",
                "subdomain": "nexxess",
                "access_files_folders": true,
                "modify_files_folders": true,
                "admin_users": true,
                "admin_accounts": true,
                "change_my_settings": true,
                "web_app_login": true
            }
        """

        url = f"https://{self.settings.subdomain}.sharefile.com/oauth/token/"
        data = {
            "client_id": self.settings.client_id,
            "client_secret": self.settings.client_secret,
            "code": self.settings.code,
            "grant_type": "password",
            "username": self.settings.username,
            "password": self.settings.password,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        token_info = requests.post(url=url, data=data, headers=headers).json()

        return token_info

    def prepare_merge_fields(self, invoice, product):
        """Filling fields in pdf before file sending"""

        fields = [
            {
                "name": "benefecial_trust_cb",
                "value": "true"
            },
            {
                "name": "price",
                "value": invoice['PRICE']
            },
            {
                "name": "benefecial_trust",
                "value": "ONE"
            },
            {
                "name": "4_d_no_cb",
                "value": "true"
            },
            {
                "name": "4_e_no_cb",
                "value": "true"
            },
            {
                "name": "4_f_no_cb",
                "value": "true"
            },
            {
                "name": "4_h_no_cb",
                "value": "true"
            },
            {
                "name": "copies_1",
                "value": "ONE"
            },
            {
                "name": "copies_2",
                "value": "ONE"
            },
            {
                "name": "hours",
                "value": product[BitrixHelper.PRODUCT_HOURS_FIELD]['value']
            },
        ]

        return fields

    def send_document(self, contact, invoice, product):
        """Send document for sign"""

        template = self.get_template()

        url = f"https://api.rightsignature.com/public/{self.api_version}/reusable_templates/{template.reference_id}/send_document/"
        data = {
            "message": "Please sign this",
            "expires_in": 1,  # 1 Day for signing
            "roles": [
                {
                    "name": "signer1",
                    "signer_email": "btomchishen@icloud.com",
                    # "signer_email": contact["EMAIL"][0]["VALUE"],
                    # "signer_name": contact["NAME"]
                    "signer_name": "Bohdan"
                }
            ],
            "name": template.name,
            "merge_field_identifier": "name",
            "merge_field_values": self.prepare_merge_fields(invoice, product)
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic cHZfYjhhZDQyZDU1YWVhNGJjNjk5MzgzMjg3NmZmZjczNWY="
        }
        document = requests.post(url=url, json=data, headers=headers).json()

        BitrixHelper.update_entity(
            method='crm.invoice.update',
            entity_id=invoice['ID'],
            fields={
                BitrixHelper.INVOICE_SIGNED_FILE: document['document']['id']
            }
        )

        contact_db = User.objects.get(b24_contact_id=contact['ID'])
        invoice_db = Invoice.objects.get(invoice_id=invoice['ID'])
        RightSignatureDocument.objects.create(
            template=template,
            contact=contact_db,
            invoice=invoice_db,
            status=document['document']['state']
        )

    def check_status(self):
        # TODO: if document was signed update status in DB and prepare a payment link
        pass
