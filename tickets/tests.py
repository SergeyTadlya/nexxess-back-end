from django.test import TestCase


# test function add file in ticket
# from django.core.files.base import ContentFile
# from authentication.models import B24keys
# from bitrix24 import *
# from django.http import HttpResponse
# from tickets.models import TicketComments
# import requests
# def test(request):
#     b24keys = B24keys.objects.first()
#     domain = b24keys.domain
#     rest_key = b24keys.rest_key
#     b24_comment = 'task.commentitem.get'
#     bx24 = Bitrix24(domain + rest_key)
#
#     # check if comment is isset in ticket
#     comment = bx24.callMethod(
#         b24_comment,
#         taskId=78,
#         itemId=388,
#     )
#     print(comment)
#
#     # if file is isset in comment
#     if 'ATTACHED_OBJECTS' in comment:
#         for file_data in comment['ATTACHED_OBJECTS']:
#             file_item = file_data
#
#         # Завантаження файлу з URL
#         # file_download_url = comment['ATTACHED_OBJECTS'][file_item]['DOWNLOAD_URL']
#         file_view_url = domain[:-1] + comment['ATTACHED_OBJECTS'][file_item]['VIEW_URL']
#         file_name = comment['ATTACHED_OBJECTS'][file_item]['NAME']
#
#
#
#         # file_url = "https://450d-188-190-190-33.ngrok-free.app/media/profile-user.png"
#         response = requests.get(file_view_url)
#         image_content = response.content
#         image_file = ContentFile(image_content)
#         # image_name = "test.png"
#
#         new_comment = TicketComments.objects.get(id=20)
#         new_comment.added_documents.save(file_name, image_file)
#         new_comment.save()
#
#     return HttpResponse()