import notifications.urls
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.landing),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^signup/$', views.signup),
    url(r'^login/$', views.signin),
    url(r'^logout/$', views.logout_view),
    url(r'^search/$', views.search),
    url(r'^photos/$', views.photos_main, name="photos_main"),
    url(r'^vectors/$', views.vectors_main, name="vectors_main"),
    url(r'^calligraphy/$', views.calligraphy_main, name="calligraphy_main"),
    url(r'^about/$', views.about, name="about"),
    url(r'^contact/$', views.contact, name="contact"),
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^profile/(?P<username>[\w\-]+)/$', views.other_profile, name="other_profile"),
    url(r'^products/$', views.products_main),
    url(r'^products/new/$', views.products_new),
    url(r'^products/(?P<pk>\d+)/delete/$', views.product_delete, name='product_delete'),
    url(r'^ajax/load_subcategories/$', views.load_subcategories),
    url(r'^ajax/pending_products_count/$', views.pending_product_count),
    url(r'^ajax/pending_requests_count/$', views.pending_requests_count),
    url(r'^ajax/pending_faqs_count/$', views.pending_faqs_count),
    url(r'^ajax/notifications_undread_to_read/$', views.notifications_undread_to_read),
    url(r'^ajax/cart_items_count/$', views.cart_items_count),
    url(r'^account_settings/$', views.account_settings, kwargs={},name="account_settings"),
    url(r'^update_personal_info/$', views.update_personal_info),
    url(r'^update_address/$', views.update_address),
    url(r'^update_password/$', views.update_password),
    url(r'^update_public_info/$', views.update_public_info),
    url(r'^update_photo_id/$', views.update_photo_id),
    url(r'^notifications/$', views.notifications_main),
    url(r'^notifications/(?P<pk>\d+)/delete/$', views.notifications_delete, name="notifications_delete"),
    url(r'^products/public/(?P<public_id>\d+)/$', views.product_public_details, name="product_public"),
    url(r'^add_to_cart/$', views.add_to_cart, name="add_to_cart"),
    url(r'^shopping-cart/$', views.shopping_cart_main, name="shopping_cart_main"),
    url(r'^update_cart/$', views.update_cart, name="update_cart"),
    url(r'^remove_from_cart/(?P<pk>\d+)/$', views.remove_from_cart, name="remove_from_cart"),
    url(r'^checkout/$', views.checkout, name="checkout"),
    url(r'^orders/$', views.orders, name="orders"),
    url(r'^orders/(?P<order_no>\d+)/$', views.order_details, name="order_details"),
    url(r'^collections/$', views.collections_main),
    url(r'^collections/new/$', views.collections_new, name="collections_new"),
    url(r'^collections/(?P<pk>\d+)/edit/$', views.collections_edit, name="collections_edit"),
    url(r'^collections/(?P<pk>\d+)/delete/$', views.collections_delete, name="collections_delete"),
    url(r'^reviews/$', views.reviews_main),
    url(r'^faqs/$', views.faqs_main),
    url(r'^admin/', include('ssw.gadmin.urls')),
    url(r'^reviewer/', include('ssw.image_reviewer.urls')),
    url(r'^legal/', include('ssw.legal.urls')),
]