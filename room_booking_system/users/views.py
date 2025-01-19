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
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]  # Use Django's built-in IsAdminUser
        elif self.action in ['update', 'partial_update', 'deactivate']:
            return [IsAdminOrStaff()]
        elif self.action == 'profile':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()


    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Handle user login and return JWT tokens.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=403)
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
            })
        return Response({"error": "Invalid credentials"}, status=401)

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """
        GET: Retrieve the authenticated user's profile information.
        PUT: Update the authenticated user's profile information.
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        if request.method == "PUT":
            print("Incoming data for update:", request.data)
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Allow partial updates for the admin interface.
        """
        serializer = self.get_serializer(data=request.data, instance=self.get_object(), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return super().update(request, *args, **kwargs)

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
    def deactivate_self(self, request):
        """
        Allow a user to deactivate their own account.
        """
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "Your account has been deactivated successfully."})


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
        Allow admins to list all users.
        """
        if request.user.is_superuser or request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({"detail": "Not allowed."}, status=403)

    def get_queryset(self):
        """
        Apply filters for role and status.
        """
        queryset = super().get_queryset()

        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            is_active = status.lower() == 'active'
            queryset = queryset.filter(is_active=is_active)

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """
        Disable the retrieve view for individual users.
        """
        return Response({"detail": "Not allowed."}, status=405)

    def update(self, request, *args, **kwargs):
        print("Incoming payload:", request.data)  # Log incoming data
        serializer = self.get_serializer(data=request.data, instance=self.get_object(), partial=True)
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)  # Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Perform any additional actions during creation.
        """
        user = serializer.save()
        print(f"User created: {user.username}")  # Debug log for username