from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render

from ssw import models
from ssw.views import getSowarStockUser


@login_required
def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = models.SubCategory.objects.filter(main_category=category_id).order_by('name')
    return render(request, 'ssw/subcategories_dropdown_list_options.html', {'subcategories': subcategories})


@login_required
def load_payment_amount(request):
    contributor_pk = request.GET.get('pk')
    try:
        contributor = models.Contributor.objects.get(pk=contributor_pk)
        try:
            owed = models.Earning.objects.filter(type="contributor", payment=None, contributor=contributor).aggregate(Sum('amount'))
            owed_amount = round(owed['amount__sum'], 2)
        except:
            owed_amount = 0

        return JsonResponse({"result": "success", "amount":owed_amount})
    except:
        return JsonResponse({"result": "error", "msg": "no contributor"})


@login_required
def notifications_undread_to_read(request):
    notifications = request.user.notifications.unread()
    notifications.mark_all_as_read()
    return JsonResponse({"result": "success"})


def pending_product_count(request):
    if request.user.is_authenticated:
        user = getSowarStockUser(request.user)
        if user.type == "admin":
            count = models.Product.objects.filter(status="pending_admin_approval").count() + models.Product.objects.filter(requested_to_archive=True).count()
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
        user = getSowarStockUser(request.user)
        if user.type == "admin":
            count = models.UserRequest.objects.filter(status="pending_approval").count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


def pending_faqs_count(request):
    if request.user.is_authenticated:
        user = getSowarStockUser(request.user)
        if user.type == "admin":
            count = models.FaqPersonal.objects.filter(replier__isnull=True).count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


def cart_items_count(request):
    if request.user.is_authenticated:
        user = getSowarStockUser(request.user)
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
def pending_reviews_count(request):
    if request.user.is_authenticated:
        user = getSowarStockUser(request.user)
        if user.type == "contributor":
            count = models.Review.objects.filter(product__owner=user, read_by_product_owner=False).count()
            return JsonResponse({"result": "success", "count": count})
        elif user.type == "admin":
            count = models.Review.objects.filter(read_by_admin=False).count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no contributor or admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})


@login_required
def reviews_undread_to_read(request):
    user = getSowarStockUser(request.user)
    if user.type == "contributor":
        reviews = models.Review.objects.filter(product__owner=user, read_by_product_owner=False)
        for review in reviews:
            review.read_by_product_owner = True
            review.save()
    elif user.type == "admin":
        reviews = models.Review.objects.filter(read_by_admin=False)
        for review in reviews:
            review.read_by_admin = True
            review.save()
    return JsonResponse({"result": "success"})


@login_required
def pending_sample_products_count(request):
    if request.user.is_authenticated:
        user = getSowarStockUser(request.user)
        if user.type == "image_reviewer":
            count = models.SampleProduct.objects.filter(viewed_by_reviewer=False).count()
            return JsonResponse({"result": "success", "count": count})
        elif user.type == "admin":
            count = models.SampleProduct.objects.filter(viewed_by_admin=False).count()
            return JsonResponse({"result": "success", "count": count})
        else:
            return JsonResponse({"result": "error", "msg": "no reviewer or admin"})
    else:
        return JsonResponse({"result": "error", "msg": "no user"})
