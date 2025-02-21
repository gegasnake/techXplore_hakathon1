from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

from core.models import MainAccount


class CustomUserManager(BaseUserManager):
    def create_user(self, ssn, phone_number, password=None, **extra_fields):
        # Validate uniqueness of SSN and phone number
        if CustomUser.objects.filter(ssn=ssn).exists():
            raise ValidationError("A user with this SSN already exists.")
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("A user with this phone number already exists.")

        if not ssn:
            raise ValueError("The SSN field must be set")
        user = self.model(ssn=ssn, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Create MainAccount for the user with 0 GEL
        MainAccount.objects.create(user=user, balance=0)

        return user

    def create_superuser(self, ssn, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(ssn, phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ssn = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(r'^\d{11}$', "SSN must be exactly 11 digits.")
        ]
    )
    phone_number = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(r'^\d{9}$', "Phone number must be exactly 9 digits.")
        ]
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["ssn"]

    def __str__(self):
        return self.phone_number

