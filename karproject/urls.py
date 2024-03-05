from django.contrib import admin
from django.urls import path, include
from account import views as account_views
from account import auth_views as auth_views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "USERMANAGEMENT"
admin.site.site_title = "ADMIN PORTAL"
admin.site.index_title = "Carrington welcomes you!!!"

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('',account_views.home, name="home"),
    path('users/<int:pk>/', account_views.UserDetailView.as_view(), name="user_detail"),

    path('sign-in/', auth_views.login_view, name="login"),
    path('sign-out/', auth_views.logout_view, name="logout"),
    path('logout-success/', auth_views.logout_success, name="logout-success"),
    path('register/', auth_views.signup, name="register"),
    path('profile/', auth_views.profile, name="profile"),

    

    
    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), 
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), 
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
     name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
    name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
      name='password_reset_complete'),
    
]



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)