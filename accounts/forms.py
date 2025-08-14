from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Roles
from django import forms




class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))


class SuperadminSetupForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean(self):
        cleaned = super().clean()
        if User.objects.filter(role=Roles.SUPERADMIN).exists():
            raise forms.ValidationError("Un Superadmin existe déjà. Connectez-vous.")
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = Roles.SUPERADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AcceptInviteForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)
        widgets = {"email": forms.EmailInput(attrs={"readonly": "readonly"})}

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        return cleaned
      
