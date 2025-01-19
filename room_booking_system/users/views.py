from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin, IsAdminOrStaff

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
    """
    ViewSet for managing user-related operations.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'email', 'role']

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['create']:
            return [IsAdmin()]  # Restrict user creation to admins only
        elif self.action in ['login', 'profile', 'register_user']:
            return [permissions.AllowAny()]  # Allow anyone to log in or fetch public profile data
        elif self.action in ['list', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'deactivate']:
            return [IsAdminOrStaff()]
        elif self.action in ['change_password']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    def register_user(self, request):
        """
        Register a new user.
        """
        try:
            data = request.data
            print("Incoming data:", data)  # Debug incoming data

            role = data.get("role", "student").lower()
            if role == "lecturer":
                role = "staff"
            if role not in ["student", "staff", "admin"]:
                return Response({"error": "Invalid role. Must be 'student', 'staff', or 'admin'."},
                                status=status.HTTP_400_BAD_REQUEST)

            if not data.get("username"):
                return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get("email"):
                return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not data.get("password"):
                return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Check for duplicates
            if CustomUser.objects.filter(email=data["email"]).exists():
                return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(username=data["username"]).exists():
                return Response({"error": "This username is already taken."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure is_staff is set properly for staff members
            serializer = self.get_serializer(data={
                "username": data["username"],
                "email": data["email"],
                "password": data["password"],
                "role": role,
                "is_staff": True if role == "staff" else False,
            })

            if not serializer.is_valid():
                print("Validation errors:", serializer.errors)  # Debug validation errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Unexpected error:", str(e))  # Debug unexpected exceptions
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        User login with email and password.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)

            if user.role not in ["student", "staff", "admin"]:
                return Response({"error": "Unknown user role. Please contact support."}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def profile(self, request):
        """
        Retrieve basic public user profile data without requiring authentication.
        """
        email = request.query_params.get("email")  # Expect `email` as a query param
        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Change password for the authenticated user.
        """
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"message": f"User {user.username} deactivated successfully."})

    def list(self, request, *args, **kwargs):
        """
        Disable the list view for all users.
        """
        return Response({"detail": "Not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        """
        Disable retrieving individual user details.
        """
        return Response({"detail": "Not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
