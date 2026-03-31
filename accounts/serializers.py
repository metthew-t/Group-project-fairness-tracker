from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'first_name', 'last_name', 'phone_number', 'bio', 'avatar']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'bio', 'avatar', 'user_type', 'first_name', 'last_name', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 from the data
        validated_data.pop('password2')
        user_type = validated_data.get('user_type')
        
        # Create user using create_user (handles password hashing)
        user = CustomUser.objects.create_user(**validated_data)
        
        # If instructor, generate verification code immediately
        if user_type == 'INSTRUCTOR':
            from django.utils import timezone
            from datetime import timedelta
            import random
            
            code = ''.join(random.choices('0123456789', k=6))
            user.verification_code = code
            user.verification_expiry = timezone.now() + timedelta(minutes=10)
            user.email_verified = False
            
            # Send initial verification email
            from django.core.mail import send_mail
            subject = 'Your Fairness Tracker Verification Code'
            message = f'Hello {user.username}, your instructor verification code is: {code}. It expires in 10 minutes.'
            send_mail(subject, message, 'noreply@fairness-tracker.com', [user.email])
        else:
            # For others, we can keep it True for now as per previous testing preference, 
            # or set to False if we want total security. 
            # The prompt specifically mentioned "for instructor".
            user.email_verified = True
            
        user.save()
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['user_type'] = user.user_type
        return token