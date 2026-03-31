HOST = "https://new.e-taxes.gov.az"

_ENDPOINTS: dict[str, str] = {
    # authentication
    "asan_start":           "/api/po/auth/public/v1/asanImza/start",
    "asan_status":          "/api/po/auth/public/v1/asanImza/status",
    "list_certificates":    "/api/po/auth/public/v1/asanImza/certificates",
    "choose_taxpayer":      "/api/po/auth/public/v1/asanImza/chooseTaxpayer",
    "logout":               "/api/po/auth/public/v1/legacyLogout",
    # invoices
    "invoice_list":         "/api/po/invoice/public/v2/invoice/{direction}",
    "invoice_detail":       "/api/po/invoice/public/v2/invoice/{id}?sourceSystem={source}",
    # portal (browser view — not an API call)
    "invoice_view":         "/eportal/az/invoice/view/",
    "declaration_list":     "/api/po/declaration/public/v1/declaration/list",
    "declaration_get":      "/api/po/declaration/public/v1/calc/UNIFIED_APPENDIX_1_EMPLOYEE_LIST"
}


def _url(name: str, **kwargs) -> str:
    """Return the full URL for a named endpoint, substituting any path variables."""
    path = _ENDPOINTS[name]
    return HOST + (path.format(**kwargs) if kwargs else path)
