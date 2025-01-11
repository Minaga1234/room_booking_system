from django.contrib.auth.models import AbstractUser, BaseUserManager
<<<<<<< HEAD
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

=======
from django.db import models


>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
<<<<<<< HEAD
        if CustomUser.objects.filter(username=username).exists():
            raise ValueError('A user with this username already exists.')
        if CustomUser.objects.filter(email=email).exists():
            raise ValueError('A user with this email already exists.')
=======
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

<<<<<<< HEAD

=======
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')  # Ensure the role is admin
        if extra_fields.get('role') != 'admin':
            raise ValueError('Superuser must have role set to "admin".')
        return self.create_user(username, email, password, **extra_fields)

<<<<<<< HEAD
=======

>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]
<<<<<<< HEAD
    email = models.EmailField(unique=True)  # Ensure email is unique
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)  # Optional username
=======
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)

<<<<<<< HEAD
    USERNAME_FIELD = 'email'  # Use email as the primary identifier
    REQUIRED_FIELDS = ['username']  # Add username as a required field if needed

    objects = CustomUserManager()

    def __str__(self):
        return self.email  # Return email for representation
=======
    # Resolve conflicts with related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # Adjusted related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # Adjusted related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        return self.username
>>>>>>> 574110dd6dcb3717a7e05795ad1887ba00793b63
