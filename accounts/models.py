from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class Roles(models.TextChoices):
    SUPERADMIN = "SUPERADMIN", _("Superadmin")
    COMPANY_ADMIN = "COMPANY_ADMIN", _("Admin Entreprise")
    COMPANY_OPERATOR = "COMPANY_OPERATOR", _("Opérateur Entreprise")
    CLIENT = "CLIENT", _("Client")


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Un email est requis")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Roles.SUPERADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Utilisateur custom :
    - email = identifiant
    - pas de username
    - champ role
    """
    username = None
    email = models.EmailField(_("email address"), unique=True)

    role = models.CharField(
        max_length=32,
        choices=Roles.choices,
        default=Roles.CLIENT,
    )
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # pour createsuperuser

    objects = UserManager()

    def __str__(self):
        return self.email

    # Helpers pratiques
    @property
    def is_superadmin(self):  # property pour templating simple
        return self.role == Roles.SUPERADMIN

    @property
    def is_company_admin(self):
        return self.role == Roles.COMPANY_ADMIN

    @property
    def is_company_operator(self):
        return self.role == Roles.COMPANY_OPERATOR
