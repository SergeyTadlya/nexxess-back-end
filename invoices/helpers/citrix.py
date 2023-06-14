import requests
import base64

from telegram_bot.models import User
from .bitrix import BitrixHelper
from invoices.models import RightSignatureSettings, RightSignatureTemplate, RightSignatureDocument, Invoice, \
    ShareFileSettings, RightSignatureField


class RightSignatureHelper:
    """Class for working with RightSignature API by Citrix."""

    def __init__(self):
        self.settings = RightSignatureHelper.get_settings()
        self.api_version = "v2"

    @staticmethod
    def get_settings():
        """Get first active record with settings for RightSignature API"""

        return RightSignatureSettings.objects.filter(is_active=True).first()

    @staticmethod
    def get_template():
        """Get first active record with template for RightSignature API"""

        return RightSignatureTemplate.objects.filter(is_active=True).first()

    @staticmethod
    def convert_private_api_to_base64(private_api):
        """Convert private API key to base64 for using in auth for RightSignature"""

        message_bytes = private_api.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        return base64_message

    @staticmethod
    def prepare_merge_fields(invoice, product, template):
        """Filling fields in pdf before file sending"""

        merge_fields = []
        fields = RightSignatureField.objects.filter(template=template)

        for field in fields:
            if field.name == 'price':
                merge_fields.append({'name': field.name, 'value': invoice['PRICE']})
            elif field.name == 'hours':
                merge_fields.append({'name': field.name, 'value': product[BitrixHelper.PRODUCT_HOURS_FIELD]['value']})
            else:
                merge_fields.append({'name': field.name, 'value': field.value})

        return merge_fields

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
                    "signer_email": contact["EMAIL"][0]["VALUE"],
                    "signer_name": contact["NAME"]
                }
            ],
            "name": template.name,
            "merge_field_identifier": "name",
            "merge_field_values": RightSignatureHelper.prepare_merge_fields(invoice, product, template)
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {RightSignatureHelper.convert_private_api_to_base64(self.settings.private_api)}"
        }
        document = requests.post(url=url, json=data, headers=headers).json()

        BitrixHelper.update_entity(
            method='crm.invoice.update',
            entity_id=invoice['ID'],
            fields={
                BitrixHelper.INVOICE_SIGNED_FILE: document['document']['id']
            }
        )

        db_contact = User.objects.get(b24_contact_id=contact['ID'])
        db_invoice = Invoice.objects.get(invoice_id=invoice['ID'])
        RightSignatureDocument.objects.create(
            reference_id=document['document']['id'],
            template=template,
            contact=db_contact,
            invoice=db_invoice,
            status=document['document']['state']
        )

    def check_status(self, contact, invoice) -> bool:
        """Check document status.
        If document was signed update status in DB, """

        db_contact = User.objects.get(b24_contact_id=contact['ID'])
        db_invoice = Invoice.objects.get(invoice_id=invoice['ID'])
        db_document = RightSignatureDocument.objects.get(
            contact=db_contact,
            invoice=db_invoice
        )

        url = f"https://api.rightsignature.com/public/{self.api_version}/documents/{db_document.reference_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {RightSignatureHelper.convert_private_api_to_base64(self.settings.private_api)}"
        }

        document = requests.get(url=url, headers=headers).json()

        if document['document']['state'] == 'executed':
            db_document.status = 'executed'
            db_document.save()

            BitrixHelper.update_entity(
                method='crm.contact.update',
                entity_id=contact['ID'],
                fields={
                    BitrixHelper.CONTACT_SIGNED_FILES: [document['document']['id']]
                }
            )

            return True

        return False


class ShareFileHelper:
    """Class for working with ShareFile API by Citrix.

    This class is actually unused, but you can use it in Future to work with ShareFile APIs.
    For using a class add fields into admin.py

    Methods:
        get_code: require a work with web interface. You need in browser make a request to the link in method
            and then make an auth to ShareFile account and in link you will get a code

        get_access_token: need to get access and refresh tokens and other needed info
    """

    def __init__(self):
        self.settings = ShareFileHelper.get_settings()
        self.token = self.get_access_token()

    @staticmethod
    def get_settings():
        """Get first active record with settings for RightSignature API"""

        return ShareFileSettings.objects.filter(is_active=True).first()

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
