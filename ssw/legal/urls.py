from django.conf.urls import url

from ssw.legal import views

urlpatterns = [
    url(r'^contributor/$', views.contributor, name="legal_contributor"),
    url(r'^license/$', views.license, name='legal_license'),
    url(r'^privacy/$', views.privacy, name='legal_privacy'),
    url(r'^terms/$', views.terms, name='legal_terms'),
]