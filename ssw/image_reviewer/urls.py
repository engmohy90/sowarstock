from django.conf.urls import url

from ssw.image_reviewer import views

urlpatterns = [
    url(r'^products/$', views.products_main, name="reviewer_products_main"),
    url(r'^products/(?P<pk>\d+)/approve/$', views.product_approve, name='reviewer_product_approve'),
    url(r'^products/(?P<pk>\d+)/reject/$', views.product_reject, name='reviewer_product_reject'),
]