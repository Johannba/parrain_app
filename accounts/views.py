from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from companies.models import CompanyInvite, CompanyMembership, CompanyRole
from .forms import AcceptInviteForm
from .forms import EmailAuthenticationForm, SuperadminSetupForm
from .models import User, Roles

from django.shortcuts import render, redirect, get_object_or_404

class EmailLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class SuperadminSetupView(View):
    template_name = "accounts/superadmin_setup.html"

    def get(self, request):
        if User.objects.filter(role=Roles.SUPERADMIN).exists():
            messages.info(request, "Le Superadmin existe déjà. Connectez-vous.")
            return redirect("accounts:login")
        form = SuperadminSetupForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if User.objects.filter(role=Roles.SUPERADMIN).exists():
            messages.info(request, "Le Superadmin existe déjà. Connectez-vous.")
            return redirect("accounts:login")
        form = SuperadminSetupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Superadmin créé avec succès.")
            return redirect("dashboard:home")
        return render(request, self.template_name, {"form": form})
      
class AcceptInviteView(View):
    template_name = "accounts/accept_invite.html"

    def get(self, request, token):
        invite = get_object_or_404(CompanyInvite, token=token)
        if not invite.is_valid():
            messages.error(request, "Invitation invalide ou expirée.")
            return redirect("accounts:login")

        # si user existe déjà, pas besoin de form de création
        try:
            existing = User.objects.get(email=invite.email)
            ctx = {"invite": invite, "existing_user": existing}
            return render(request, self.template_name, ctx)
        except User.DoesNotExist:
            form = AcceptInviteForm(initial={"email": invite.email})
            return render(request, self.template_name, {"invite": invite, "form": form})

    def post(self, request, token):
        invite = get_object_or_404(CompanyInvite, token=token)
        if not invite.is_valid():
            messages.error(request, "Invitation invalide ou expirée.")
            return redirect("accounts:login")

        # Cas 1 : utilisateur existant se rattache
        if "accept_existing" in request.POST:
            user = User.objects.get(email=invite.email)
            CompanyMembership.objects.get_or_create(
                user=user, company=invite.company, defaults={"role": invite.role}
            )
            # lui donner le rôle global minimal (pas superadmin), si besoin
            if user.role == Roles.CLIENT:
                # si c'est un admin d'entreprise, on peut le promouvoir globalement
                if invite.role == CompanyRole.ADMIN:
                    user.role = Roles.COMPANY_ADMIN
                    user.save(update_fields=["role"])
                # sinon, on pourrait le laisser CLIENT (ou COMPANY_OPERATOR si tu préfères)
            invite.accepted = True
            invite.save(update_fields=["accepted"])
            messages.success(request, "Invitation acceptée. Vous pouvez vous connecter.")
            return redirect("accounts:login")

        # Cas 2 : création de compte
        form = AcceptInviteForm(request.POST, initial={"email": invite.email})
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            # rôle global par défaut en fonction de l’invitation
            user.role = Roles.COMPANY_ADMIN if invite.role == CompanyRole.ADMIN else Roles.COMPANY_OPERATOR
            user.is_active = True
            user.save()
            CompanyMembership.objects.create(
                user=user, company=invite.company, role=invite.role
            )
            invite.accepted = True
            invite.save(update_fields=["accepted"])
            login(request, user)
            messages.success(request, "Compte créé et invitation acceptée.")
            return redirect("dashboard:home")

        return render(request, self.template_name, {"invite": invite, "form": form})