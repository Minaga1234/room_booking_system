from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
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
<<<<<<< HEAD
        if self.action in ['register_user', 'login']:
            return [permissions.AllowAny()]
=======
        if self.action in ['create']:
            return [IsAdmin()]  # Restrict user creation to admins only
        elif self.action in ['login']:
            return [permissions.AllowAny()]  # Allow anyone to log in
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        elif self.action in ['list', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'deactivate']:
            return [IsAdminOrStaff()]
        elif self.action in ['profile', 'change_password']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['GET','POST'], permission_classes=[permissions.AllowAny])
    def register_user(self, request):
        if request.method == "GET":
            return Response({"info": "Use POST to register a new user."}, status=status.HTTP_200_OK)
        elif request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
<<<<<<< HEAD
        """
        User login with email and password.
        """
=======
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
<<<<<<< HEAD
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password):
=======
            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=401)
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
            if not user.is_active:
                return Response({"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
            })
<<<<<<< HEAD
        return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
=======
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=401)
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """
        Retrieve the authenticated user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

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
<<<<<<< HEAD
        Disable listing all users.
=======
        Disable the list view for all users.
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        """
        return Response({"detail": "Not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, *args, **kwargs):
        """
        Disable retrieving individual user details.
        """
        return Response({"detail": "Not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
