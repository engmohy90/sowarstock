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
    pending_admin = models.Product.objects.filter(status='pending_admin_approval')
    approved = models.Product.objects.filter(status="approved")
    rejected = models.Product.objects.filter(status="rejected")
    return render(request, "ssw/admin/products_main.html", {"user":getSowarStockUser(request.user),"pending":pending,
                                                            "pending_admin":pending_admin, "approved":approved, "rejected": rejected,
                                                            "showadminmenu": True, "activeDashboardMenu": "products"})

@login_required
def product_approve(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    product.status = "approved"
    product.save()
    notify.send(request.user, recipient=product.owner, level="success",
                verb='Product {} has been approved'.format(product.public_id))
    messages.success(request, "Product has been approved")
    return HttpResponseRedirect("/admin/products")

@login_required
def product_reject(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    product.status = "rejected"
    product.save()
    notify.send(request.user, recipient=product.owner, level="error",
                verb='Product {} has been rejected'.format(product.public_id))
    messages.success(request, "Product has been rejected")
    return HttpResponseRedirect("/admin/products")

@login_required
def faqs_main(request):
    faqs = models.Faq.objects.all()
    personal_faqs = models.FaqPersonal.objects.all()
    return render(request, "ssw/admin/faqs_main.html", {"user":getSowarStockUser(request.user), "faqs": faqs, "personal_faqs": personal_faqs,
                                                        "showadminmenu": True, "activeDashboardMenu": "faqs"})
@login_required
def faqs_new(request):
    form = forms.FaqForm()
    if request.method == "POST":
        form = forms.FaqForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ has been added")
        else:
            messages.error(request, "An error has occured")
        return HttpResponseRedirect("/admin/faqs")
    return render(request, "ssw/admin/faqs_new.html", {"user":getSowarStockUser(request.user), "form": form,
                                                       "showadminmenu": True, "activeDashboardMenu": "faqs"})

@login_required
def faqs_edit(request,pk):
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
                                                       "showadminmenu": True,"activeDashboardMenu": "faqs"})

@login_required
def faqs_delete(request,pk):
    faq = get_object_or_404(models.Faq, pk=pk)
    faq.delete()
    messages.success(request, "FAQ has been deleted")
    return HttpResponseRedirect("/admin/faqs")

@login_required
def personal_faqs_reply(request,pk):
    if request.method == "POST":
        faq = get_object_or_404(models.FaqPersonal, pk=pk)
        user = get_object_or_404(models.SowarStockUser, pk=request.user.pk)
        answer = request.POST['answer']
        faq.answer = answer
        faq.replier = user
        faq.save()
        messages.success(request, "FAQ has been answered")
    return HttpResponseRedirect("/admin/faqs")

@login_required
def requests_main(request):
    pending = models.UserRequest.objects.filter(status="pending_approval")
    approved = models.UserRequest.objects.filter(status="approved")
    rejected = models.UserRequest.objects.filter(status="rejected")
    return render(request, "ssw/admin/requests_main.html", {"user":getSowarStockUser(request.user),
                                                            "pending": pending, "approved": approved, "rejected": rejected,
                                                            "showadminmenu": True,"activeDashboardMenu": "requests"})

@login_required
def requests_approve(request,pk):
    r = get_object_or_404(models.UserRequest, pk = pk)
    r.status = "approved"
    r.save()
    r.owner.photo_id_verified = True
    r.owner.save()
    notify.send(request.user, recipient=r.owner, level="success",
                verb='Photo ID has been verified')
    messages.success(request, "Request has been approved")
    return HttpResponseRedirect("/admin/requests")

@login_required
def requests_reject(request,pk):
    r = get_object_or_404(models.UserRequest, pk=pk)
    r.status = "rejected"
    r.save()
    r.owner.photo_id = None
    r.owner.save()
    notify.send(request.user, recipient=r.owner, level="error",
                verb='Photo ID has been rejected')
    messages.success(request, "Request has been rejected")
    return HttpResponseRedirect("/admin/requests")

@login_required
def reviews_main(request):
    reviews = models.Review.objects.all()
    return render(request, "ssw/admin/reviews_main.html", {"user":getSowarStockUser(request.user), "reviews": reviews,
                                                      "showadminmenu": True, "activeDashboardMenu": "reviews"})

@login_required
def reviews_delete(request,pk):
    review = get_object_or_404(models.Review, pk=pk)
    review.delete()
    messages.success(request, "Review has been deleted")
    return HttpResponseRedirect("/admin/reviews")

@login_required
def notifications_main(request):
    form = forms.NotificationForm()
    if request.method == "POST":
        recipients = request.POST.getlist("recipient")
        level = request.POST["level"]
        verb = request.POST["verb"]
        print(recipients)
        for r in recipients:
            user = get_object_or_404(models.SowarStockUser, pk=r)
            notify.send(request.user, recipient = user, level = level, verb = verb)
            messages.success(request, "Notification sent")
            return HttpResponseRedirect("/admin/notices")
    return render(request, "ssw/admin/notifications_main.html", {"user":getSowarStockUser(request.user), "form": form,
                                                                 "showadminmenu": True, "activeDashboardMenu": "notifications"})

@login_required
def categories_main(request):
    categories = models.Category.objects.all()
    subcategories = models.SubCategory.objects.all()
    return render(request, "ssw/admin/categories_main.html", {"user":getSowarStockUser(request.user), "categories": categories, "subcategories": subcategories,
                                                              "showadminmenu": True,"activeDashboardMenu": "categories"})

@login_required
def categories_new(request):
    form = forms.CategoryForm()
    if request.method == "POST":
        form = forms.CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New category added")
        else:
            messages.error(request, "An error has occurred")
        return HttpResponseRedirect("/admin/categories")
    return render(request, "ssw/admin/categories_new.html", {"user":getSowarStockUser(request.user), "form": form,
                                                             "showadminmenu": True, "activeDashboardMenu": "categories"})
@login_required
def categories_edit(request, pk):
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
    return render(request, "ssw/admin/categories_new.html", {"user":getSowarStockUser(request.user), "form": form, "category" : category,
                                                             "showadminmenu": True, "activeDashboardMenu": "categories"})

@login_required
def categories_delete(request,pk):
    category = get_object_or_404(models.Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted")
    return HttpResponseRedirect("/admin/categories")

@login_required
def subcategories_new(request):
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
                                                             "showadminmenu": True,"activeDashboardMenu": "categories"})

@login_required
def subcategories_edit(request, pk):
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
    return render(request, "ssw/admin/subcategories_new.html", {"user":getSowarStockUser(request.user), "form": form, "subcategory" : subcategory,
                                                             "showadminmenu": True, "activeDashboardMenu": "categories"})

@login_required
def subcategories_delete(request,pk):
    subcategory = get_object_or_404(models.SubCategory, pk=pk)
    subcategory.delete()
    messages.success(request, "Subcategory deleted")
    return HttpResponseRedirect("/admin/categories")

@login_required
def legal_main(request):
    documents = models.LegalDocument.objects.all()
    return render(request, "ssw/admin/legal_main.html", {"user":getSowarStockUser(request.user),"documents":documents,
                                                         "showadminmenu": True, "activeDashboardMenu": "legal"})

@login_required
def legal_edit(request, pk):
    document = get_object_or_404(models.LegalDocument, pk=pk)
    form = forms.LegalDocumentForm(instance=document)
    if request.method == "POST":
        form = forms.LegalDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "document updated")
            return HttpResponseRedirect("/admin/legal")
    return render(request, "ssw/admin/legal_edit.html", {"user":getSowarStockUser(request.user), "document": document, "form": form,
                                                         "showadminmenu": True, "activeDashboardMenu": "legal"})