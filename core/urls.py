from django.urls import path
from .views import ping
from .views import UserProfileDetail, ChangePasswordView

urlpatterns = [
    path('api/ping/', ping),
    path('api/user-profile/<int:pk>/', UserProfileDetail.as_view(), name='user-profile-detail'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
