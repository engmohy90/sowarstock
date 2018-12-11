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
def suspend_account(request, username):
    user = getSowarStockUser(request.user)
    account = get_object_or_404(models.SowarStockUser, username=username)
    if user.type == "admin":
        if request.method == "POST":
            suspension_reason = request.POST["suspension_reason"]
            account.suspended = True
            account.suspension_reason = suspension_reason
            account.save()
            # send email
            email_body = loader.render_to_string("ssw/email_suspend_account.html", {"user": account})
            send_mail("إيقاف حسابك", "", "Sowarstock", [account.email], False,
                      None, None, None, email_body)
            messages.success(request, "Account suspended")
        return HttpResponseRedirect("/admin/users")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def unsuspend_account(request,username):
    user = getSowarStockUser(request.user)
    account = get_object_or_404(models.SowarStockUser, username=username)
    if user.type == "admin":
        account.suspended = False
        account.suspension_reason = None
        account.save()
        messages.success(request, "Account un-suspended")
        return HttpResponseRedirect("/admin/users")
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
        requested_to_archive = models.Product.objects.filter(requested_to_archive=True)
        archived = models.Product.objects.filter(status="archived")
        return render(request, "ssw/admin/products_main.html", {"user":user,"pending":pending, "pending_admin":pending_admin,
                                                                "approved":approved, "rejected": rejected,
                                                                "requested_to_archive": requested_to_archive, "archived": archived,
                                                                "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def product_approve(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        product = get_object_or_404(models.Product, pk=pk)
        product.status = "pending_approval"
        product.save()
        messages.success(request, "Product has been approved by you and now waiting reviewer approval")
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
            send_mail("رفض عملك {}".format(product.public_id), "", "Sowarstock", [product.owner.email], False,
                      None, None, None, email_body)
            notify.send(request.user, recipient=product.owner, level="error",
                        verb='Product {} has been rejected for the following reason: {}, {}'.format(product.public_id,
                                                                                                    rejection_reason,
                                                                                                    rejection_note))
            messages.success(request, "Product has been rejected")
            return HttpResponseRedirect("/admin/products")
        return HttpResponseRedirect("/admin/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_archive(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        product = get_object_or_404(models.Product, pk=pk)
        product.status = "archived"
        product.requested_to_archive = False
        product.save()
        messages.success(request, "Product has been archived")
        return HttpResponseRedirect("/admin/products")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def collections_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        collections = models.Collection.objects.all()
        return render(request, "ssw/admin/collections_main.html", {"user":getSowarStockUser(request.user), "collections": collections,
                                                  "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def collections_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        products = models.Product.objects.filter(status="approved")
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["description"]
            products = request.POST.getlist("products")
            if title == "":
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/admin/collections/new")
            if description == "":
                messages.error(request, "Please choose a description for your collection")
                return HttpResponseRedirect("/admin/collections/new")
            if not products:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/admin/collections/new")
            collection = models.Collection.objects.create(title=title, description=description, owner=user)
            for product in products:
                p = get_object_or_404(models.Product, pk=product)
                collection.products.add(p)
            collection.save()
            messages.success(request, "Collection created successfully")
            return HttpResponseRedirect("/admin/collections")
        return render(request, "ssw/admin/collections_new.html", {"user":getSowarStockUser(request.user), "products": products,
                                                      "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def collections_edit(request,pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        if user == collection.owner:
            products = models.Product.objects.filter(status="approved")
        else:
            products = models.Product.objects.filter(owner=collection.owner, status="approved")
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["description"]
            products_pks = request.POST.getlist("products")
            if title == "":
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/admin/collections/{}/edit".format(collection.pk))
            if description == "":
                messages.error(request, "Please choose a description for your collection")
                return HttpResponseRedirect("/admin/collections/{}/edit".format(collection.pk))
            if not products_pks:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/admin/collections/{}/edit".format(collection.pk))
            collection.title = title
            collection.description = description
            collection.products.clear()
            for product in products_pks:
                p = get_object_or_404(models.Product, pk=product)
                collection.products.add(p)
            collection.save()
            messages.success(request, "Collection updated successfully")
            return HttpResponseRedirect("/admin/collections")
        return render(request, "ssw/admin/collections_new.html", {"user": getSowarStockUser(request.user), "products": products, "collection": collection,
                                                            "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def collections_delete(request, pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        collection.delete()
        messages.success(request,"Collection deleted")
        return HttpResponseRedirect("/admin/collections")
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
def requests_profile(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        r = get_object_or_404(models.UserRequest, pk=pk)
        sample_products = models.SampleProduct.objects.filter(owner=r.owner)
        return render(request, "ssw/admin/requests_profile.html", {"user": user, "r": r, "sample_products": sample_products,
                                                                   "activeDashboardMenu": "requests",
                                                                   **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def requests_approve(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        r = get_object_or_404(models.UserRequest, pk=pk)
        r.status = "approved"
        r.save()
        if r.type == "new_contributor":
            r.owner.photo_id_verified = True
            r.owner.save()
            notify.send(request.user, recipient=r.owner, level="success",
                        verb='Your account has been verified')
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
        if r.type == "new_contributor":
            r.owner.photo_id = None
            r.owner.save()
            notify.send(request.user, recipient=r.owner, level="error",
                        verb='You request to verify your account has been rejected')
        else:
            notify.send(request.user, recipient=r.owner, level="error",
                        verb='Your request to delete your account has been rejected')
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
        notifications = request.user.notifications.all()
        return render(request, "ssw/admin/notifications_main.html", {"user": user, "notifications": notifications,
                                                                     "activeDashboardMenu": "notifications",
                                                                     **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def notifications_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.NotificationForm()
        if request.method == "POST":
            recipients_type = request.POST.getlist("recipients")[0]
            if recipients_type == "contributors":
                recipients = models.SowarStockUser.objects.filter(type="contributor")
            elif recipients_type == "clients":
                recipients = models.SowarStockUser.objects.filter(type="client")
            else:
                recipients = request.POST.getlist("recipient")
            level = request.POST["level"]
            verb = request.POST["verb"]
            for r in recipients:
                user = get_object_or_404(models.SowarStockUser, pk=r)
                notify.send(request.user, recipient=user, level=level, verb=verb)
            messages.success(request, "Notification sent")
            return HttpResponseRedirect("/admin/notices")
        return render(request, "ssw/admin/notifications_new.html", {"user": user, "form": form,
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
        return render(request, "ssw/admin/orders_main.html", {"user": user, "orders": orders,
                                                              "activeDashboardMenu": "orders", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def order_details(request, order_no):
    order = get_object_or_404(models.Order, order_no=order_no)
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        return render(request, "ssw/admin/order_details.html", {"user": getSowarStockUser(request.user), "order": order,
                                                      "activeDashboardMenu": "orders", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        contributors = models.Contributor.objects.filter(featured=True)
        products = models.Product.objects.filter(featured=True)
        return render(request, "ssw/admin/featured_main.html", {"user": user, "contributors": contributors,
                                                                "products": products, "activeDashboardMenu": "featured",
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_contributor_edit(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        contributors = models.Contributor.objects.all()
        if request.method == "POST":
            for contributor in contributors:
                contributor.featured = False
                contributor.save()
            cs = request.POST.getlist("contributors")
            if cs:
                for contributor in cs:
                    c = get_object_or_404(models.Contributor, pk=contributor)
                    c.featured = True
                    c.save()
            messages.success(request, "Featured contributors list updated successfully")
            return HttpResponseRedirect("/admin/featured")
        return render(request, "ssw/admin/featured_contributor_edit.html", {"user": user, "contributors": contributors,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def featured_product_edit(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        products = models.Product.objects.filter(status="approved")
        if request.method == "POST":
            for product in products:
                product.featured = False
                product.save()
            ps = request.POST.getlist("products")
            if ps:
                for product in ps:
                    p = get_object_or_404(models.Product, pk=product)
                    p.featured = True
                    p.save()
            messages.success(request, "Featured products list updated successfully")
            return HttpResponseRedirect("/admin/featured")
        return render(request, "ssw/admin/featured_product_edit.html", {"user": user, "products": products,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def earnings_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        searnings = models.Earning.objects.filter(type="sowarstock")
        cearnings = models.Earning.objects.filter(type="contributor")
        return render(request, "ssw/admin/earnings_main.html", {"user": user, "searnings": searnings,
                                                                "cearnings": cearnings, "activeDashboardMenu": "earnings",
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def payment_new(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        earning = get_object_or_404(models.Earning, pk=pk)
        form = forms.PaymentForm()
        if request.method == "POST":
            form = forms.PaymentForm(request.POST, request.FILES)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.amount = earning.amount
                payment.earning = earning
                payment.save()
                messages.success(request, "Payment has been successfully made")
                # notify contributor and send email
                email_body = loader.render_to_string("ssw/email_new_payment.html", {"payment": payment})
                send_mail("عملية دفع جديدة لك", "", "Sowarstock", [payment.contributor.email], False,
                          None, None, None, email_body)
                notify.send(request.user, recipient=payment.contributor, level="success",
                            verb='You got paid ${}'.format(payment.amount))
                return HttpResponseRedirect("/fadmin/earnings")
        return render(request, "ssw/admin/payment_new.html", {"user": user, "earning": earning,
                                                                "form": form,
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def search_keywords_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        keywords = models.SearchKeyword.objects.all()
        synonyms = models.SearchKeywordSynonyms.objects.all()
        return render(request, "ssw/admin/search_keywords_main.html",
                      {"user": user, "keywords": keywords, "synonyms": synonyms,
                       "activeDashboardMenu": "keywords",
                       **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def search_keyword_synonyms_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        form = forms.SearchKeywordSynonymsForm()
        if request.method == "POST":
            form = forms.SearchKeywordSynonymsForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Word synonyms added successfully")
                return HttpResponseRedirect("/admin/search-keywords")
        return render(request, "ssw/admin/search_keyword_synonyms_new.html",
                      {"user": user, "form": form,
                       "activeDashboardMenu": "keywords",
                       **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def search_keyword_synonyms_edit(request, pk):
    user = getSowarStockUser(request.user)
    synonym = get_object_or_404(models.SearchKeywordSynonyms, pk=pk)
    if user.type == "admin":
        form = forms.SearchKeywordSynonymsForm(instance=synonym)
        if request.method == "POST":
            form = forms.SearchKeywordSynonymsForm(request.POST, instance=synonym)
            if form.is_valid():
                form.save()
                messages.success(request, "Word synonyms updated successfully")
                return HttpResponseRedirect("/admin/search-keywords")
        return render(request, "ssw/admin/search_keyword_synonyms_new.html",
                      {"user": user, "form": form,
                       "activeDashboardMenu": "keywords",
                       **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def search_keyword_synonyms_delete(request, pk):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        synonym = get_object_or_404(models.SearchKeywordSynonyms, pk=pk)
        synonym.delete()
        messages.success(request, "Word synonyms deleted successfully")
        return HttpResponseRedirect("/admin/search-keywords")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def reports_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        return render(request, "ssw/admin/reports_main.html",
                      {"user": user, "activeDashboardMenu": "reports",
                       **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def site_settings_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "admin":
        settings = models.SiteSettings.objects.get(pk=1)
        form = forms.SiteSettingsForm(instance=settings)
        if request.method == "POST":
            form = forms.SiteSettingsForm(request.POST, request.FILES, instance=settings)
            if form.is_valid():
                form.save()
                messages.success(request, "Settings updated successfully")
            else:
                messages.error(request, "An error occurred while trying to save the settings")
        return render(request, "ssw/admin/site_settings_main.html",
                      {"user": user, "activeDashboardMenu": "site_settings", "settings": settings,
                       "form": form, **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

