from django.conf.urls import url

from ssw.ajax import views

urlpatterns = [
    url(r'^load_subcategories/$', views.load_subcategories),
    url(r'^pending_products_count/$', views.pending_product_count),
    url(r'^pending_requests_count/$', views.pending_requests_count),
    url(r'^pending_faqs_count/$', views.pending_faqs_count),
    url(r'^notifications_undread_to_read/$', views.notifications_undread_to_read),
    url(r'^cart_items_count/$', views.cart_items_count),
    url(r'^pending_reviews_count/$', views.pending_reviews_count),
    url(r'^reviews_unread_to_read/$', views.reviews_undread_to_read),
    url(r'^load_payment_amount/$', views.load_payment_amount),
    url(r'^sign_s3/$', views.sign_s3),
    url(r'^upload_result/$', views.upload_file_result),
]