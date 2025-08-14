from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import build_dashboard_context

class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(build_dashboard_context(self.request.user))
        return ctx