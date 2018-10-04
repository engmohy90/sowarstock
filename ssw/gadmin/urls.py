from django.conf.urls import url

from ssw.gadmin import views

urlpatterns = [
    url(r'^users/$', views.users),
    url(r'^products/$', views.products_main),
    url(r'^products/(?P<pk>\d+)/approve/$', views.product_approve, name='product_approve'),
    url(r'^products/(?P<pk>\d+)/reject/$', views.product_reject, name='product_reject'),
    url(r'^faqs/$', views.faqs_main, name='faqs_main'),
    url(r'^faqs/new/$', views.faqs_new, name='faqs_new'),
    url(r'^faqs/(?P<pk>\d+)/edit/$', views.faqs_edit, name='faqs_edit'),
    url(r'^faqs/(?P<pk>\d+)/delete/$', views.faqs_delete, name='faqs_delete'),
    url(r'^pfaqs/(?P<pk>\d+)/reply/$', views.personal_faqs_reply, name='personal_faqs_reply'),
    url(r'^requests/$', views.requests_main, name='requests_main'),
    url(r'^requests/(?P<pk>\d+)/approve/$', views.requests_approve, name='requests_approve'),
    url(r'^requests/(?P<pk>\d+)/reject/$', views.requests_reject, name='requests_reject'),
    url(r'^reviews/$', views.reviews_main, name='reviews_main'),
    url(r'^reviews/(?P<pk>\d+)/delete/$', views.reviews_delete, name='reviews_delete'),
    url(r'^notices/$', views.notifications_main, name='notifications_main'),
    url(r'^categories/$', views.categories_main, name='categories_main'),
    url(r'^categories/new_category/$', views.categories_new, name='categories_new'),
    url(r'^categories/edit_category/(?P<pk>\d+)/$', views.categories_edit, name='categories_edit'),
    url(r'^categories/delete_category/(?P<pk>\d+)/$', views.categories_delete, name='categories_delete'),
    url(r'^categories/new_subcategory/$', views.subcategories_new, name='subcategories_new'),
    url(r'^categories/edit_subcategory/(?P<pk>\d+)/$', views.subcategories_edit, name='subcategories_edit'),
    url(r'^categories/delete_subcategory/(?P<pk>\d+)/$', views.subcategories_delete, name='subcategories_delete'),
    url(r'^legal/$', views.legal_main, name='admin_legal_main'),
    url(r'^legal/(?P<pk>\d+)/edit/$', views.legal_edit, name='admin_legal_edit'),
]