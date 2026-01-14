from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='finances/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard y páginas principales
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('categories/', views.categories, name='categories'),
    path('investments/', views.investments, name='investments'),
    path('reports/', views.reports, name='reports'),
    path('contact/', views.contact, name='contact'),
    
    # Acciones
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('investments/delete/<int:investment_id>/', views.delete_investment, name='delete_investment'),
    
    # API para gráficos
    path('api/financial-data/', views.get_financial_data, name='financial_data'),
    path('api/category-spending/', views.get_category_spending, name='category_spending'),
]