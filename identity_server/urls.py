from django.urls import path
import identity_server.views as views

urlpatterns = [
    path('is_authenticated', views.is_authenticated),
    # GET
    path('login', views.login),
    # GET
    path('register', views.register),
    # POST
    path('token', views.create_token),
    # POST
    path('logout', views.logout),
    # POST
    path('revoke', views.revoke),
    # POST
    path('introspect', views.introspect_token),
    # GET
    path('contacts', views.get_contacts),
    # GET
    path('contacts/<int:user_id>', views.get_user_contacts),
    # GET
    path('user', views.get_user),
    # GET
    path('users', views.get_users),
    # PUT
    path('users/<int:user_id>', views.update_or_delete_user),
    # POST
    path('create_user', views.create_user),
    # GET
    path('worker_shifts/<int:user_id>', views.get_workers_shift),
    # GET
    path('get_authorized_apps', views.get_authorized_apps),
    # GET
    path('is_active', views.is_active)
]
