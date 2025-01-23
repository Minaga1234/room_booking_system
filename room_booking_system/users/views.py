from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin, IsAdminOrStaff
from django.db.models import Q

# CSRF Token View
@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """
    Return a new CSRF token for the frontend.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email', 'role']

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['create', 'login', 'register_user']:
            return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'deactivate']:
            return [IsAdminOrStaff()]
        elif self.action in ['profile']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List users with optional filters for role, status, and search.
        """
        queryset = self.get_queryset()

        # Apply role filter
        role = request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)

        # Apply status filter
        status = request.query_params.get('status', None)
        if status:
            is_active = status.lower() == 'active'
            queryset = queryset.filter(is_active=is_active)

        # Apply search filter
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(role__icontains=search)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



    # User Registration
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register_user(self, request):
        """
        Register a new user.
        """
        try:
            data = request.data
            role = data.get("role", "student").lower()
            if role not in ["student", "staff", "admin"]:
                return Response({"error": "Invalid role. Must be 'student', 'staff', or 'admin'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check required fields
            if not data.get("email"):
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get("password"):
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Check for duplicates
            if CustomUser.objects.filter(email=data["email"]).exists():
                return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

            # Auto-generate a username from the email
            username = data.get("username", data["email"].split('@')[0])
            if CustomUser.objects.filter(username=username).exists():
                return Response({"error": "This username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure proper `is_staff` setting for staff/admin roles
            is_staff = True if role in ["staff", "admin"] else False

            serializer = self.get_serializer(data={
                "username": username,
                "email": data["email"],
                "password": data["password"],
                "role": role,
                "is_staff": is_staff,
            })

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Login Method
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        Login with email or username and password.
        """
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(email=email)

        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password):
            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
            })

        return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    # Profile View
    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """
        Manage the authenticated user's profile.
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    # Deactivate User
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"message": f"User {user.username} deactivated successfully"})

    # Deactivate Self
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def deactivate_self(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "Your account has been deactivated successfully."})
