from django.conf.urls import url
from . import views

urlpatterns = [ 
    url(r'^article/create/(?P<entrez_id>\d+)/$', views.article_create, name = 'article_create'),
]
