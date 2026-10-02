from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    mfa_secret_code = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    mfa_authentication_image = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'middle_name',
            'last_name',
            'full_name',
            'mobile',
            'phone',
            'username',
            'email',
            'password',
            'address',
            'user_type',
            'access_type',
            'is_mfa_enabled',
            'is_email_authentication_enabled',
            'mfa_secret_code',
            'mfa_authentication_image',
            'is_active',
            'last_logged_in',
            'is_staff',
            'is_superuser',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email_or_user = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), email=email_or_user, password=password)
        if not user:
            # Fallback authenticate by username if email lookup wasn't directly found
            try:
                user_obj = User.objects.get(username=email_or_user)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        if not user.is_active:
            raise serializers.ValidationError('This account has been deactivated.')

        attrs['user'] = user
        return attrs
