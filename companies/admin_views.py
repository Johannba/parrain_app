from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from core.permissions import SuperadminRequiredMixin
from .models import Company, CompanyMembership, CompanyRole
from .admin_forms import CompanyAdminCreateForm

class CompanyMembersView(SuperadminRequiredMixin, View):
    template_name = "companies/company_members.html"

    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        members = CompanyMembership.objects.select_related("user").filter(company=company).order_by("-role", "user__email")
        form = CompanyAdminCreateForm()
        return render(request, self.template_name, {"company": company, "members": members, "form": form})

    def post(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        form = CompanyAdminCreateForm(request.POST)
        members = CompanyMembership.objects.select_related("user").filter(company=company).order_by("-role", "user__email")

        if form.is_valid():
            user, created = form.create_or_attach_admin(company)
            if created:
                messages.success(request, f"Admin créé et rattaché : {user.email}")
            else:
                messages.success(request, f"Utilisateur existant rattaché comme Admin : {user.email}")
            return redirect("companies:members", slug=company.slug)

        # erreurs de formulaire
        return render(request, self.template_name, {"company": company, "members": members, "form": form})
