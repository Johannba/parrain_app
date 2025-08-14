from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse
from core.permissions import SuperadminRequiredMixin
from .forms import CompanyForm
from .models import Company

class CompanyCreateView(SuperadminRequiredMixin, View):
    template_name = "companies/company_create.html"

    def get(self, request):
        return render(request, self.template_name, {"form": CompanyForm()})

    def post(self, request):
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, "Entreprise créée.")
            return redirect("companies:detail", slug=company.slug)
        return render(request, self.template_name, {"form": form})

class CompanyDetailView(SuperadminRequiredMixin, View):
    template_name = "companies/company_detail.html"

    def get(self, request, slug):
        company = get_object_or_404(Company, slug=slug)
        return render(request, self.template_name, {"company": company})
