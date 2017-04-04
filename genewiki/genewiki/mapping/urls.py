from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^wiki/(?P<entrez_id>\d+)/$', views.wiki_mapping, name='wiki_mapping'),
]
