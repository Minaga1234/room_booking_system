from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        if not username:
            raise ValueError("The Username field must be set.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)  # Default staff status
        extra_fields.setdefault("is_superuser", False)  # Default superuser status
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  # Ensure the role is admin
        if extra_fields.get("role") != "admin":
            raise ValueError('Superuser must have role set to "admin".')
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Lecturer"),  # Maps to "lecturer" in the frontend
        ("student", "Student"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{10,15}$', "Enter a valid phone number.")],
    )
    is_active = models.BooleanField(default=True)

    # Resolve conflicts with related_name
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True,
    )

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email_constraint"),
        ]


class UserProfile(models.Model):
    """
    Optional: Separate user profile model for additional user-related data.
    """

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"