from django.conf.urls import url

from ssw.fadmin import views

urlpatterns = [
    url(r'^earnings/$', views.earnings_main, name="fadmin_earnings_main"),
    url(r'^earnings/new-payment/$', views.payment_new, name="fadmin_payment_new"),
]