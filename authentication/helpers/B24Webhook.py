from authentication.models import B24keys

try:
    B24keys = B24keys.objects.get(id=1)     # get b24 keys from db (1 - id)
    B24_WEBHOOK = B24keys.b24_webhook       # init b24 webhook
except B24keys.DoesNotExist:
    B24_WEBHOOK = False