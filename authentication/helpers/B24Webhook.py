from authentication.models import B24keys


def set_webhook(method='', b24_id=1):
    try:
        b24_key = B24keys.objects.get(id=b24_id)  # get b24 keys from db (ID -> 1)
        b24_webhook = b24_key.b24_webhook
        b24_webhook += method

    except B24keys.DoesNotExist:
        b24_webhook = False

    return b24_webhook

