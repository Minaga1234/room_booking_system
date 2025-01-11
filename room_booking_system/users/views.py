#Users/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin, IsAdminOrStaff
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email', 'role']

    def get_permissions(self):
        """
        Assign permissions based on the action being performed.
        """
<<<<<<< HEAD
        if self.action in ['create']:
            return [IsAdmin()]  # Restrict user creation to admins only
        elif self.action in ['login']:
            return [permissions.AllowAny()]  # Allow anyone to log in
=======
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
        elif self.action in ['list', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'deactivate']:
            return [IsAdminOrStaff()]
        elif self.action == 'profile':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
<<<<<<< HEAD
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=401)
=======
        """
        Handle user login and return JWT tokens.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=403)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
            })
<<<<<<< HEAD
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=401)
=======
        return Response({"error": "Invalid credentials"}, status=401)
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        Retrieve the authenticated user's profile information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update the authenticated user's profile information.
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account (Admin only).
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"message": f"User {user.username} deactivated successfully"})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change the authenticated user's password.
        """
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password"}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated successfully"})
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account (Admin only).
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"message": f"User {user.username} has been deactivated."})

    def list(self, request, *args, **kwargs):
        """
<<<<<<< HEAD
        Disable the list view for all users.
=======
        Disable the list view for users.
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
        """
        return Response({"detail": "Not allowed."}, status=405)

    def retrieve(self, request, *args, **kwargs):
        """
        Disable the retrieve view for individual users.
        """
        return Response({"detail": "Not allowed."}, status=405)
