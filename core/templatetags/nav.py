from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, namespace_prefix):
    """
    Retourne 'active' si le namespace courant commence par namespace_prefix.
    Usage: class="nav-link {% active 'dashboard' %}"
    """
    req = context.get("request")
    if not req or not getattr(req, "resolver_match", None):
        return ""
    current_ns = req.resolver_match.namespace or ""
    return "active" if current_ns.startswith(namespace_prefix) else ""
