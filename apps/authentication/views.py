from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.contrib.auth import login, logout

from .models import User
from .serializers import UserSerializer, LoginSerializer
from apps.core.permissions import IsAdminRole
from apps.core.pagination import StandardResultsSetPagination


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        email = data.get('email', '').strip().lower()
        password = data.get('password')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()

        if not email or not password:
            return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        if name and not first_name:
            parts = name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''

        username = data.get('username') or email.split('@')[0]
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            mobile=data.get('mobile', phone),
            address=address,
            user_type=data.get('user_type', 'admin'),
            access_type=data.get('access_type', 'standard'),
            is_active=True,
            is_staff=True,
        )
        user.set_password(password)
        user.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Account created successfully.',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Update last_logged_in datetime
        user.last_logged_in = timezone.now()
        user.save(update_fields=['last_logged_in'])

        # Generate or retrieve token
        token, _ = Token.objects.get_or_create(user=user)

        # Login session
        login(request, user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'message': 'Login successful.'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
        except Exception:
            pass
        logout(request)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD management for Users — Restricted exclusively to Admin.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    pagination_class = StandardResultsSetPagination
    search_fields = ['email', 'username', 'first_name', 'last_name', 'mobile']
