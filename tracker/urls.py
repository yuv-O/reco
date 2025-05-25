from django.contrib.auth import views as auth_views
from django.urls import path
from .views import dashboard
from . import views
from .views import CustomPasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth import views as auth_views
from .views import register



urlpatterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-budget/', views.add_budget, name='add_budget'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('', dashboard, name='dashboard'),
     path('register/', register, name='register'),
    path('login/', views.login_view, name='login'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('logout/', views.logout_view, name='logout'),
]
