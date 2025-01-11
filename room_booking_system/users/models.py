from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
<<<<<<< HEAD
            raise ValueError("The Email field must be set.")
=======
            raise ValueError('The Email field must be set.')
        if CustomUser.objects.filter(username=username).exists():
            raise ValueError('A user with this username already exists.')
        if CustomUser.objects.filter(email=email).exists():
            raise ValueError('A user with this email already exists.')
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
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
        ("staff", "Staff"),
        ("student", "Student"),
    ]
<<<<<<< HEAD

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{10,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    is_active = models.BooleanField(default=True)
=======
    email = models.EmailField(unique=True)  # Ensure email is unique
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)  # Optional username
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109

    USERNAME_FIELD = 'email'  # Use email as the primary identifier
    REQUIRED_FIELDS = ['username']  # Add username as a required field if needed

    objects = CustomUserManager()

    def __str__(self):
<<<<<<< HEAD
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
=======
        return self.email  # Return email for representation
>>>>>>> 95be7a5d30d503825ae028e43040e0af7f1c5109
