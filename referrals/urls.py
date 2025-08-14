from django.urls import path
from .views import ReferralsHomeView

app_name = "referrals"

urlpatterns = [
    path("", ReferralsHomeView.as_view(), name="home"),
    path("parrains/", ReferralsHomeView.as_view(), name="parrains_list"),   # ← ajouté
    path("parraines/", ReferralsHomeView.as_view(), name="parraine_list"),  # ← ajouté
]
