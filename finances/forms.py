from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Transaction, Investment
from django.utils import timezone

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer 'user' de kwargs antes de llamar al padre
        self.user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        
        if self.user:
            # Filtrar categorías solo del usuario actual
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        
        # Agregar clases Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
    
    # Campo amount personalizado para manejar mejor los números
    amount = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'inputmode': 'decimal'
        }),
        label="Monto",
        help_text="Ejemplo: 450000.00"
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Descripción de la transacción...'
        })
    )
    
    def clean_amount(self):
        """Limpia y valida el campo amount"""
        data = self.cleaned_data['amount']
        
        # Remover caracteres no numéricos excepto punto
        data = data.replace('$', '').replace(' ', '').replace(',', '')
        
        try:
            # Convertir a Decimal
            amount = Decimal(data)
        except:
            raise forms.ValidationError("Ingresa un monto válido. Ejemplo: 450000.00")
        
        if amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor a 0")
        
        return amount
    
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description', 'transaction_type', 'date']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'value': timezone.now().strftime('%Y-%m-%d')
            }),
            'transaction_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'category': 'Categoría',
            'amount': 'Monto',
            'description': 'Descripción (opcional)',
            'transaction_type': 'Tipo de Transacción',
            'date': 'Fecha',
        }

class CategoryForm(forms.ModelForm):
    COLORS = [
        ('#FF6B6B', 'Rojo'),
        ('#4ECDC4', 'Turquesa'),
        ('#45B7D1', 'Azul claro'),
        ('#96CEB4', 'Verde menta'),
        ('#FFEAA7', 'Amarillo'),
        ('#DDA0DD', 'Ciruela'),
        ('#98D8C8', 'Verde agua'),
        ('#F7DC6F', 'Amarillo dorado'),
        ('#BB8FCE', 'Púrpura'),
        ('#85C1E9', 'Azul cielo'),
        ('#F8C471', 'Naranja'),
        ('#82E0AA', 'Verde claro'),
    ]
    
    ICONS = [
        ('fas fa-home', 'Casa'),
        ('fas fa-car', 'Auto'),
        ('fas fa-utensils', 'Comida'),
        ('fas fa-shopping-cart', 'Compras'),
        ('fas fa-heartbeat', 'Salud'),
        ('fas fa-graduation-cap', 'Educación'),
        ('fas fa-plane', 'Viajes'),
        ('fas fa-gift', 'Regalos'),
        ('fas fa-money-bill-wave', 'Ingresos'),
        ('fas fa-piggy-bank', 'Ahorros'),
        ('fas fa-chart-line', 'Inversiones'),
        ('fas fa-wallet', 'Billetera'),
    ]
    
    # Sobreescribir el campo color para usar un select de colores
    color = forms.ChoiceField(
        choices=COLORS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Sobreescribir el campo icon para usar un select de íconos
    icon = forms.ChoiceField(
        choices=ICONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    budget_limit = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        })
    )
    
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'color', 'icon', 'budget_limit', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'category_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción opcional...'
            }),
        }
        labels = {
            'name': 'Nombre',
            'category_type': 'Tipo de Categoría',
            'color': 'Color',
            'icon': 'Ícono',
            'budget_limit': 'Límite Presupuestal (opcional)',
            'description': 'Descripción (opcional)',
        }

class InvestmentForm(forms.ModelForm):
    initial_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    current_value = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    expected_return = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje de retorno esperado anual",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '-100',
            'max': '1000'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Descripción de la inversión...'
        })
    )
    
    class Meta:
        model = Investment
        fields = ['name', 'investment_type', 'initial_amount', 'current_value', 
                 'description', 'start_date', 'expected_return', 'risk_level', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la inversión'
            }),
            'investment_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'value': timezone.now().strftime('%Y-%m-%d')
            }),
            'risk_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Nombre de la Inversión',
            'investment_type': 'Tipo de Inversión',
            'initial_amount': 'Monto Inicial',
            'current_value': 'Valor Actual',
            'description': 'Descripción (opcional)',
            'start_date': 'Fecha de Inicio',
            'expected_return': 'Retorno Esperado (%)',
            'risk_level': 'Nivel de Riesgo',
            'is_active': '¿Inversión Activa?',
        }

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre completo'
        }),
        label="Nombre"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        }),
        label="Correo Electrónico"
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del mensaje'
        }),
        label="Asunto"
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': 'Escribe tu mensaje aquí...'
        }),
        label="Mensaje"
    )
    
    contact_preference = forms.ChoiceField(
        choices=[
            ('email', 'Correo Electrónico'),
            ('phone', 'Teléfono'),
            ('whatsapp', 'WhatsApp'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Preferencia de Contacto",
        initial='email'
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        }),
        label="Teléfono (opcional)"
    )

class BudgetForm(forms.Form):
    month = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'month',
            'class': 'form-control'
        }),
        label="Mes"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Categoría"
    )
    
    allocated_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        label="Monto Asignado"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

class FilterForm(forms.Form):
    DATE_RANGES = [
        ('today', 'Hoy'),
        ('week', 'Esta semana'),
        ('month', 'Este mes'),
        ('year', 'Este año'),
        ('custom', 'Personalizado'),
    ]
    
    date_range = forms.ChoiceField(
        choices=DATE_RANGES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'date-range-select'
        }),
        label="Rango de Fechas",
        initial='month'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'start-date'
        }),
        label="Fecha Inicio"
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'end-date'
        }),
        label="Fecha Fin"
    )
    
    transaction_type = forms.ChoiceField(
        choices=[('', 'Todos')] + Transaction.TRANSACTION_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Tipo de Transacción"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Categoría"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

class QuickTransactionForm(forms.ModelForm):
    """Formulario rápido para transacciones desde el dashboard"""
    
    def __init__(self, user=None, *args, **kwargs):
        super(QuickTransactionForm, self).__init__(*args, **kwargs)
        if user:
            # Solo mostrar categorías de gastos para transacciones rápidas
            self.fields['category'].queryset = Category.objects.filter(
                user=user, 
                category_type='EXPENSE'
            )
        
        # Hacer el formulario más compacto
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control form-control-sm'
    
    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'description']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Descripción breve...'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control form-control-sm'
            }),
        }
        labels = {
            'category': '',
            'amount': '',
            'description': '',
        }

class ProfileUpdateForm(forms.ModelForm):

    """Formulario para actualizar perfil de usuario"""
    
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
        }

        