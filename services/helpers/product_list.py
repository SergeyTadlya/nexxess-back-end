from authentication.helpers.B24Webhook import set_webhook
from bitrix24 import Bitrix24
from authentication.models import B24keys


class Product:
    @staticmethod
    def list(service_type):
        """set product list for service 1,2,3 url"""
        try:
            url = set_webhook()
            bx24 = Bitrix24(url)

            # get value id from custom field
            property_type = bx24.callMethod("crm.product.property.get", id=100)["VALUES"]  # 100 - id custom field "type"
            for property_type_id in property_type:
                property_type_name = property_type[property_type_id]["VALUE"]
                if (property_type_name == service_type):
                    consultation_field_id = property_type_id

            product_list = bx24.callMethod('crm.product.list', order={'PRICE': "ASC"},
                                           filter={"PROPERTY_100": consultation_field_id},
                                           select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID", "PROPERTY_100",
                                                   "DESCRIPTION", "SECTION_ID", "PROPERTY_44"])
            description = []
            for product in product_list:
                # get section title
                section = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"},
                                          filter={"ID": product['SECTION_ID']},
                                          select={"ID", "NAME", "CODE"})
                # description convertation for template
                description_parts = product['DESCRIPTION'].split("•")
                parts_array = []
                for description_part in description_parts:
                    if description_part != "":
                        parts_array.append(description_part.strip().replace('<br>', ''))
                description.append({
                    "ID": product["ID"],
                    "DESCRIPTION": parts_array,
                })

            b24_domain = B24keys.objects.order_by("id").first().domain[:-1]
            context = {
                'b24_domain': b24_domain,
                'services': product_list,
                'services_description': description,
                'section_title': section[0]["NAME"]
            }
        except:
            context = {}

        return context