from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.mail import send_mail
from itertools import chain
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from notifications.models import Notification
import random
import uuid

from . import models
from . import forms


def showCorrectMenu(user):
    showcontributormenu = False
    showadminmenu = False
    showreviewermenu = False
    u = models.SowarStockUser.objects.get(id=user.id)
    if u.type == "contributor":
        showcontributormenu = True
    elif u.type == "admin":
        showadminmenu = True
    elif u.type == "image_reviewer":
        showreviewermenu = True
    return {"showcontributormenu":showcontributormenu, "showadminmenu": showadminmenu, "showreviewermenu": showreviewermenu,
            "user": getSowarStockUser(user)}

def getSowarStockUser(user):
    if user.is_authenticated:
        u = models.SowarStockUser.objects.get(pk=user.pk)
        if u.type == "contributor":
            co = models.Contributor.objects.get(pk=user.pk)
            return co
        elif u.type == "client":
            cl = models.Client.objects.get(pk=user.pk)
            return cl
        return u # admins
    else:
        return user

# Create your views here.
def landing(request):
    return render(request, "ssw/landing.html",{"user":getSowarStockUser(request.user), "activeDashboardMenu": "home"})

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
        return HttpResponseRedirect("/")
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
            messages.error(request, "username and/or password is incorrect")
    return render(request, "ssw/login.html",{"user":getSowarStockUser(request.user)})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")

def verfiy_email(request, uuid):
    print("in verify email")
    try:
        user = models.SowarStockUser.objects.get(email_verification_code=uuid, email_verified=False)
        user.email_verified = True
        user.save()
        return render(request, "ssw/email_verification_success.html", {"user":getSowarStockUser(request.user)})
    except:
        messages.error(request, "The link you followed is invalid")
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
            messages.success(request, "An email address has been sent to you")
        except:
            messages.error(request, "This email address does not exist")
        return HttpResponseRedirect("/recover")
    return render(request, "ssw/recover_account.html", {"user": getSowarStockUser(request.user)})

def reset_password(request, uuid):
    if request.method == "POST":
        user = models.SowarStockUser.objects.get(forgot_password_verification=uuid, forgot_password_status="not_used")
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            #user.set_password(password)
            #user.forgot_password_status = "used"
            #user.save()
            messages.success(request, "Your password has been reset")
            return HttpResponseRedirect("/")
        else:
            messages.error(request, "Oops! an error has occurred. Please try again !")
            return HttpResponseRedirect("/reset-password/{}".format(user.forgot_password_verification))
    try:
        user = models.SowarStockUser.objects.get(forgot_password_verification=uuid, forgot_password_status="not_used")
        form = SetPasswordForm(user)
        return render(request, "ssw/reset_password.html", {"user": getSowarStockUser(request.user), "form": form})
    except:
        messages.error(request, "The link you followed is invalid")
        return HttpResponseRedirect("/")

def search(request):
    if request.method == "POST":
        kws = request.POST['search']
        kws_list = kws.split(" ")
        products = list()
        for kw in kws_list:
            qs = models.Product.objects.filter(keywords__icontains=kw, status="approved")
            products = list(chain(products,qs))
        #products = models.Product.objects.filter(Q(keywords__contains=kw[0])| Q(keywords__contains=kw[1]))
        return render(request,"ssw/search_results.html", {"user":getSowarStockUser(request.user),
                                                          "products": list(reversed(products)), "keywords": kws})
    return HttpResponseRedirect("/")

def photos_main(request):
    photos = models.Product.objects.filter(category__name="Photos", status="approved")
    return render(request, "ssw/photos_main.html", {"user":getSowarStockUser(request.user),
                                                    "photos": photos,"activeDashboardMenu": "photos"})

def vectors_main(request):
    vectors = models.Product.objects.filter(category__name="Vectors and Paintings", status="approved")
    return render(request, "ssw/vectors_main.html", {"user":getSowarStockUser(request.user),
                                                     "vectors": vectors, "activeDashboardMenu": "vectors"})

def calligraphy_main(request):
    calligraphy = models.Product.objects.filter(category__name="Calligraphy", status="approved")
    return render(request, "ssw/calligraphy_main.html", {"user":getSowarStockUser(request.user),
                                                         "calligraphy": calligraphy, "activeDashboardMenu": "calligraphy"})
def about(request):
    return render(request, "ssw/about.html", {"user":getSowarStockUser(request.user), "activeDashboardMenu": "about"} )

def contact(request):
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
        return HttpResponseRedirect("/products/public/{}".format(product.public_id))
    return HttpResponseRedirect("/photos")

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
        print(request.POST)
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
    item.status = "removed"
    item.save()
    return HttpResponseRedirect("/shopping-cart")

@login_required
def checkout(request):
    user = getSowarStockUser(request.user)
    cart = get_object_or_404(models.ShoppingCart, owner = user)
    items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")
    if not items:
        return HttpResponseRedirect("/shopping-cart")
    if request.method == "POST":
        order_no = "%08d" % random.randint(1, 100000000)
        order = models.Order.objects.create(order_no=order_no,owner=user,total=cart.total())
        for shopping_item in items:
            models.OrderItem.objects.create(price=shopping_item.price(),order=order,product=shopping_item.product,shopping_cart_item=shopping_item)
            shopping_item.status = "purchased"
            shopping_item.save()
        return HttpResponseRedirect("/orders/{}".format(order_no))
    return render(request, "ssw/checkout.html", {"user": user, "cart": cart, "items": items} )

@login_required
def orders(request):
    orders = models.Order.objects.filter(owner__pk = request.user.pk)
    return render(request, "ssw/orders.html", {"user": getSowarStockUser(request.user), "orders":orders})

@login_required
def order_details(request, order_no):
    order = get_object_or_404(models.Order, order_no = order_no)
    return render(request, "ssw/order_details.html", {"user": getSowarStockUser(request.user), "order":order})

def other_profile(request, username):
    user = get_object_or_404(models.SowarStockUser, username=username)
    other_user = getSowarStockUser(user)
    return render(request, "ssw/other_profile.html", {"other_profile": other_user} )

@login_required
def profile(request):
    user = getSowarStockUser(request.user)
    email_body = loader.render_to_string("ssw/email_verify_email.html", {"user": user})
    send_mail("Test Email Subject", "", "Sowar Stock", [user.email], False,
              None, None, None, email_body)
    return render(request, "ssw/profile.html", showCorrectMenu(request.user))

@login_required
def products_main(request):
    #models.SowarStockUser.objects.create_user(username="reviewer", password="0000", type="image_reviewer")
    pending = models.Product.objects.filter(owner_id=request.user.id, status="pending_approval")
    approved = models.Product.objects.filter(owner_id=request.user.id, status="approved")
    rejected = models.Product.objects.filter(owner_id=request.user.id, status="rejected")
    return render(request, "ssw/products_main.html", {"user":getSowarStockUser(request.user),"pending":pending,"approved":approved, "rejected": rejected,
                                                      "showcontributormenu": True, "activeDashboardMenu": "products"})

@login_required
def products_new(request):
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
            messages.success(request, "Request to add product has been submitted successfully")
            return HttpResponseRedirect("/products/")
    return render(request, "ssw/products_new.html", {"user":getSowarStockUser(request.user),"form": form,
                                                     "showcontributormenu": True,"activeDashboardMenu": "products"})

def pending_product_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "admin":
            count = models.Product.objects.filter(status="pending_admin_approval").count()
            return JsonResponse({"result":"success", "count": count})
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
            return JsonResponse({"result":"success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})

def pending_faqs_count(request):
    if request.user.is_authenticated:
        user = models.SowarStockUser.objects.get(pk=request.user.pk)
        if user.type == "admin":
            count = models.FaqPersonal.objects.filter(replier__isnull=True).count()
            return JsonResponse({"result":"success", "count": count})
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
    product = get_object_or_404(models.Product, pk=pk)
    product.image.delete_thumbnails()
    product.image.delete(False)
    product.delete()
    messages.success(request, "product deleted")
    return HttpResponseRedirect("/products/")

@login_required
def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = models.SubCategory.objects.filter(main_category = category_id).order_by('name')
    return render(request, 'ssw/subcategories_dropdown_list_options.html', {'subcategories': subcategories})

@login_required
def account_settings(request, **kwargs):
    user = models.Contributor.objects.get(username = "contributor1")
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
    return render(request, 'ssw/account_settings.html', {"user":user,"personal_info_form":personal_info_form,
                                                         "address_form": address_form,"password_form":password_form,
                                                         "public_info_form": public_info_form, "photo_id_form": photo_id_form,
                                                         "showcontributormenu": True, "activeDashboardMenu": "account_settings"})

@login_required
def update_personal_info(request):
    if request.method == "POST":
        user = models.Contributor.objects.get(id=request.user.id)
        clear_profile_image = request.POST.get('profile_image-clear', None)
        if clear_profile_image != None:
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
        user = models.Contributor.objects.get(id=request.user.id)
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
        user = models.Contributor.objects.get(id=request.user.id)
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
        user = models.Contributor.objects.get(id=request.user.id)
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
        user = models.Contributor.objects.get(id=request.user.id)
        photo_id_form = forms.PhotoIdForm(request.POST, request.FILES, instance=user)
        if photo_id_form.is_valid():
            photo_id_form.save()
            models.UserRequest.objects.create(owner = user, body = user.photo_id.url)
            messages.success(request, "Photo ID updated successfully")
        else:
            messages.error(request, photo_id_form.errors)
    return HttpResponseRedirect("/account_settings")

@login_required
def notifications_main(request):
    notifications = request.user.notifications.all()
    return render(request, 'ssw/notifications_main.html', {"user":getSowarStockUser(request.user),"notifications":notifications,
                                                           "showcontributormenu": True,"activeDashboardMenu": "notifications"})

@login_required
def notifications_delete(request,pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.delete()
    messages.success(request, "Notification has been deleted")
    return HttpResponseRedirect("/notifications")

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
    return render(request, 'ssw/product_public_details.html', {"user":getSowarStockUser(request.user),"product": product, "review_form": review_form})

@login_required
def reviews_main(request):
    user = models.Contributor.objects.get(id=request.user.id)
    reviews = models.Review.objects.filter(product__owner = user)
    return render(request, "ssw/reviews_main.html", {"user":getSowarStockUser(request.user),
                                                     "showcontributormenu":True, "activeDashboardMenu": "reviews",
                                                     "reviews": reviews})
@login_required
def faqs_main(request):
    faqs = models.Faq.objects.all()
    personal_faqs = models.FaqPersonal.objects.filter(owner__id = request.user.id)
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
                                                  "form": form, "showcontributormenu": True, "activeDashboardMenu": "faqs"})

@login_required
def collections_main(request):
    collections = models.Collection.objects.filter(owner__pk = request.user.pk)
    return render(request, "ssw/collections_main.html", {"user":getSowarStockUser(request.user), "collections": collections,
                                                  "showcontributormenu": True, "activeDashboardMenu": "collections"})

@login_required
def collections_new(request):
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
                                                  "showcontributormenu": True, "activeDashboardMenu": "collections"})

@login_required
def collections_edit(request,pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    products = models.Product.objects.filter(owner__id=request.user.id, status="approved")
    if request.method == "POST":
        title = request.POST["title"]
        products_pks = request.POST.getlist("products")
        if (title == ""):
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
                                                        "showcontributormenu": True,"activeDashboardMenu": "collections"})

@login_required
def collections_delete(request,pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    collection.delete()
    messages.success(request,"Collection deleted")
    return HttpResponseRedirect("/collections")