import os
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from .models import Branding, Degree, Theme
from .serializers import DegreeSerializer, BrandingSerializer, ThemeSerializer

# Setup logging
logger = logging.getLogger(__name__)

class BrandingSettingsView(TemplateView):
    template_name = "branding/settings.html"


class BrandingSettingsAPI(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        branding = Branding.objects.first()
        if not branding:
            return Response({"detail": "Branding settings not found."}, status=404)

        serializer = BrandingSerializer(branding)
        return Response(serializer.data)

    def put(self, request):
        branding = Branding.objects.first()
        if not branding:
            return Response({"detail": "Branding settings not found."}, status=404)

        serializer = BrandingSerializer(branding, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Branding settings updated by {request.user.username}.")
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


class BrandingAssetsAPI(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        if not request.user.is_staff:
            raise PermissionDenied("You must be an admin to upload branding assets.")

        favicon = request.FILES.get("favicon")
        login_background = request.FILES.get("login_background")

        # Ensure the assets path exists
        assets_path = os.path.join(settings.BASE_DIR, "../frontend/assets/branding/")
        os.makedirs(assets_path, exist_ok=True)

        saved_files = {}

        # Save favicon
        if favicon:
            favicon_path = os.path.join(assets_path, "favicon.png")
            with open(favicon_path, "wb") as f:
                for chunk in favicon.chunks():
                    f.write(chunk)
            saved_files["favicon"] = "/assets/branding/favicon.png"

        # Save login background
        if login_background:
            login_bg_path = os.path.join(assets_path, "login_background.jpg")
            with open(login_bg_path, "wb") as f:
                for chunk in login_background.chunks():
                    f.write(chunk)
            saved_files["login_background"] = "/assets/branding/login_background.jpg"

        # Update branding model
        branding = Branding.objects.first()
        if not branding:
            branding = Branding.objects.create()

        branding.favicon = saved_files.get("favicon", branding.favicon)
        branding.login_background = saved_files.get("login_background", branding.login_background)
        branding.save()

        logger.info(f"Branding assets uploaded by {request.user.username}. Files: {saved_files}")
        return Response({"message": "Assets uploaded successfully!", "files": saved_files}, status=200)


class DegreeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            degrees = Degree.objects.all()
            serializer = DegreeSerializer(degrees, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching degrees: {e}")
            return Response({"detail": "Internal server error while fetching degrees."}, status=500)


    def post(self, request):
        serializer = DegreeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Degree '{serializer.data['name']}' added by {request.user.username}.")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk=None):
        degree_id = request.data.get("id")
        if not degree_id:
            return Response({"detail": "Degree ID is required."}, status=400)

        try:
            degree = Degree.objects.get(pk=degree_id)
            # Check for dependencies
            if Branding.objects.filter(degrees=degree).exists():
                return Response({"detail": f"Cannot delete degree '{degree.name}' as it is linked to a branding."}, status=400)
            degree.delete()
            logger.info(f"Degree '{degree.name}' deleted by {request.user.username}.")
            return Response({"message": "Degree deleted successfully."}, status=204)
        except Degree.DoesNotExist:
            return Response({"detail": "Degree not found."}, status=404)


class ThemeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        themes = Theme.objects.all()
        serializer = ThemeSerializer(themes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ThemeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Theme '{serializer.data['name']}' created by {request.user.username}.")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ThemeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def get_object(self, pk):
        try:
            return Theme.objects.get(pk=pk)
        except Theme.DoesNotExist:
            return None

    def get(self, request, pk):
        theme = self.get_object(pk)
        if not theme:
            return Response({"detail": "Theme not found."}, status=404)

        serializer = ThemeSerializer(theme)
        return Response(serializer.data)

    def post(self, request, pk):
        theme = self.get_object(pk)
        if not theme:
            return Response({"detail": "Theme not found."}, status=404)

        # Apply the theme to branding
        branding = Branding.objects.first()
        if branding:
            branding.theme = theme
            branding.save()
            return Response({"message": f"Theme '{theme.name}' applied successfully!"}, status=200)

        return Response({"detail": "Branding settings not found."}, status=404)

    def delete(self, request, pk):
        theme = self.get_object(pk)
        if not theme:
            return Response({"detail": "Theme not found."}, status=404)

        # Check for dependencies
        if Branding.objects.filter(theme=theme).exists():
            return Response({"detail": f"Cannot delete theme '{theme.name}' as it is linked to a branding."}, status=400)

        theme.delete()
        return Response({"message": "Theme deleted successfully."}, status=204)
