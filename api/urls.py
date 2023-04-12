"""ursl shema for api v1"""
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import UserAPICreate, UserAPIDetailView
from django.urls import path, include, re_path


urlpatterns = [
    # djoser
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    # djoser
    # auth
    path('auth/register/', UserAPICreate.as_view()),
    path('auth/update/<int:pk>/', UserAPIDetailView.as_view()),
    # auth
]