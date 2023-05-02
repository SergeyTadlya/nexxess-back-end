from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    b24_contact_id = models.PositiveIntegerField(verbose_name='Bitrix24 contact ID', unique=True, null=True, blank=True)
    email = models.EmailField(max_length=64, unique=True)
    username = models.CharField(verbose_name='Username', max_length=64, null=True, blank=True)
    photo = models.ImageField(default='profile-user.png', upload_to='')
    telegram_id = models.PositiveIntegerField(verbose_name='Telegram user ID', unique=True, null=True, blank=True)
    first_name = models.CharField(verbose_name='First name', max_length=50, null=True, blank=True)
    last_name = models.CharField(verbose_name='Last name', max_length=50, null=True, blank=True)
    step = models.CharField(verbose_name='Step', max_length=50, default='Nothing', null=True, blank=True)
    activation_code = models.CharField(verbose_name='Activation code', max_length=16, null=True, blank=True)
    google_auth = models.BooleanField(verbose_name='Google Auth', default=False, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
