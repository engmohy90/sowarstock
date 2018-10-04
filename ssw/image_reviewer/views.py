from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from notifications.signals import notify

from ssw import models, forms
from ssw.views import getSowarStockUser

@login_required
def users(request):
    users = models.SowarStockUser.objects.all()
    return render(request, "ssw/admin/users.html", {"user":getSowarStockUser(request.user), "users":users,
                                                    "showadminmenu": True, "activeDashboardMenu":"users"})

@login_required
def products_main(request):
    pending = models.Product.objects.filter(status="pending_approval")
    pending_admin = models.Product.objects.filter(status="pending_admin_approval")
    approved = models.Product.objects.filter(status="approved")
    rejected = models.Product.objects.filter(status="rejected")
    return render(request, "ssw/reviewer/products_main.html", {"user":getSowarStockUser(request.user),"pending":pending,
                                                            "pending_admin":pending_admin, "approved":approved, "rejected": rejected,
                                                            "showadminmenu": True, "activeDashboardMenu": "products"})

@login_required
def product_approve(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    product.status = "pending_admin_approval"
    product.save()
    messages.success(request, "Product has been approved by you and now waiting admin approval")
    return HttpResponseRedirect("/reviewer/products")

@login_required
def product_reject(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    product.status = "rejected"
    product.save()
    notify.send(request.user, recipient=product.owner, level="error",
                verb='Product {} has been rejected'.format(product.public_id))
    messages.success(request, "Product has been rejected")
    return HttpResponseRedirect("/reviwer/products")