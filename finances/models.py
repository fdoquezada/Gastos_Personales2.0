from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    CATEGORY_TYPES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Gasto'),
        ('INVESTMENT', 'Inversión'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    icon = models.CharField(max_length=50, default='fas fa-wallet')
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCOME', 'Ingreso'),
        ('EXPENSE', 'Gasto'),
        ('INVESTMENT', 'Inversión'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField(default=timezone.now)
    is_recurring = models.BooleanField(default=False)
    recurrence_interval = models.CharField(max_length=20, blank=True, choices=[
        ('DAILY', 'Diario'),
        ('WEEKLY', 'Semanal'),
        ('MONTHLY', 'Mensual'),
        ('YEARLY', 'Anual'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.description}: ${self.amount}"

class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('STOCK', 'Acciones'),
        ('BOND', 'Bonos'),
        ('REAL_ESTATE', 'Bienes Raíces'),
        ('CRYPTO', 'Criptomonedas'),
        ('SAVINGS', 'Ahorros'),
        ('OTHER', 'Otro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    name = models.CharField(max_length=100)
    investment_type = models.CharField(max_length=20, choices=INVESTMENT_TYPES)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    expected_return = models.DecimalField(max_digits=5, decimal_places=2, help_text="Porcentaje de retorno esperado")
    risk_level = models.CharField(max_length=20, choices=[
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ${self.current_value}"
    
    def roi(self):
        """Return on Investment"""
        return ((self.current_value - self.initial_amount) / self.initial_amount) * 100

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.DateField()
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month']
    
    def __str__(self):
        return f"{self.category.name} - {self.month.strftime('%B %Y')}"
    
    def remaining(self):
        return self.allocated_amount - self.spent_amount
    
    def spent_percentage(self):
        if self.allocated_amount == 0:
            return 0
        return (self.spent_amount / self.allocated_amount) * 100