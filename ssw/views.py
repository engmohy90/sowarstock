from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext as _
from itertools import chain
from notifications.models import Notification
from paypal.standard.forms import PayPalPaymentsForm
from countries_plus.models import Country
import json
import random
import uuid

from . import models, forms
from .image_handling import create_watermarked_image, create_thumbnailed_image, remove_profile_image, crop_profile_image


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


def get_country_codes_json():
    countries = list(Country.objects.all())
    country_codes = list()
    for country in countries:
        country_codes.append("{}".format(country))
    codes_json = json.dumps(list(country_codes), cls=DjangoJSONEncoder)
    return codes_json


# Create your views here.
def landing(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]
        body = "name: {}, email: {}, message: {}".format(name,email,message)
        send_mail("contact us inquery", body, email, ["support@sowarstock.com"])
        messages.success(request, _("Thanks for your enquiry, we'll be in touch shortly."))
        return HttpResponseRedirect("/")
    return render(request, "ssw/landing.html", {"user": getSowarStockUser(request.user),
                                                "activeDashboardMenu": "home"})


def signup(request):
    form = forms.SignupForm()
    if request.method == "POST":
        user_type = request.POST['user_type']
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save(False)
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            if user_type == "contributor":
                user = models.Contributor.objects.create_user(username, email, password, type=user_type)
            elif user_type == "client":
                    user = models.Client.objects.create_user(username, email, password, type=user_type)
            email_body = loader.render_to_string("ssw/email_verify_email.html", {"user": user})
            send_mail("شكرا لإنضمامكم", "", "Sowarstock", [user.email], False, None, None, None, email_body)
            return HttpResponseRedirect("/thanks-for-joining")
    return render(request, "ssw/signup.html",{"user":getSowarStockUser(request.user), "form": form})


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
        login(request, user)
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
            send_mail("إسترجاع الحساب", "", "Sowarstock", [user.email], False,
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
    kws = request.GET.get('keywords', '')
    kws_list = kws.split(" ")
    kws_final_list = list()
    for kw in kws_list:
        try:
            keyword = models.SearchKeyword.objects.get(word__iexact=kw)
            keyword.count = keyword.count + 1
            keyword.save()
        except:
            models.SearchKeyword.objects.create(word=kw, count=1)
    for kw in kws_list:
        try:
            synonyms = models.SearchKeywordSynonyms.objects.get(word__iexact=kw)
            synonyms_list = [x.strip() for x in synonyms.synonyms.split(",")]
            kws_final_list.append(kw)
            kws_final_list = kws_final_list + synonyms_list
        except:
            kws_final_list.append(kw)
    products = list()
    for kw in kws_final_list:
        qs = models.Product.objects.filter(
            Q(title__icontains=kw, status="approved") |
            Q(description__icontains=kw, status="approved") |
            Q(keywords__icontains=kw, status="approved")
        )
        products = list(chain(products,qs))
    # remove duplicates
    final_products = list()
    for product in products:
        if product not in final_products:
            final_products.append(product)
    subcategories = set()
    for product in final_products:
        subcategories.add(product.subcategory)
    return render(request, "ssw/search_results.html", {"user": getSowarStockUser(request.user),
                                                      "subcategories": subcategories,
                                                      "products": final_products, "keywords": kws})


def photos_main(request):
    photos = models.Product.objects.filter(category__name="Photos", status="approved")
    subcategories = set()
    for photo in photos:
        subcategories.add(photo.subcategory)
    return render(request, "ssw/photos_main.html", {"user": getSowarStockUser(request.user), "photos": photos,
                                                    "subcategories": subcategories,
                                                    "activeDashboardMenu": "photos"})


def vectors_main(request):
    vectors = models.Product.objects.filter(category__name="Vectors and Paintings", status="approved")
    subcategories = set()
    for vector in vectors:
        subcategories.add(vector.subcategory)
    return render(request, "ssw/vectors_main.html", {"user": getSowarStockUser(request.user),
                                                     "subcategories": subcategories,
                                                     "vectors": vectors, "activeDashboardMenu": "vectors"})


def calligraphy_main(request):
    calligraphy = models.Product.objects.filter(category__name="Calligraphy", status="approved")
    subcategories = set()
    for c in calligraphy:
        subcategories.add(c.subcategory)
    return render(request, "ssw/calligraphy_main.html", {"user": getSowarStockUser(request.user),
                                                         "calligraphy": calligraphy,
                                                         "subcategories": subcategories,
                                                         "activeDashboardMenu": "calligraphy"})


def editorials_main(request):
    editorials = models.Product.objects.filter(editorial=True, status="approved")
    subcategories = set()
    for editorial in editorials:
        subcategories.add(editorial.subcategory)
    return render(request, "ssw/editorials_main.html", {"user": getSowarStockUser(request.user), "editorials": editorials,
                                                    "subcategories": subcategories,
                                                    "activeDashboardMenu": "editorials"})


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
        return HttpResponseRedirect("/contact")
    return render(request, "ssw/contact2.html", {"user":getSowarStockUser(request.user), "activeDashboardMenu": "contact"} )


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
    invoice_id = uuid.uuid4()
    paypal_dict = {
        "business": "sowarstock.co@gmail.com",
        "amount": cart.total(),
        "item_name": '+ '.join(str(e) for e in products),
        "invoice": uuid.uuid4(),
        "notify_url": "https://www.sowarstock.com" + reverse('paypal-ipn'),
        "return": "https://www.sowarstock.com/thanks-for-payment",
        "cancel_return": "https://www.sowarstock.com/checkout",
        "custom": "%s:%s" % (user,invoice_id)
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

import urllib.request
from PIL import Image
from io import BytesIO
import requests
@login_required
def order_details(request, order_no):
    order = get_object_or_404(models.Order, order_no=order_no)
    user = getSowarStockUser(request.user)
    if user.type == "client" and order.owner == user:
        return render(request, "ssw/order_details.html", {"user": getSowarStockUser(request.user), "order":order,
                                                      "activeDashboardMenu": "orders", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def other_profile(request, username):
    user = get_object_or_404(models.SowarStockUser, username=username)
    other_profile = getSowarStockUser(user)
    products = list()
    if other_profile.type == "contributor":
        products = models.Product.objects.filter(owner=other_profile, status="approved")
    return render(request, "ssw/other_profile.html", {"other_profile": other_profile, "products": products})


@login_required
def profile(request):
    user = getSowarStockUser(request.user)
    if  user.type == "client":
        return render(request, "ssw/profile.html", {"user": user, **showCorrectMenu(request.user)})
    elif user.type == "contributor":
        if user.completed_registration:
            return render(request, "ssw/profile.html", {"user": user, **showCorrectMenu(request.user)})
        else:
            return HttpResponseRedirect("/complete-registration")
    elif user.type == "admin":
        users = models.SowarStockUser.objects.all()
        contributors = models.Contributor.objects.all()
        clients = models.Client.objects.all()
        pending = models.Product.objects.filter(status="pending_approval") | models.Product.objects.filter(status="pending_admin_approval")
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
            status="pending_admin_approval")
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
def complete_registration(request):
    user = getSowarStockUser(request.user)
    if not user.completed_registration:
        personal_info_form = forms.ProfilePersonalInfoForm(instance=user)
        address_form = forms.AddressForm()
        #photo_id_form = forms.PhotoIdForm(instance=user)
        #sample_product_formset = forms.SampleProductFormset(queryset=models.SampleProduct.objects.filter(owner=user))

        codes_json = get_country_codes_json()

        models.ActivityLog.objects.create(short_description="user %s started completing registration" % user, owner=user)

        if request.method == "POST":
            personal_info_form = forms.ProfilePersonalInfoForm(request.POST, request.FILES, instance=user)
            address_form = forms.AddressForm(request.POST, instance=user.address)
            #photo_id_form = forms.PhotoIdForm(request.POST, request.FILES, instance=user)
            #sample_product_formset = forms.SampleProductFormset(request.POST, request.FILES)
            if personal_info_form.is_valid() and address_form.is_valid():
                personal_info_form.save()
                address = address_form.save()
                user.address = address
                user.save()
                #photo_id_form.save()

                profile_image_url = request.POST.get('profile_image_url', None)
                if profile_image_url:
                    user.profile_image_url = profile_image_url
                    user.save()
                    crop_profile_image(user)

                photo_id_url = request.POST.get('photo_id_url', None)
                if photo_id_url:
                    user.photo_id_url = photo_id_url
                    user.save()

                sample_portfolio_url = request.POST.get('sample_portfolio_url', None)
                if sample_portfolio_url:
                    if "http" not in sample_portfolio_url:
                        user.sample_portfolio_url = "http://" + sample_portfolio_url
                    else:
                        user.sample_portfolio_url = sample_portfolio_url
                    user.save()

                models.ActivityLog.objects.create(short_description="user %s finished completing registration" % user,
                                                  owner=user)
                models.UserRequest.objects.create(owner=user)
                """
                for i in range(1, 11):
                    sample_image_url = request.POST.get("sample_image_%s_url" % i, None)
                    if sample_image_url:
                        sample = models.SampleProduct.objects.create(image_url=sample_image_url, owner=user)
                        create_thumbnailed_image(sample)
                samples = sample_product_formset.save(commit=False)
                for sample in samples:
                    sample.owner = user
                    sample.save()
                    create_thumbnailed_image(sample)
                """
                user.completed_registration = True
                user.save()
                return HttpResponseRedirect("/thanks-for-completing-registration")
        return render(request, "ssw/complete_registration.html", {"user": user, "personal_info_form": personal_info_form,
                                                                  "address_form": address_form,
                                                                  "codes_json": codes_json})
    else:
        return HttpResponseRedirect("/profile")


@login_required
def thanks_for_completing_registration(request):
    user = getSowarStockUser(request.user)
    return render(request, "ssw/thanks_for_completing_registration.html", {"user": user})


@login_required
def resend_email_activation(request):
    user = getSowarStockUser(request.user)
    email_body = loader.render_to_string("ssw/email_verify_email.html", {"user": user})
    send_mail("شكرا لإنضمامكم", "", "Sowarstock", [user.email], False, None, None, None, email_body)
    return JsonResponse({"result": "success", "msg": "email sent"})


@login_required
def products_main(request):
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
                public_id = "%08d" % random.randint(1, 100000000)
                product.public_id = public_id
                contributor = models.Contributor.objects.get(id=request.user.id)
                product.owner = contributor
                if product.file_type == "eps":
                    file_url = request.POST.get("file_url", None)
                    product.file_url = file_url
                else:
                    image_url = request.POST.get('image_url', None)
                    product.image_url = image_url
                product.save()
                create_watermarked_image(product)
                messages.success(request, "Request to add product has been submitted successfully")
                models.ActivityLog.objects.create(short_description="user %s submitted a new product %s" % (user,product),
                                                  owner=user)
                return HttpResponseRedirect("/products/")
            else:
                if '__all__' in form.errors:
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
                                                            "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_details(request,public_id):
    user = getSowarStockUser(request.user)
    if not user.type == "client":
        product = get_object_or_404(models.Product, public_id=public_id)
        return render(request, "ssw/product_details.html", {"user": getSowarStockUser(request.user), "product": product,
                                                            "activeDashboardMenu": "products", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


@login_required
def product_request_to_archive(request, pk):
    product = get_object_or_404(models.Product, pk=pk)
    product.requested_to_archive = True
    product.save()
    return HttpResponseRedirect("/products/")


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
        user_request_delete_form = forms.UserRequestDeleteForm()
        codes_json = get_country_codes_json()
        return render(request, 'ssw/account_settings.html', {"user": user,"personal_info_form":personal_info_form,
                                                             "address_form": address_form,"password_form": password_form,
                                                             "public_info_form": public_info_form, "photo_id_form": photo_id_form,
                                                             "payment_method_form": payment_method_form,
                                                             "user_request_delete_form": user_request_delete_form,
                                                             "codes_json": codes_json,
                                                             "activeDashboardMenu": "account_settings", **showCorrectMenu(request.user)})
    else:
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


@login_required
def update_personal_info(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        clear_profile_image = request.POST.get('profile_image-clear', None)
        avatar_url = request.POST.get('avatar-url', None)
        if avatar_url:
            # check if user already has a profile image
            if user.profile_image_url:
                remove_profile_image(user)
            user.profile_image_url = avatar_url
            user.save()
            crop_profile_image(user)
        if clear_profile_image is not None:
            #storage, path = user.profile_image.storage, user.profile_image.path
            #storage.delete(path)
            remove_profile_image(user)
        personal_info_form = forms.ProfilePersonalInfoForm(request.POST, instance=user)
        if personal_info_form.is_valid():
            personal_info_form.save()
            messages.success(request, "Personal Information updated successfully")
        else:
            if '__all__' in personal_info_form.errors:
                messages.error(request, personal_info_form.errors['__all__'])
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
            messages.success(request, "Password updated successfully. Please login with the new password")
            models.ActivityLog.objects.create(short_description="user %s updated password" % user,
                                              owner=user)
        else:
            messages.error(request, "Please Correct the errors")
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
            models.UserRequest.objects.create(owner=user, body=user.photo_id_url)
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
            email_body = loader.render_to_string("ssw/email_update_payment_settings.html", {"user": user})
            send_mail("تحديث إعدادات الدفع", "", "Sowarstock", [user.email], False, None, None, None, email_body)
            messages.success(request, "Payment method updated successfully")
        else:
            messages.error(request, payment_method_form.errors)
    return HttpResponseRedirect("/account_settings")


@login_required
def update_user_request_delete(request):
    if request.method == "POST":
        user = getSowarStockUser(request.user)
        user_request_delete_form = forms.UserRequestDeleteForm(request.POST)
        if user_request_delete_form.is_valid():
            r = user_request_delete_form.save(commit=False)
            r.owner = user
            r.type = "delete"
            r.save()
            messages.success(request, "Request sent successfully")
        else:
            messages.error(request, user_request_delete_form.errors)
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
    if notification.recipient.pk == user.pk:
        notification.delete()
        messages.success(request, "Notification has been deleted")
        if user.type == "admin":
            return HttpResponseRedirect("/admin/notices")
        else:
            return HttpResponseRedirect("/notifications")
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")


def product_public_details(request, public_id):
    product = get_object_or_404(models.Product, public_id=public_id)
    referer = request.META.get('HTTP_REFERER', "")
    if referer:
        if "search" in referer:
            back_section = "Search Results"
        elif "photos" in referer:
            back_section = "Photos"
        elif "vectors" in referer:
            back_section = "Vectors & Paintings"
        elif "calligraphy" in referer:
            back_section = "Calligraphy"
        elif "editorials" in referer:
            back_section = "Editorials"
        else:
            back_section = product.category
    else:
        referer = "/%s" % product.category.name.lower()
        back_section = product.category
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
                                                               "back_section": back_section, "back_url": referer,
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
            description = request.POST["description"]
            products = request.POST.getlist("products")
            if title == "" :
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/collections/new")
            if description == "":
                messages.error(request, "Please choose a description for your collection")
                return HttpResponseRedirect("/collections/new")
            if not products:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/collections/new")
            contributor = get_object_or_404(models.Contributor, pk=request.user.pk)
            collection = models.Collection.objects.create(title=title, description=description, owner=contributor)
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
    if user.type == "contributor" and collection.owner.pk == user.pk:
        products = models.Product.objects.filter(owner__id=request.user.id, status="approved")
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["description"]
            products_pks = request.POST.getlist("products")
            if title == "":
                messages.error(request, "Please choose a title for your collection")
                return HttpResponseRedirect("/collections/{}/edit".format(collection.pk))
            if description == "":
                messages.error(request, "Please choose a description for your collection")
                return HttpResponseRedirect("/collections/{}/edit".format(collection.pk))
            if not products_pks:
                messages.error(request, "Please select at least one product")
                return HttpResponseRedirect("/collections/{}/edit".format(collection.pk))
            collection.title = title
            collection.description = description
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
    products = models.Product.objects.filter(owner=other_profile, status="approved")
    subcategories = set()
    for p in products:
        subcategories.add(p.subcategory)
    return render(request, "ssw/profile_products.html", {"user": user, "other_profile": other_profile,
                                                         "subcategories": subcategories,"products": products})


def profile_product_details(request, username, public_id):
    user = getSowarStockUser(request.user)
    other_profile = get_object_or_404(models.Contributor, username=username)
    product = get_object_or_404(models.Product, public_id=public_id, owner=other_profile, status="approved")
    return render(request, "ssw/profile_product_details.html", {"user":user, "other_profile": other_profile,
                                                                "product": product})

@login_required
def earnings_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        earnings = models.Earning.objects.filter(contributor=user)

        try:
            earnings2 = earnings.aggregate(Sum('amount'))
            earnings_total = round(earnings2['amount__sum'], 2)
        except:
            earnings_total = 0

        payments = models.Payment.objects.filter(contributor=user)

        try:
            payments2 = payments.aggregate(Sum('amount'))
            payments_total = round(payments2['amount__sum'], 2)
        except:
            payments_total = 0

        return render(request, "ssw/earnings_main.html", {"user": user, "earnings": earnings, "earnings_total": earnings_total,
                                                          "payments": payments, "payments_total": payments_total,
                                                          **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")
