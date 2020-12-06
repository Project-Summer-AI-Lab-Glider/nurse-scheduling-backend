from django.urls import path
import identity_server.views as views

urlpatterns = [
    # GET
    path('login', views.login),
    # POST
    path('token', views.create_token),
    # POST
    path('revoke', views.revoke_token),
    # POST
    path('introspect', views.introspect_token),
    # GET
    path('user', views.get_user_info)

]
