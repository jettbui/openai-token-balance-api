"""
Models for the Database.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """Manager for Users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new User."""
        if not email:
            raise ValueError('Users must have an email address.')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create, save, and return a new User as a superuser."""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User for the API."""
    id = models.AutoField(primary_key=True, unique=True, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Balance(models.Model):
    """Balance model for the API."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    balance = models.PositiveIntegerField(default=0)

    @receiver(models.signals.post_save, sender=User)
    def create_user_balance(sender, instance, created, **kwargs):
        """Create Balance for a new User."""
        if created:
            Balance.objects.create(user=instance)

    def __str__(self):
        """Return the string representation of the model."""
        return str(self.user)
