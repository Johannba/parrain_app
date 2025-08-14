from dataclasses import dataclass
from typing import Dict, Any
from accounts.models import Roles, User
from companies.models import Company, CompanyMembership, CompanyRole

@dataclass
class DashboardMetrics:
    total_companies: int = 0
    total_admins: int = 0
    total_operators: int = 0
    total_parrains: int = 0
    total_filleuls: int = 0
    total_rewards: int = 0

def _metrics_superadmin() -> DashboardMetrics:
    return DashboardMetrics(
        total_companies=Company.objects.count(),
        total_admins=CompanyMembership.objects.filter(role=CompanyRole.ADMIN).count(),
        total_operators=CompanyMembership.objects.filter(role=CompanyRole.OPERATOR).count(),
        # placeholders: on branchera sur referrals.* plus tard
        total_parrains=0,
        total_filleuls=0,
        total_rewards=0,
    )

def _metrics_for_company(company: Company) -> DashboardMetrics:
    return DashboardMetrics(
        total_companies=1,
        total_admins=company.memberships.filter(role=CompanyRole.ADMIN).count(),
        total_operators=company.memberships.filter(role=CompanyRole.OPERATOR).count(),
        total_parrains=0,
        total_filleuls=0,
        total_rewards=0,
    )

def get_user_current_company(user: User) -> Company | None:
    """
    Heuristique simple : si l'utilisateur n'est pas superadmin et a une seule entreprise,
    on considère que c'est l'entreprise 'courante' pour le dashboard.
    Ensuite on pourra ajouter un sélecteur si multi-entreprises.
    """
    if user.role == Roles.SUPERADMIN:
        return None
    qs = Company.objects.filter(memberships__user=user).distinct()
    if qs.count() == 1:
        return qs.first()
    return None

def build_dashboard_context(user: User) -> Dict[str, Any]:
    company = get_user_current_company(user)
    if user.role == Roles.SUPERADMIN or company is None:
        metrics = _metrics_superadmin()
        companies = Company.objects.all().order_by("name")[:8]
    else:
        metrics = _metrics_for_company(company)
        companies = [company]
    return {
        "metrics": metrics,
        "companies": companies,
        "current_company": company,
        "is_superadmin": user.role == Roles.SUPERADMIN,
    }
