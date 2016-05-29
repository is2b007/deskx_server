from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/', views.login_view),
    url(r'^session/create/', views.create_session),
    url(r'^session/join/', views.join_session),
    url(r'^session/list/', views.get_list),
    url(r'^session/update/', views.update_session),
    url(r'^session/object/store/', views.object_store),
    url(r'^session/object/get/(?P<content_type>[^/]+)/$', views.get_objects),
]
