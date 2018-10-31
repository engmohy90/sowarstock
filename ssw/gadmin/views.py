from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import loader
from notifications.signals import notify

from ssw import models, forms
from ssw.views import getSowarStockUser, showCorrectMenu


@login_required
def users(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        users = models.SowarStockUser.objects.all()
        return render(request, "ssw/admin/users.html", {"user": user, "users": users,
                                                        "activeDashboardMenu": "users", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def products_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        pending = models.Product.objects.filter(status="pending_approval")
        pending_admin = models.Product.objects.filter(status='pending_admin_approval')
        approved = models.Product.objects.filter(status="approved")
        rejected = models.Product.objects.filter(status="rejected")
        return render(request, "ssw/admin/products_main.html", {"user":user,"pending":pending, "pending_admin":pending_admin,
                                                                "approved":approved, "rejected": rejected,
                                                                "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def product_approve(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        product = get_object_or_404(models.Product, pk=pk)
        product.status = "approved"
        product.save()
        email_body = loader.render_to_string("ssw/email_product_accept.html", {"product": product})
        send_mail("قبول عملك {}".format(product.public_id), "", "Sowar Stock", [product.owner.email], False,
                  None, None, None, email_body)
        notify.send(request.user, recipient=product.owner, level="success",
                    verb='Product {} has been approved'.format(product.public_id))
        messages.success(request, "Product has been approved")
        return HttpResponseRedirect("/admin/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_reject(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        if request.method == "POST":
            product = get_object_or_404(models.Product, pk=pk)
            rejection_reason = request.POST["rejection_reason"]
            rejection_note = request.POST["rejection_note"]
            product.status = "rejected"
            product.rejection_reason = rejection_reason
            product.rejection_note = rejection_note
            product.save()
            email_body = loader.render_to_string("ssw/email_product_reject.html", {"product": product})
            send_mail("رفض عملك {}".format(product.public_id), "", "Sowar Stock", [product.owner.email], False,
                      None, None, None, email_body)
            notify.send(request.user, recipient=product.owner, level="error",
                        verb='Product {} has been rejected'.format(product.public_id))
            messages.success(request, "Product has been rejected")
            return HttpResponseRedirect("/admin/products")
        return HttpResponseRedirect("/admin/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def faqs_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        faqs = models.Faq.objects.all()
        personal_faqs = models.FaqPersonal.objects.all()
        return render(request, "ssw/admin/faqs_main.html", {"user":user, "faqs": faqs, "personal_faqs": personal_faqs,
                                                            "activeDashboardMenu": "faqs", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def faqs_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.FaqForm()
        if request.method == "POST":
            form = forms.FaqForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "FAQ has been added")
            else:
                messages.error(request, "An error has occured")
            return HttpResponseRedirect("/admin/faqs")
        return render(request, "ssw/admin/faqs_new.html", {"user": user, "form": form, "activeDashboardMenu": "faqs",
                                                           **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def faqs_edit(request,pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        faq = get_object_or_404(models.Faq, pk=pk)
        form = forms.FaqForm(instance=faq)
        if request.method == "POST":
            form = forms.FaqForm(request.POST, instance=faq)
            if form.is_valid():
                form.save()
                messages.success(request, "FAQ has been edit")
            else:
                messages.error(request, "FAQ has been added")
            return HttpResponseRedirect("/admin/faqs")
        return render(request, "ssw/admin/faqs_new.html", {"user":getSowarStockUser(request.user), "faq":faq, "form": form,
                                                           "activeDashboardMenu": "faqs", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def faqs_delete(request,pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        faq = get_object_or_404(models.Faq, pk=pk)
        faq.delete()
        messages.success(request, "FAQ has been deleted")
        return HttpResponseRedirect("/admin/faqs")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def personal_faqs_reply(request,pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        if request.method == "POST":
            faq = get_object_or_404(models.FaqPersonal, pk=pk)
            user = get_object_or_404(models.SowarStockUser, pk=request.user.pk)
            answer = request.POST['answer']
            faq.answer = answer
            faq.replier = user
            faq.save()
            messages.success(request, "FAQ has been answered")
        return HttpResponseRedirect("/admin/faqs")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def requests_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        pending = models.UserRequest.objects.filter(status="pending_approval")
        approved = models.UserRequest.objects.filter(status="approved")
        rejected = models.UserRequest.objects.filter(status="rejected")
        return render(request, "ssw/admin/requests_main.html", {"user": user, "pending": pending, "approved": approved,
                                                                "rejected": rejected, "activeDashboardMenu": "requests",
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def requests_approve(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        r = get_object_or_404(models.UserRequest, pk = pk)
        r.status = "approved"
        r.save()
        r.owner.photo_id_verified = True
        r.owner.save()
        notify.send(request.user, recipient=r.owner, level="success",
                    verb='Photo ID has been verified')
        messages.success(request, "Request has been approved")
        return HttpResponseRedirect("/admin/requests")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def requests_reject(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        r = get_object_or_404(models.UserRequest, pk=pk)
        r.status = "rejected"
        r.save()
        r.owner.photo_id = None
        r.owner.save()
        notify.send(request.user, recipient=r.owner, level="error",
                    verb='Photo ID has been rejected')
        messages.success(request, "Request has been rejected")
        return HttpResponseRedirect("/admin/requests")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def reviews_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        reviews = models.Review.objects.all()
        return render(request, "ssw/admin/reviews_main.html", {"user": user, "reviews": reviews,
                                                      "activeDashboardMenu": "reviews", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def reviews_delete(request,pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        review = get_object_or_404(models.Review, pk=pk)
        review.delete()
        messages.success(request, "Review has been deleted")
        return HttpResponseRedirect("/admin/reviews")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def notifications_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.NotificationForm()
        if request.method == "POST":
            recipients = request.POST.getlist("recipient")
            level = request.POST["level"]
            verb = request.POST["verb"]
            for r in recipients:
                user = get_object_or_404(models.SowarStockUser, pk=r)
                notify.send(request.user, recipient = user, level = level, verb = verb)
                messages.success(request, "Notification sent")
                return HttpResponseRedirect("/admin/notices")
        return render(request, "ssw/admin/notifications_main.html", {"user": user, "form": form,
                                                                     "activeDashboardMenu": "notifications",
                                                                     **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def categories_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        categories = models.Category.objects.all()
        subcategories = models.SubCategory.objects.all()
        return render(request, "ssw/admin/categories_main.html", {"user": user, "categories": categories, "subcategories": subcategories,
                                                                  "activeDashboardMenu": "categories", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def categories_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.CategoryForm()
        if request.method == "POST":
            form = forms.CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "New category added")
            else:
                messages.error(request, "An error has occurred")
            return HttpResponseRedirect("/admin/categories")
        return render(request, "ssw/admin/categories_new.html", {"user":user, "form": form,
                                                                 "activeDashboardMenu": "categories", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def categories_edit(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        category = get_object_or_404(models.Category, pk=pk)
        form = forms.CategoryForm(instance=category)
        if request.method == "POST":
            form = forms.CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, "Category updated")
            else:
                messages.error(request, "An error has occurred")
            return HttpResponseRedirect("/admin/categories")
        return render(request, "ssw/admin/categories_new.html", {"user": user, "form": form, "category": category,
                                                                 "activeDashboardMenu": "categories", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def categories_delete(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        category = get_object_or_404(models.Category, pk=pk)
        category.delete()
        messages.success(request, "Category deleted")
        return HttpResponseRedirect("/admin/categories")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def subcategories_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.SubcategoryForm()
        if request.method == "POST":
            form = forms.SubcategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Subcategory updated")
            else:
                messages.error(request, "An error has occurred")
            return HttpResponseRedirect("/admin/categories")
        return render(request, "ssw/admin/subcategories_new.html", {"user": getSowarStockUser(request.user), "form": form,
                                                                 "activeDashboardMenu": "categories", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def subcategories_edit(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        subcategory = get_object_or_404(models.SubCategory, pk=pk)
        form = forms.SubcategoryForm(instance=subcategory)
        if request.method == "POST":
            form = forms.SubcategoryForm(request.POST, instance=subcategory)
            if form.is_valid():
                form.save()
                messages.success(request, "Subcategory updated")
            else:
                messages.error(request, "An error has occurred")
            return HttpResponseRedirect("/admin/categories")
        return render(request, "ssw/admin/subcategories_new.html", {"user":user, "form": form, "subcategory" : subcategory,
                                                                 "activeDashboardMenu": "categories", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def subcategories_delete(request,pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        subcategory = get_object_or_404(models.SubCategory, pk=pk)
        subcategory.delete()
        messages.success(request, "Subcategory deleted")
        return HttpResponseRedirect("/admin/categories")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def legal_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        documents = models.LegalDocument.objects.all()
        return render(request, "ssw/admin/legal_main.html", {"user":user,"documents":documents,
                                                         "activeDashboardMenu": "legal", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def legal_edit(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        document = get_object_or_404(models.LegalDocument, pk=pk)
        form = forms.LegalDocumentForm(instance=document)
        if request.method == "POST":
            form = forms.LegalDocumentForm(request.POST, request.FILES, instance=document)
            if form.is_valid():
                form.save()
                messages.success(request, "document updated")
                return HttpResponseRedirect("/admin/legal")
        return render(request, "ssw/admin/legal_edit.html", {"user": user, "document": document, "form": form,
                                                             "activeDashboardMenu": "legal", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def orders_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        orders = models.Order.objects.all()
        return render(request, "ssw/admin/orders_main.html", {"user": user, "orders": orders, **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def featured_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        slider_images = models.Featured.objects.filter(type="slider")
        contributors = models.Featured.objects.filter(type="contributors")
        featured_products = models.Featured.objects.filter(type="featured")
        return render(request, "ssw/admin/featured_main.html", {"user": user, "slider_images": slider_images,
                                                                "contributors": contributors, "featured_products": featured_products,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_slider_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.FeaturedSliderForm()
        if request.method == "POST":
            form = forms.FeaturedSliderForm(request.POST, request.FILES)
            if form.is_valid():
                featured = form.save(False)
                featured.type = "slider"
                featured.save()
                return HttpResponseRedirect("/admin/featured")
            else:
                messages.error(request, "An error has occurred")
        return render(request, "ssw/admin/featured_slider_new.html", {"user": user, "form": form,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_contributor_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.FeaturedContributorForm()
        if request.method == "POST":
            form = forms.FeaturedContributorForm(request.POST)
            if form.is_valid():
                featured = form.save(False)
                featured.type = "contributors"
                featured.save()
                return HttpResponseRedirect("/admin/featured")
            else:
                messages.error(request, "An error has occurred")
        return render(request, "ssw/admin/featured_contributor_new.html", {"user": user, "form": form,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_product_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.FeaturedProductForm()
        if request.method == "POST":
            form = forms.FeaturedProductForm(request.POST)
            if form.is_valid():
                featured = form.save(False)
                featured.type = "featured"
                featured.save()
                return HttpResponseRedirect("/admin/featured")
            else:
                messages.error(request, "An error has occurred")
        return render(request, "ssw/admin/featured_product_new.html", {"user": user, "form": form,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_slider_delete(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        featured = get_object_or_404(models.Featured, pk=pk)
        featured.image.delete_thumbnails()
        featured.image.delete(False)
        featured.delete()
        messages.success(request, "image has been deleted")
        return HttpResponseRedirect("/admin/featured")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_contributor_delete(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        featured = get_object_or_404(models.Featured, pk=pk)
        featured.delete()
        messages.success(request, "contributor has been deleted")
        return HttpResponseRedirect("/admin/featured")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_product_delete(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        featured = get_object_or_404(models.Featured, pk=pk)
        featured.delete()
        messages.success(request, "product has been deleted")
        return HttpResponseRedirect("/admin/featured")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")
