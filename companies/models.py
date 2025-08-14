from django.db import models
from django.conf import settings
from django.utils.text import slugify
from datetime import timedelta
from django.utils import timezone
import uuid


User = settings.AUTH_USER_MODEL

def default_invite_expiry():
    return timezone.now() + timedelta(days=7)

class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_companies"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_companies"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class CompanyRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin Entreprise"
    OPERATOR = "OPERATOR", "Opérateur"

class CompanyMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=CompanyRole.choices, default=CompanyRole.OPERATOR)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")
        ordering = ["company", "user"]

    def __str__(self):
        return f"{self.user} @ {self.company} ({self.role})"

# Invitation token simple (sans email pour l’instant, lien copiable)
class CompanyInvite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=CompanyRole.choices, default=CompanyRole.ADMIN)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="sent_invites")
    expires_at = models.DateTimeField(default=default_invite_expiry)
    accepted = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.accepted) and timezone.now() < self.expires_at
