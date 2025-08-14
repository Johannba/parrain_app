from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User, Roles
from companies.models import CompanyRole

class CompanyAdminCreateForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmation", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned

    def create_or_attach_admin(self, company):
        """
        Crée un nouvel utilisateur (ou récupère l'existant) et le rattache à l'entreprise
        en tant qu'ADMIN. Fixe le rôle global COMPANY_ADMIN.
        """
        email = self.cleaned_data["email"].strip().lower()
        first_name = self.cleaned_data.get("first_name", "")
        last_name = self.cleaned_data.get("last_name", "")

        user, created = User.objects.get_or_create(email=email, defaults={
            "first_name": first_name,
            "last_name": last_name,
            "role": Roles.COMPANY_ADMIN,
            "is_active": True,
        })

        if created:
            user.set_password(self.cleaned_data["password1"])
            # s'assure que le rôle global est au bon niveau
            user.role = Roles.COMPANY_ADMIN
            user.save()

        # Si l'utilisateur existant n'a pas un rôle global suffisant, le promouvoir
        if not created and user.role not in (Roles.SUPERADMIN, Roles.COMPANY_ADMIN):
            user.role = Roles.COMPANY_ADMIN
            user.save(update_fields=["role"])

        # rattachement membership
        from companies.models import CompanyMembership, CompanyRole
        CompanyMembership.objects.get_or_create(
            user=user, company=company,
            defaults={"role": CompanyRole.ADMIN, "is_active": True}
        )
        return user, created
