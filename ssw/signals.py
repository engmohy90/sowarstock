from django.core.mail import send_mail
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.template import loader
from notifications.signals import notify
import random

from . import models
def show_me_the_money(sender, **kwargs):
    print("in show me the money")
    """signal function"""
    ipn_obj = sender

    username = ipn_obj.custom.split(":")[0]
    user = get_object_or_404(models.Client, username=username)
    cart = get_object_or_404(models.ShoppingCart, owner=user)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != "sowarstock.co@gmail.com":
            # Not a valid payment
            return
        if ipn_obj.mc_gross != cart.total():
            return

        items = models.ShoppingCartItem.objects.filter(cart=cart, status="in_cart")

        order_no = "%08d" % random.randint(1, 100000000)
        order = models.Order.objects.create(order_no=order_no, owner=user, total=cart.total())
        for shopping_item in items:
            order_item = models.OrderItem.objects.create(price=shopping_item.price(), order=order,
                                                         product=shopping_item.product,
                                                         shopping_cart_item=shopping_item)
            shopping_item.status = "purchased"
            shopping_item.save()
            if order_item.product.exclusive:
                earning = models.Earning.objects.create(type="contributor", order_item=order_item,
                                                        contributor=order_item.product.owner,
                                                        amount=round(order_item.price * 0.6, 2))
                models.Earning.objects.create(type="sowarstock", order_item=order_item,
                                              amount=round(order_item.price * 0.4, 2))
            else:
                earning = models.Earning.objects.create(type="contributor", order_item=order_item,
                                                        contributor=order_item.product.owner,
                                                        amount=round(order_item.price * 0.4, 2))
                models.Earning.objects.create(type="sowarstock", order_item=order_item,
                                              amount=round(order_item.price * 0.6, 2))

            # send email to contributor
            admin = models.SowarStockUser.objects.get(type="admin")
            notify.send(admin, recipient=earning.contributor, level="success",
                        verb=_('You earned ${} from your product {}').format(earning.amount,
                                                                          earning.order_item.product.public_id))
            email_body = loader.render_to_string("ssw/email_new_earning.html", {"earning": earning})
            send_mail("مكسب جديد", "", "Sowarstock", [earning.contributor.email], False,
                      None, None, None, email_body)

        # send email to client
        """
        email_body = loader.render_to_string("ssw/email_order_is_ready.html", {"user": user, "order": order})
        send_mail("طلبك جاهز", "", "Sowarstock", [user.email], False,
                  None, None, None, email_body)
        """

    else:
        print("not working")


valid_ipn_received.connect(show_me_the_money)
