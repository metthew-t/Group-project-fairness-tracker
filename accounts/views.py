from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
from .serializers import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import CustomUser

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        # Add custom claims to the token
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['user_type'] = user.user_type
        
        return Response({
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)

class SendVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        code = ''.join(random.choices('0123456789', k=6))
        user.verification_code = code
        user.verification_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        # Mock sending email/SMS
        subject = 'Your Fairness Tracker Verification Code'
        message = f'Hello {user.username}, your verification code is: {code}. It expires in 10 minutes.'
        send_mail(subject, message, 'noreply@fairness-tracker.com', [user.email])
        
        return Response({'message': 'Verification code sent to your email.'})

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if user.verification_code == code and user.verification_expiry > timezone.now():
            user.email_verified = True
            user.verification_code = None
            user.verification_expiry = None
            user.save()
            return Response({'message': 'Email verified successfully!'})
        else:
            return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)