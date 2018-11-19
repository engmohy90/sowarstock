import notifications.urls
from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.landing),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^signup/$', views.signup, name="signup"),
    url(r'^login/$', views.signin, name="login"),
    url(r'^logout/$', views.logout_view),
    url(r'^thanks-for-joining/$', views.thanks_for_joining, name="thanks_for_joining"),
    url(r'^email/verify/(?P<uuid>[\w\-]+)/$', views.verfiy_email, name="verify_email"),
    url(r'^recover/$', views.recover_account, name="recover_account"),
    url(r'^reset-password/(?P<uuid>[\w\-]+)/$', views.reset_password, name="reset_password"),
    url(r'^search/$', views.search, name="search"),
    url(r'^photos/$', views.photos_main, name="photos_main"),
    url(r'^vectors/$', views.vectors_main, name="vectors_main"),
    url(r'^calligraphy/$', views.calligraphy_main, name="calligraphy_main"),
    url(r'^about/$', views.about, name="about"),
    url(r'^contact/$', views.contact, name="contact"),
    url(r'^complete-registration/$', views.complete_registration, name="complete_registration"),
    url(r'^resend-email-activation/$', views.resend_email_activation, name="resend_email_activation"),
    url(r'^profile/$', views.profile, name="profile"),
    url(r'^profile/(?P<username>[\w\-]+)/$', views.other_profile, name="other_profile"),
    url(r'^profile/(?P<username>[\w\-]+)/products/$', views.profile_products, name="profile_products"),
    url(r'^profile/(?P<username>[\w\-]+)/products/(?P<public_id>\d+)/$', views.profile_product_details, name="profile_product_details"),
    url(r'^products/$', views.products_main, name="products"),
    url(r'^products/new/$', views.products_new),
    url(r'^products/pending/(?P<public_id>\d+)/$', views.product_pending, name='product_pending'),
    url(r'^products/details/(?P<public_id>\d+)/$', views.product_details, name='product_details'),
    url(r'^products/(?P<pk>\d+)/request-to-archive/$', views.product_request_to_archive, name='product_request_to_archive'),
    url(r'^account_settings/$', views.account_settings, kwargs={},name="account_settings"),
    url(r'^update_personal_info/$', views.update_personal_info, name="update_personal_info"),
    url(r'^update_address/$', views.update_address, name="update_address"),
    url(r'^update_password/$', views.update_password, name="update_password"),
    url(r'^update_public_info/$', views.update_public_info, name="update_public_info"),
    url(r'^update_photo_id/$', views.update_photo_id, name="update_photo_id"),
    url(r'^update_payment_method/$', views.update_payment_method, name="update_payment_method"),
    url(r'^notifications/$', views.notifications_main),
    url(r'^notifications/(?P<pk>\d+)/delete/$', views.notifications_delete, name="notifications_delete"),
    url(r'^products/public/(?P<public_id>\d+)/$', views.product_public_details, name="product_public"),
    url(r'^add_to_cart/$', views.add_to_cart, name="add_to_cart"),
    url(r'^shopping-cart/$', views.shopping_cart_main, name="shopping_cart_main"),
    url(r'^update_cart/$', views.update_cart, name="update_cart"),
    url(r'^remove_from_cart/(?P<pk>\d+)/$', views.remove_from_cart, name="remove_from_cart"),
    url(r'^checkout/$', views.checkout, name="checkout"),
    url(r'^thanks-for-payment/$', views.thanks_for_payment, name="thanks_for_payment"),
    url(r'^orders/$', views.orders, name="orders"),
    url(r'^orders/(?P<order_no>\d+)/$', views.order_details, name="order_details"),
    url(r'^collections/$', views.collections_main),
    url(r'^collections/new/$', views.collections_new, name="collections_new"),
    url(r'^collections/(?P<pk>\d+)/edit/$', views.collections_edit, name="collections_edit"),
    url(r'^collections/(?P<pk>\d+)/delete/$', views.collections_delete, name="collections_delete"),
    url(r'^reviews/$', views.reviews_main),
    url(r'^faqs/$', views.faqs_main),
    url(r'^earnings/$', views.earnings_main, name="earnings_main"),
    url(r'^ajax/', include('ssw.ajax.urls')),
    url(r'^admin/', include('ssw.gadmin.urls')),
    url(r'^reviewer/', include('ssw.image_reviewer.urls')),
    url(r'^fadmin/', include('ssw.fadmin.urls')),
    url(r'^legal/', include('ssw.legal.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^progressbarupload/', include('progressbarupload.urls')),
]