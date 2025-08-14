from django.urls import path
from django.contrib.auth import views as auth_views
from .views import EmailLoginView, SuperadminSetupView, AcceptInviteView


app_name = "accounts"

urlpatterns = [
    path("setup-superadmin/", SuperadminSetupView.as_view(), name="setup_superadmin"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accept-invite/<uuid:token>/", AcceptInviteView.as_view(), name="accept_invite"),
]
