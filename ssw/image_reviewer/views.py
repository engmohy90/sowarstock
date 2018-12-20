from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import loader
from notifications.signals import notify

from ssw import models
from ssw.views import getSowarStockUser, showCorrectMenu


@login_required
def products_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "image_reviewer":
        pending = models.Product.objects.filter(status="pending_approval")
        pending_admin = models.Product.objects.filter(status="pending_admin_approval")
        approved = models.Product.objects.filter(status="approved")
        rejected = models.Product.objects.filter(status="rejected")
        return render(request, "ssw/reviewer/products_main.html", {"user":user,"pending":pending,
                                                                "pending_admin":pending_admin, "approved":approved, "rejected": rejected,
                                                                "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_approve(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "image_reviewer":
        product = get_object_or_404(models.Product, pk=pk)
        product.status = "approved"
        product.reviewed_by = user
        product.save()
        email_body = loader.render_to_string("ssw/email_product_accept.html", {"product": product})
        send_mail("قبول عملك {}".format(product.public_id), "", "Sowarstock", [product.owner.email], False,
                  None, None, None, email_body)
        notify.send(user, recipient=product.owner, level="success",
                    verb='Product {} has been approved'.format(product.public_id))
        admin = models.SowarStockUser.objects.filter(type="admin")
        notify.send(request.user, recipient=admin, level="success",
                    verb='Product {} has been approved by {}'.format(product.public_id, user.get_full_name()))
        messages.success(request, "Product has been approved")
        return HttpResponseRedirect("/reviewer/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_reject(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "image_reviewer":
        if request.method == "POST":
            product = get_object_or_404(models.Product, pk=pk)
            rejection_reason = request.POST["rejection_reason"]
            rejection_note = request.POST["rejection_note"]
            product.status = "rejected"
            product.rejection_reason = rejection_reason
            product.rejection_note = rejection_note
            product.reviewed_by = user
            product.save()
            email_body = loader.render_to_string("ssw/email_product_reject.html", {"product": product})
            send_mail("رفض عملك {}".format(product.public_id), "", "Sowarstock", [product.owner.email], False,
                      None, None, None, email_body)
            notify.send(request.user, recipient=product.owner, level="error",
                        verb='Product {} has been rejected for the following reason: {}, {}'.format(
                            product.public_id,
                            product.get_rejection_reason_display(),
                            product.rejection_note))
            admin = models.SowarStockUser.objects.filter(type="admin")
            notify.send(request.user, recipient=admin, level="success",
                        verb='Product {} has been rejected by {} for the following reason: {}, {}'.format(
                            product.public_id, user.get_full_name(), product.get_rejection_reason_display(), product.rejection_note))
            messages.success(request, "Product has been rejected")
            return HttpResponseRedirect("/reviewer/products")
        return HttpResponseRedirect("/reviewer/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

