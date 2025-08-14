from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.utils import timezone
from core.permissions import SuperadminRequiredMixin
from .models import Company, CompanyInvite
from .invite_forms import InviteForm

class InviteCreateView(SuperadminRequiredMixin, View):
    template_name = "companies/invite_create.html"

    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        form = InviteForm()
        return render(request, self.template_name, {"company": company, "form": form})

    def post(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        form = InviteForm(request.POST)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.company = company
            invite.invited_by = request.user
            invite.expires_at = timezone.now() + timezone.timedelta(days=7)
            invite.save()
            link = request.build_absolute_uri(
                reverse("accounts:accept_invite", args=[str(invite.token)])
            )
            messages.success(request, "Invitation créée.")
            # On affiche le lien dans la page (copiable pour l’instant)
            return render(request, self.template_name, {
                "company": company, "form": InviteForm(), "invite_link": link
            })
        return render(request, self.template_name, {"company": company, "form": form})
