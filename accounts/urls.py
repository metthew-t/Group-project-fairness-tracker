from django.urls import path
from .views import RegisterView, SendVerificationView, VerifyEmailView, MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-verification/', SendVerificationView.as_view(), name='send-verification'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
]