from django.urls import path
from .views import CompanyCreateView, CompanyDetailView
from . import invite_views
from .admin_views import CompanyMembersView

urlpatterns = [
    path("create/", CompanyCreateView.as_view(), name="create"),
    path("<slug:slug>/", CompanyDetailView.as_view(), name="detail"),
    # Invitations Admin / Opérateur
    path("<slug:slug>/invite/", invite_views.InviteCreateView.as_view(), name="invite_create"),
    
    # Membres (liste + create Admin direct)
    path("<slug:slug>/members/", CompanyMembersView.as_view(), name="members"),
]
