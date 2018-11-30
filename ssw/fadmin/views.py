from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import loader
from notifications.signals import notify

from ssw import models, forms
from ssw.views import getSowarStockUser, showCorrectMenu

@login_required
def earnings_main(request):
    user = getSowarStockUser(request.user)
    if user.type == "financial_admin":
        searnings = models.Earning.objects.filter(type="sowarstock")
        cearnings = models.Earning.objects.filter(type="contributor")
        return render(request, "ssw/fadmin/earnings_main.html", {"user": user, "searnings": searnings, "cearnings": cearnings,
                                                                 "activeDashboardMenu": "earnings", **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")

@login_required
def payment_new(request):
    user = getSowarStockUser(request.user)
    if user.type == "financial_admin":
        form = forms.PaymentForm()

        if request.method == "POST":
            form = forms.PaymentForm(request.POST, request.FILES)
            if form.is_valid():
                payment = form.save(commit=False)
                try:
                    earnings = models.Earning.objects.filter(type="contributor", payment=None,
                                                             contributor=payment.contributor)
                    owed = earnings.aggregate(Sum('amount'))
                    owed_amount = round(owed['amount__sum'], 2)
                except:
                    owed_amount = 0
                payment.amount = owed_amount
                payment.save()

                for earning in earnings:
                    earning.payment = payment
                    earning.save()

                messages.success(request, "Payment has been successfully made")
                # notify contributor and send email
                email_body = loader.render_to_string("ssw/email_new_payment.html", {"payment": payment})
                send_mail("عملية دفع جديدة لك", "", "Sowarstock", [payment.contributor.email], False,
                          None, None, None, email_body)
                notify.send(request.user, recipient=payment.contributor, level="success",
                            verb='You got paid ${}'.format(payment.amount))
                return HttpResponseRedirect("/fadmin/earnings")

        return render(request, "ssw/fadmin/payment_new.html", {"user": user, "form": form,
                                                               "activeDashboardMenu": "earnings",
                                                                **showCorrectMenu(request.user)})
    else:
        messages.error(request, "You are not authorized to view this page !")
        return HttpResponseRedirect("/")
