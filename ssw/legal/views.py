from django.shortcuts import render, get_object_or_404

from ssw import models, forms
from ssw.views import getSowarStockUser

def contributor(request):
    document = get_object_or_404(models.LegalDocument, title="Contributor Agreement")
    return render(request, "ssw/legal/contributor.html", {"user": getSowarStockUser(request.user), "document": document,
                                                          "activeDashboardMenu": "legal_contributor"})

def license(request):
    document = get_object_or_404(models.LegalDocument, title="License Agreement")
    return render(request, "ssw/legal/license.html",
                  {"user": getSowarStockUser(request.user), "document": document,
                   "activeDashboardMenu": "legal_license"})

def privacy(request):
    document = get_object_or_404(models.LegalDocument, title="Privacy Policy")
    return render(request, "ssw/legal/privacy.html",
                  {"user": getSowarStockUser(request.user), "document": document,
                   "activeDashboardMenu": "legal_privacy"})

def terms(request):
    document = get_object_or_404(models.LegalDocument, title="Terms and Conditions")
    return render(request, "ssw/legal/terms.html",
                  {"user": getSowarStockUser(request.user),"document": document,
                   "activeDashboardMenu": "legal_terms"})