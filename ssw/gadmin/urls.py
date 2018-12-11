from django.conf.urls import url

from ssw.gadmin import views

urlpatterns = [
    url(r'^users/$', views.users, name="admin_users"),
    url(r'^users/(?P<username>[\w\-]+)/suspend/$', views.suspend_account, name="admin_users_suspend"),
    url(r'^users/(?P<username>[\w\-]+)/unsuspend/$', views.unsuspend_account, name="admin_users_unsuspend"),
    url(r'^products/$', views.products_main, name="admin_products_main"),
    url(r'^products/(?P<pk>\d+)/approve/$', views.product_approve, name='product_approve'),
    url(r'^products/(?P<pk>\d+)/reject/$', views.product_reject, name='product_reject'),
    url(r'^products/(?P<pk>\d+)/archive/$', views.product_archive, name='admin_product_archive'),
    url(r'^collections/$', views.collections_main, name="admin_collections_main"),
    url(r'^collections/new/$', views.collections_new, name="admin_collections_new"),
    url(r'^collections/(?P<pk>\d+)/edit/$', views.collections_edit, name="admin_collections_edit"),
    url(r'^collections/(?P<pk>\d+)/delete/$', views.collections_delete, name="admin_collections_delete"),
    url(r'^faqs/$', views.faqs_main, name='faqs_main'),
    url(r'^faqs/new/$', views.faqs_new, name='faqs_new'),
    url(r'^faqs/(?P<pk>\d+)/edit/$', views.faqs_edit, name='faqs_edit'),
    url(r'^faqs/(?P<pk>\d+)/delete/$', views.faqs_delete, name='faqs_delete'),
    url(r'^pfaqs/(?P<pk>\d+)/reply/$', views.personal_faqs_reply, name='personal_faqs_reply'),
    url(r'^requests/$', views.requests_main, name='requests_main'),
    url(r'^requests/(?P<pk>\d+)/$', views.requests_profile, name='requests_profile'),
    url(r'^requests/(?P<pk>\d+)/approve/$', views.requests_approve, name='requests_approve'),
    url(r'^requests/(?P<pk>\d+)/reject/$', views.requests_reject, name='requests_reject'),
    url(r'^reviews/$', views.reviews_main, name='reviews_main'),
    url(r'^reviews/(?P<pk>\d+)/delete/$', views.reviews_delete, name='reviews_delete'),
    url(r'^notices/$', views.notifications_main, name='notifications_main'),
    url(r'^notices/new$', views.notifications_new, name='admin_notifications_new'),
    url(r'^categories/$', views.categories_main, name='categories_main'),
    url(r'^categories/new_category/$', views.categories_new, name='categories_new'),
    url(r'^categories/edit_category/(?P<pk>\d+)/$', views.categories_edit, name='categories_edit'),
    url(r'^categories/delete_category/(?P<pk>\d+)/$', views.categories_delete, name='categories_delete'),
    url(r'^categories/new_subcategory/$', views.subcategories_new, name='subcategories_new'),
    url(r'^categories/edit_subcategory/(?P<pk>\d+)/$', views.subcategories_edit, name='subcategories_edit'),
    url(r'^categories/delete_subcategory/(?P<pk>\d+)/$', views.subcategories_delete, name='subcategories_delete'),
    url(r'^legal/$', views.legal_main, name='admin_legal_main'),
    url(r'^legal/(?P<pk>\d+)/edit/$', views.legal_edit, name='admin_legal_edit'),
    url(r'^orders/$', views.orders_main, name='admin_orders_main'),
    url(r'^orders/(?P<order_no>\d+)/$', views.order_details, name="admin_order_details"),
    url(r'^earnings/(?P<pk>\d+)/new-payment/$', views.payment_new, name="admin_payment_new"),
    url(r'^earnings/$', views.earnings_main, name='admin_earnings_main'),
    url(r'^featured/$', views.featured_main, name='admin_featured_main'),
    url(r'^featured/contributor/new$', views.featured_contributor_edit, name='admin_featured_contributor_edit'),
    url(r'^featured/product/new$', views.featured_product_edit, name='admin_featured_product_edit'),
    url(r'^search-keywords/$', views.search_keywords_main, name="admin_search_keywords_main"),
    url(r'^search-keywords/new/$', views.search_keyword_synonyms_new, name="admin_search_keyword_synonyms_new"),
    url(r'^search-keywords/edit/(?P<pk>\d+)/$', views.search_keyword_synonyms_edit, name='admin_search_keyword_synonyms_edit'),
    url(r'^search-keywords/(?P<pk>\d+)/delete/$', views.search_keyword_synonyms_delete, name='admin_search_keyword_synonyms_delete'),
    url(r'^reports/$', views.reports_main, name="admin_reports_main"),
    url(r'^site-settings/$', views.site_settings_main, name="admin_site_settings_main"),
]