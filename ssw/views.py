from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext as _
from itertools import chain
from notifications.models import Notification
from paypal.standard.forms import PayPalPaymentsForm
import random
import uuid

from . import models, forms
from .image_handling import create_watermarked_image, eps_to_jpeg


def showCorrectMenu(user):
    showcontributormenu = False
    showadminmenu = False
    showreviewermenu = False
    showclientmenu = False
    showfinancialmenu = False
    u = models.SowarStockUser.objects.get(id=user.id)
    if u.type == "contributor":
        showcontributormenu = True
    elif u.type == "admin":
        showadminmenu = True
    elif u.type == "image_reviewer":
        showreviewermenu = True
    elif u.type == "financial_admin":
        showfinancialmenu = True
    elif u.type == "client":
        showclientmenu = True
    return {"showcontributormenu": showcontributormenu, "showadminmenu": showadminmenu,
            "showfinancialmenu": showfinancialmenu, "showreviewermenu": showreviewermenu,
            "showclientmenu": showclientmenu}


def getSowarStockUser(user):
    if user.is_authenticated:
        u = models.SowarStockUser.objects.get(pk=user.pk)
        if u.type == "contributor":
            co = models.Contributor.objects.get(pk=user.pk)
            return co
        elif u.type == "client":
            cl = models.Client.objects.get(pk=user.pk)
            return cl
        return u
    else:
        return user


# Create your views here.
def landing(request):
    return render(request, "ssw/landing.html", {"user": getSowarStockUser(request.user),
                                                "activeDashboardMenu": "home"})


def signup(request):
    if request.method == "POST":
        user_type = request.POST['user_type']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if user_type == "contributor":
            user = models.Contributor.objects.create_user(username,email,password, type=user_type, status="unverified")
        elif user_type == "client":
            user = models.Client.objects.create_user(username, email, password, type=user_type)
        email_body = loader.render_to_string("ssw/email_verify_email.html", {"user": user})
        send_mail("شكرا لإنضمامكم", "", "Sowar Stock", [user.email], False,
                  None, None, None, email_body)
        return HttpResponseRedirect("/thanks-for-joining")
    return render(request, "ssw/signup.html",{"user":getSowarStockUser(request.user)})


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/profile")
        else:
            messages.error(request, _("username and/or password is incorrect"))
    return render(request, "ssw/login.html", {"user": getSowarStockUser(request.user)})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


def thanks_for_joining(request):
    return render(request, "ssw/thanks_for_joining.html", {"user": getSowarStockUser(request.user)})


def verfiy_email(request, uuid):
    try:
        user = models.SowarStockUser.objects.get(email_verification_code=uuid, email_verified=False)
        user.email_verified = True
        user.save()
        return render(request, "ssw/email_verification_success.html", {"user": getSowarStockUser(request.user)})
    except:
        messages.error(request, _("The link you followed is invalid"))
        return HttpResponseRedirect("/")


def recover_account(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = models.SowarStockUser.objects.get(email=email)
            user.forgot_password_verification = uuid.uuid4()
            user.forgot_password_status = "not_used"
            user.save()
            email_body = loader.render_to_string("ssw/email_recover_account.html", {"user": user})
            send_mail("إعادة كلمة المرور", "", "Sowar Stock", [user.email], False,
                     None, None, None, email_body)
            messages.success(request, _("An email address has been sent to you"))
        except:
            messages.error(request, _("This email address does not exist"))
        return HttpResponseRedirect("/recover")
    return render(request, "ssw/recover_account.html", {"user": getSowarStockUser(request.user)})


def reset_password(request, uuid):
    if request.method == "POST":
        user = models.SowarStockUser.objects.get(forgot_password_verification=uuid, forgot_password_status="not_used")
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.forgot_password_status = "used"
            user.save()
            messages.success(request, _("Your password has been reset"))
            return HttpResponseRedirect("/")
        else:
            messages.error(request, _("The Password you've entered is not valid. One or more of the Password rules has not been met. Please try again."))
            return HttpResponseRedirect("/reset-password/{}".format(user.forgot_password_verification))
    try:
        user = models.SowarStockUser.objects.get(forgot_password_verification=uuid, forgot_password_status="not_used")
        form = SetPasswordForm(user)
        return render(request, "ssw/reset_password.html", {"user": getSowarStockUser(request.user), "form": form})
    except:
        messages.error(request, _("The link you followed is invalid"))
        return HttpResponseRedirect("/")


def search(request):
    if request.method == "POST":
        kws = request.POST['search']
        kws_list = kws.split(" ")
        products = list()
        for kw in kws_list:
            qs = models.Product.objects.filter(keywords__icontains=kw, status="approved")
            products = list(chain(products,qs))
        return render(request,"ssw/search_results.html", {"user": getSowarStockUser(request.user),
                                                          "products": list(reversed(products)), "keywords": kws})
    return HttpResponseRedirect("/")


def photos_main(request):
    photos = models.Product.objects.filter(category__name="Photos", status="approved")
    return render(request, "ssw/photos_main.html", {"user": getSowarStockUser(request.user),
                                                    "photos": photos, "activeDashboardMenu": "photos"})


def vectors_main(request):
    vectors = models.Product.objects.filter(category__name="Vectors and Paintings", status="approved")
    return render(request, "ssw/vectors_main.html", {"user": getSowarStockUser(request.user),
                                                     "vectors": vectors, "activeDashboardMenu": "vectors"})


def calligraphy_main(request):
    calligraphy = models.Product.objects.filter(category__name="Calligraphy", status="approved")
    return render(request, "ssw/calligraphy_main.html", {"user": getSowarStockUser(request.user),
                                                         "calligraphy": calligraphy,
                                                         "activeDashboardMenu": "calligraphy"})


def about(request):
    return render(request, "ssw/about.html", {"user": getSowarStockUser(request.user), "activeDashboardMenu": "about"})


def contact(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]
        body = "name: {}, email: {}, message: {}".format(name,email,message)
        send_mail("contact us inquery", body, email, ["support@sowarstock.com"])
        messages.success(request, _("Thanks for your enquiry, we'll be in touch shortly."))
    return render(request, "ssw/contact.html", {"user":getSowarStockUser(request.user), "activeDashboardMenu": "contact"} )


@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_pk = request.POST["product"]
        product = get_object_or_404(models.Product, pk=product_pk)
        license = request.POST["license"]
        user = get_object_or_404(models.Client, pk=request.user.pk)
        try:
            cart = models.ShoppingCart.objects.get(owner=user)
            models.ShoppingCartItem.objects.create(product=product, license_type=license, cart=cart)
        except:
            cart = models.ShoppingCart.objects.create(owner = user)
            models.ShoppingCartItem.objects.create(product=product, license_type=license, cart=cart)
        messages.success(request,"item has been added to your cart")
        return HttpResponseRedirect("/products/public/{}".format(product.public_id))
    return HttpResponseRedirect("/")


@login_required
def shopping_cart_main(request):
    user = get_object_or_404(models.Client, pk=request.user.pk)
    try:
        cart = models.ShoppingCart.objects.get(owner=user)
    except:
        cart = models.ShoppingCart.objects.create(owner=user)
    items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")
    return render(request, "ssw/shopping_cart_main.html", {"user":getSowarStockUser(request.user), "cart":cart, "items": items})


@login_required
def update_cart(request):
    if request.method == "POST":
        cart_pk = request.POST["cart"]
        cart = get_object_or_404(models.ShoppingCart,pk = cart_pk)
        items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")
        for item in items:
            license = request.POST["license_{}".format(item.pk)]
            item.license_type = license
            item.save()
        return HttpResponseRedirect("/shopping-cart")


@login_required
def remove_from_cart(request,pk):
    item = get_object_or_404(models.ShoppingCartItem, pk=pk)
    user = getSowarStockUser(request.user)
    if item.cart.owner == user:
        item.status = "removed"
        item.save()
        return HttpResponseRedirect("/shopping-cart")
    else:
        messages.error(request, "An error has occurred")
        return HttpResponseRedirect("/")


@login_required
def checkout(request):
    user = get_object_or_404(models.Client, pk=request.user.pk)
    cart = get_object_or_404(models.ShoppingCart, owner=user)
    items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")
    if not items:
        return HttpResponseRedirect("/shopping-cart")
    products = []
    for item in items:
        products.append(item.product)
    # What you want the button to do.
    paypal_dict = {
        "business": "sowarstock.co@gmail.com",
        "amount": cart.total(),
        "item_name": '+ '.join(str(e) for e in products),
        "invoice": "unique-invoice-id",
        "notify_url": "https://33441949.ngrok.io" + reverse('paypal-ipn'),
        "return": "https://33441949.ngrok.io/thanks-for-payment",
        "cancel_return": "https://33441949.ngrok.io/checkout",
        "custom": user
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)

    return render(request, "ssw/checkout.html", {"user": user, "cart": cart, "items": items, "form": form})


@login_required
def thanks_for_payment(request):
    return render(request, "ssw/thanks_for_payment.html", {"user": getSowarStockUser(request.user)})


@login_required
def orders(request):
    user = getSowarStockUser(request.user)
    if user.type == "client":
        orders = models.Order.objects.filter(owner__pk = request.user.pk)
        return render(request, "ssw/orders.html", {"user": getSowarStockUser(request.user), "orders":orders,
                                               "activeDashboardMenu": "orders", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def order_details(request, order_no):
    order = get_object_or_404(models.Order, order_no = order_no)
    user = getSowarStockUser(request.user)
    if user.type == "client" and order.owner == user:
        return render(request, "ssw/order_details.html", {"user": getSowarStockUser(request.user), "order":order,
                                                      "activeDashboardMenu": "orders", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def other_profile(request, username):
    user = get_object_or_404(models.SowarStockUser, username=username)
    other_user = getSowarStockUser(user)
    return render(request, "ssw/other_profile.html", {"other_profile": other_user})


@login_required
def profile(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor" or user.type == "client":
        return render(request, "ssw/profile.html", {"user": user, **showCorrectMenu(request.user)})
    elif user.type == "admin":
        users = models.SowarStockUser.objects.all()
        contributors = models.Contributor.objects.all()
        clients = models.Client.objects.all()
        pending = models.Product.objects.filter(status="pending_approval") | models.Product.objects.filter(owner_id=request.user.id, status="pending_admin_approval")
        approved = models.Product.objects.filter(status="approved")
        rejected = models.Product.objects.filter(status="rejected")
        try:
            sales = models.Order.objects.aggregate(Sum('total'))
            sales_amount = round(sales['total__sum'], 2)
        except:
            sales_amount = 0
        try:
            earnings = models.Earning.objects.filter(type="sowarstock").aggregate(Sum('amount'))
            earnings_amount = round(earnings['amount__sum'], 2)
        except:
            earnings_amount = 0
        try:
            owed = models.Earning.objects.filter(type="contributor", payment=None).aggregate(Sum('amount'))
            owed_amount = round(owed['amount__sum'],2)
        except:
            owed_amount = 0
        return render(request, "ssw/profile.html", {"user": user, "users": users, "contributors": contributors,
                                                    "clients": clients, "pending": pending, "approved": approved,
                                                    "rejected": rejected, "sales": sales_amount,
                                                    "earnings": earnings_amount, "owed": owed_amount,
                                                    **showCorrectMenu(request.user)})
    elif user.type == "image_reviewer":
        pending = models.Product.objects.filter(status="pending_approval") | models.Product.objects.filter(
            owner_id=request.user.id, status="pending_admin_approval")
        approved = models.Product.objects.filter(status="approved")
        rejected = models.Product.objects.filter(status="rejected")
        return render(request, "ssw/profile.html", {"pending": pending, "approved": approved,
                                                    "rejected": rejected, "user": user, **showCorrectMenu(request.user)})
    elif user.type == "financial_admin":
        try:
            sales = models.Order.objects.aggregate(Sum('total'))
            sales_amount = round(sales['total__sum'], 2)
        except:
            sales_amount = 0
        try:
            earnings = models.Earning.objects.filter(type="sowarstock").aggregate(Sum('amount'))
            earnings_amount = round(earnings['amount__sum'], 2)
        except:
            earnings_amount = 0
        try:
            owed = models.Earning.objects.filter(type="contributor", payment=None).aggregate(Sum('amount'))
            owed_amount = round(owed['amount__sum'],2)
        except:
            owed_amount = 0
        return render(request, "ssw/profile.html", {"user": user, "sales": sales_amount, "earnings": earnings_amount,
                                                    "owed": owed_amount, **showCorrectMenu(request.user)})


@login_required
def products_main(request):
    import os
    os.system("touch test.txt")
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        pending = models.Product.objects.filter(owner_id=request.user.id, status="pending_approval") | models.Product.objects.filter(owner_id=request.user.id, status="pending_admin_approval")
        approved = models.Product.objects.filter(owner_id=request.user.id, status="approved")
        rejected = models.Product.objects.filter(owner_id=request.user.id, status="rejected")
        return render(request, "ssw/products_main.html", {"user":getSowarStockUser(request.user),
                                                      "pending": pending, "approved": approved, "rejected": rejected,
                                                      "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def products_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor" and user.is_verified():
        form = forms.ProductForm()
        if request.method == "POST":
            form = forms.ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                public_id = "%08d" % random.randint(1,100000000)
                product.public_id = public_id
                contributor = models.Contributor.objects.get(id=request.user.id)
                product.owner = contributor
                product.save()
                if product.file_type == "eps":
                    eps_to_jpeg(product)
                create_watermarked_image(product)
                messages.success(request, "Request to add product has been submitted successfully")
                return HttpResponseRedirect("/products/")
            else:
                messages.error(request, form.errors['__all__'])

        return render(request, "ssw/products_new.html", {"user": getSowarStockUser(request.user), "form": form,
                                                         "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_pending(request,public_id):
    user = getSowarStockUser(request.user)
    if not user.type == "client":
        product = get_object_or_404(models.Product, public_id=public_id)
        return render(request, "ssw/product_pending.html", {"user": getSowarStockUser(request.user), "product": product,
                                                        **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_details(request,public_id):
    user = getSowarStockUser(request.user)
    if not user.type == "client":
        product = get_object_or_404(models.Product, public_id=public_id)
        return render(request, "ssw/product_details.html", {"user": getSowarStockUser(request.user), "product": product,
                                                        **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def pending_product_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "admin":
            count = models.Product.objects.filter(status="pending_admin_approval").count()
            return JsonResponse({"result": "success", "count": count})
        elif user.type == "image_reviewer":
            count = models.Product.objects.filter(status="pending_approval").count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


def pending_requests_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "admin":
            count = models.UserRequest.objects.filter(status="pending_approval").count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


def pending_faqs_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "admin":
            count = models.FaqPersonal.objects.filter(replier__isnull=True).count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


def cart_items_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "client":
            try:
                cart = models.ShoppingCart.objects.get(owner=user)
                items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")
                if items:
                    count = items.count()
                    return JsonResponse({"result": "success", "count": count})
                else:
                    return JsonResponse({"result": "success", "msg": "no items"})
            except:
                return JsonResponse({"result": "success", "msg": "no items"})
        else:
            return JsonResponse({"result": "error", "msg": "no client"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


@login_required
def notifications_undread_to_read(request):
    notifications = request.user.notifications.unread()
    notifications.mark_all_as_read()
    return JsonResponse({"result": "success"})



@login_required
def product_delete(request, pk):
    """
    product = get_object_or_404(models.Product, pk=pk)
    product.image.delete_thumbnails()
    product.image.delete(False)
    product.delete()
    messages.success(request, "product deleted")
    """
    return HttpResponseRedirect("/products/")


@login_required
def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = models.SubCategory.objects.filter(main_category = category_id).order_by('name')
    return render(request, 'ssw/subcategories_dropdown_list_options.html', {'subcategories': subcategories})


@login_required
def account_settings(request, **kwargs):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        # personal information form
        personal_info_form = forms.ProfilePersonalInfoForm(instance=user)
        # address form
        if user.address:
            address_form = forms.AddressForm(instance=user.address)
        else:
            address_form = forms.AddressForm()
        # password form
        password_form = PasswordChangeForm(user)
        # public_info_form
        public_info_form = forms.ProfilePublicInfoForm(instance=user)
        # photo id form
        photo_id_form = forms.PhotoIdForm(instance=user)
        # payment method form
        payment_method_form = forms.PaymentMethodForm(instance=user)
        return render(request, 'ssw/account_settings.html', {"user": user,"personal_info_form":personal_info_form,
                                                             "address_form": address_form,"password_form": password_form,
                                                             "public_info_form": public_info_form, "photo_id_form": photo_id_form,
                                                             "payment_method_form": payment_method_form,
                                                             "activeDashboardMenu": "account_settings", **showCorrectMenu(request.user)})
    elif user.type == "client":
        # personal information form
        personal_info_form = forms.ProfilePersonalInfoForm(instance=user)
        # address form
        if user.address:
            address_form = forms.AddressForm(instance=user.address)
        else:
            address_form = forms.AddressForm()
        # password form
        password_form = PasswordChangeForm(user)
        return render(request, 'ssw/account_settings_client.html', {"user": user, "personal_info_form": personal_info_form,
                                                             "address_form": address_form,
                                                             "password_form": password_form,
                                                             "activeDashboardMenu": "account_settings",
                                                             **showCorrectMenu(request.user)})
    else:
        return HttpResponseRedirect("/")


@login_required
def update_personal_info(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        clear_profile_image = request.POST.get('profile_image-clear', None)
        if clear_profile_image is not None:
            storage, path = user.profile_image.storage, user.profile_image.path
            storage.delete(path)
        personal_info_form = forms.ProfilePersonalInfoForm(request.POST, request.FILES, instance=user)
        if personal_info_form.is_valid():
            personal_info_form.save()
            messages.success(request, "Personal Information updated successfully")
        else:
            messages.error(request, personal_info_form.errors)
    return HttpResponseRedirect("/account_settings")


@login_required
def update_address(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        address_form = forms.AddressForm(request.POST, instance=user.address)
        if address_form.is_valid():
            address = address_form.save()
            user.address = address
            user.save()
            messages.success(request, "Address updated successfully")
        else:
            messages.error(request, "Please Correct the errors.")
    return HttpResponseRedirect("/account_settings")


@login_required
def update_password(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            password = password_form.save()
            update_session_auth_hash(request, password)
            messages.success(request, "Password updated successfully")
        else:
            messages.error(request, "Please Correct the errors")
            #url = reverse("account_settings", kwargs={'msg':'hello world'})
            #return HttpResponseRedirect(url)
    return HttpResponseRedirect("/account_settings")


@login_required
def update_public_info(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        public_info_form = forms.ProfilePublicInfoForm(request.POST, instance=user)
        if public_info_form.is_valid():
            public_info_form.save()
            messages.success(request, "Public Information updated successfully")
        else:
            messages.error(request, public_info_form.errors)
    return HttpResponseRedirect("/account_settings")


@login_required
def update_photo_id(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        photo_id_form = forms.PhotoIdForm(request.POST, request.FILES, instance=user)
        if photo_id_form.is_valid():
            photo_id_form.save()
            models.UserRequest.objects.create(owner = user, body = user.photo_id.url)
            messages.success(request, "Photo ID updated successfully")
        else:
            messages.error(request, photo_id_form.errors)
    return HttpResponseRedirect("/account_settings")


@login_required
def update_payment_method(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        payment_method_form = forms.PaymentMethodForm(request.POST, instance=user)
        if payment_method_form.is_valid():
            payment_method_form.save()
            messages.success(request, "Payment method updated successfully")
        else:
            messages.error(request, payment_method_form.errors)
    return HttpResponseRedirect("/account_settings")

@login_required
def notifications_main(request):
    notifications = request.user.notifications.all()
    return render(request, 'ssw/notifications_main.html', {"user": getSowarStockUser(request.user),"notifications":notifications,
                                                           "activeDashboardMenu": "notifications", **showCorrectMenu(request.user)})


@login_required
def notifications_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    user = getSowarStockUser(request.user)
    if notification.recipient == user:
        notification.delete()
        messages.success(request, "Notification has been deleted")
        return HttpResponseRedirect("/notifications")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def product_public_details(request, public_id):
    product = get_object_or_404(models.Product, public_id = public_id)

    review_form = forms.ReviewForm()
    if request.method == "POST":
        review_form = forms.ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            user = models.SowarStockUser.objects.get(id=request.user.id)
            review.product = product
            review.owner = user
            review.save()
            messages.success(request, "Comment added successfully")
        else:
            messages.error(request, "There was an error adding your comment")
        return HttpResponseRedirect("/products/public/{}".format(public_id))
    return render(request, 'ssw/product_public_details.html', {"user": getSowarStockUser(request.user),
                                                               "product": product, "review_form": review_form})


@login_required
def reviews_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        reviews = models.Review.objects.filter(product__owner=user)
        return render(request, "ssw/reviews_main.html", {"user": getSowarStockUser(request.user),
                                                     "activeDashboardMenu": "reviews",
                                                     "reviews": reviews, **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def faqs_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        faqs = models.Faq.objects.all()
        personal_faqs = models.FaqPersonal.objects.filter(owner__id=request.user.id)
        form = forms.PersonalFaqForm()
        if request.method == "POST":
            form = forms.PersonalFaqForm(request.POST)
            if form.is_valid():
                user = get_object_or_404(models.Contributor, pk = request.user.pk)
                pfaq = form.save(commit=False)
                pfaq.owner = user
                pfaq.save()
                messages.success(request, "Your question has been submitted successfully")
            else:
                messages.error(request, "There was an error submitting your question")
            return HttpResponseRedirect("/faqs")
        return render(request, "ssw/faqs_main.html", {"user":getSowarStockUser(request.user), "faqs": faqs, "personal_faqs": personal_faqs,
                                                      "form": form, "activeDashboardMenu": "faqs", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def collections_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        collections = models.Collection.objects.filter(owner__pk = request.user.pk)
        return render(request, "ssw/collections_main.html", {"user":getSowarStockUser(request.user), "collections": collections,
                                                  "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def collections_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor" and user.is_verified():
        products = models.Product.objects.filter(owner__id = request.user.id, status="approved")
        if request.method == "POST":
            title = request.POST["title"]
            products = request.POST.getlist("products")
            if(title == ""):
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/collections/new")
            if not products:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/collections/new")
            contributor = get_object_or_404(models.Contributor, pk = request.user.pk)
            collection = models.Collection.objects.create(title=title, owner = contributor)
            for product in products:
                p = get_object_or_404(models.Product, pk = product)
                collection.products.add(p)
            collection.save()
            messages.success(request, "Collection created successfully")
            return HttpResponseRedirect("/collections")
        return render(request, "ssw/collections_new.html", {"user":getSowarStockUser(request.user), "products": products,
                                                      "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def collections_edit(request,pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    user = getSowarStockUser(request.user)
    if user.type == "contributor" and collection.owner == user:
        products = models.Product.objects.filter(owner__id=request.user.id, status="approved")
        if request.method == "POST":
            title = request.POST["title"]
            products_pks = request.POST.getlist("products")
            if title == "":
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/collections/{}/edit".format(collection.pk))
            if not products_pks:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/collections/{}/edit".format(collection.pk))
            collection.products.clear()
            for product in products_pks:
                p = get_object_or_404(models.Product, pk=product)
                collection.products.add(p)
            collection.save()
            messages.success(request, "Collection updated successfully")
            return HttpResponseRedirect("/collections")
        return render(request, "ssw/collections_new.html", {"user": getSowarStockUser(request.user), "products": products, "collection": collection,
                                                            "activeDashboardMenu": "collections", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def collections_delete(request, pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    user = getSowarStockUser(request.user)
    if user.type == "contributor" and collection.owner == user:
        collection.delete()
        messages.success(request,"Collection deleted")
        return HttpResponseRedirect("/collections")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def profile_products(request, username):
    other_profile = get_object_or_404(models.Contributor, username=username)
    user = getSowarStockUser(request.user)
    products = models.Product.objects.filter(owner=other_profile)
    return render(request, "ssw/profile_products.html", {"user": user, "other_profile": other_profile,
                                                         "products": products})


def profile_product_details(request, username, public_id):
    user = getSowarStockUser(request.user)
    other_profile = get_object_or_404(models.Contributor, username=username)
    product = get_object_or_404(models.Product, public_id=public_id, owner=other_profile)
    return render(request, "ssw/profile_product_details.html", {"user":user, "other_profile": other_profile,
                                                                "product": product})

@login_required
def earnings_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        earnings = models.Earning.objects.filter(contributor=user)
        return render(request, "ssw/earnings_main.html", {"user": user, "earnings": earnings, **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

