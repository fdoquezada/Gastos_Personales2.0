from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from django.http import JsonResponse
from django.db import models

from .models import Category, Transaction, Investment, Budget
from .forms import (
    UserRegistrationForm, 
    TransactionForm, 
    CategoryForm, 
    InvestmentForm,
    ContactForm
)

@login_required
def dashboard(request):
    # Get current month data
    today = timezone.now()
    first_day = today.replace(day=1)
    last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Monthly totals
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='INCOME',
        date__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='EXPENSE',
        date__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    monthly_investments = Transaction.objects.filter(
        user=request.user,
        transaction_type='INVESTMENT',
        date__range=[first_day, last_day]
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    
    # Category breakdown
    expense_categories = Category.objects.filter(
        user=request.user,
        category_type='EXPENSE'
    )
    
    category_data = []
    for category in expense_categories:
        total = Transaction.objects.filter(
            user=request.user,
            category=category,
            transaction_type='EXPENSE',
            date__range=[first_day, last_day]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        if total > 0:
            category_data.append({
                'name': category.name,
                'total': float(total),
                'color': category.color
            })
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')[:10]
    
    # Investment summary
    investments = Investment.objects.filter(user=request.user, is_active=True)
    total_investment_value = investments.aggregate(Sum('current_value'))['current_value__sum'] or Decimal('0')
    total_investment_initial = investments.aggregate(Sum('initial_amount'))['initial_amount__sum'] or Decimal('0')
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_investments': monthly_investments,
        'monthly_balance': monthly_income - monthly_expenses - monthly_investments,
        'category_data': json.dumps(category_data),
        'recent_transactions': recent_transactions,
        'investments': investments,
        'total_investment_value': total_investment_value,
        'total_investment_initial': total_investment_initial,
        'investment_roi': ((total_investment_value - total_investment_initial) / total_investment_initial * 100 
                          if total_investment_initial > 0 else 0),
        'current_month': today.strftime('%B %Y')
    }
    
    return render(request, 'finances/dashboard.html', context)

@login_required
def transactions(request):
    """
    Vista principal para manejar todas las transacciones:
    - Mostrar lista de transacciones
    - Aplicar filtros
    - Agregar nuevas transacciones
    - Calcular totales
    """
    
    # ============================================
    # 1. OBTENER Y FILTRAR TRANSACCIONES
    # ============================================
    
    # Obtener todas las transacciones del usuario ordenadas por fecha (más reciente primero)
    transactions_list = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')
    
    # Obtener todas las categorías del usuario para el filtro y formulario
    categories = Category.objects.filter(user=request.user).order_by('name')
    
    # Inicializar diccionario para filtros
    filters = {}
    
    # ============================================
    # 2. APLICAR FILTROS DESDE GET PARAMETERS
    # ============================================
    
    # Filtro por tipo de transacción
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions_list = transactions_list.filter(transaction_type=transaction_type)
        filters['type'] = transaction_type
    
    # Filtro por categoría
    category_id = request.GET.get('category', '')
    if category_id:
        transactions_list = transactions_list.filter(category_id=category_id)
        filters['category'] = category_id
    
    # Filtro por fecha de inicio
    start_date = request.GET.get('start_date', '')
    if start_date:
        try:
            transactions_list = transactions_list.filter(date__gte=start_date)
            filters['start_date'] = start_date
        except:
            messages.warning(request, "Fecha de inicio no válida")
    
    # Filtro por fecha de fin
    end_date = request.GET.get('end_date', '')
    if end_date:
        try:
            transactions_list = transactions_list.filter(date__lte=end_date)
            filters['end_date'] = end_date
        except:
            messages.warning(request, "Fecha de fin no válida")
    
    # ============================================
    # 3. MANEJAR FORMULARIO DE NUEVA TRANSACCIÓN
    # ============================================
    
    if request.method == 'POST':
        # Crear formulario con datos POST y usuario actual
        form = TransactionForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # Guardar transacción sin commit para agregar usuario
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                
                messages.success(request, '✅ Transacción agregada exitosamente.')
                return redirect('transactions')
                
            except Exception as e:
                messages.error(request, f'❌ Error al guardar la transacción: {str(e)}')
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        # Si es GET, crear formulario vacío
        form = TransactionForm(user=request.user)
    
    # ============================================
    # 4. CALCULAR TOTALES Y ESTADÍSTICAS
    # ============================================
    
    # Calcular totales para las transacciones filtradas
    totals = transactions_list.aggregate(
        total_income=Sum('amount', filter=models.Q(transaction_type='INCOME')),
        total_expenses=Sum('amount', filter=models.Q(transaction_type='EXPENSE')),
        total_investments=Sum('amount', filter=models.Q(transaction_type='INVESTMENT'))
    )
    
    # Obtener valores o 0 si son None
    total_income = totals['total_income'] or Decimal('0')
    total_expenses = totals['total_expenses'] or Decimal('0')
    total_investments = totals['total_investments'] or Decimal('0')
    
    # Calcular balance
    balance = total_income - total_expenses - total_investments
    
    # Calcular estadísticas adicionales
    transaction_count = transactions_list.count()
    
    # Calcular promedio de transacciones
    avg_transaction = Decimal('0')
    if transaction_count > 0:
        total_all = total_income + total_expenses + total_investments
        avg_transaction = total_all / transaction_count
    
    # ============================================
    # 5. DATOS PARA GRÁFICOS (opcional)
    # ============================================
    
    # Distribución por categoría (últimos 30 días)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_transactions = transactions_list.filter(date__gte=thirty_days_ago)
    
    category_totals = []
    for category in categories:
        cat_total = recent_transactions.filter(
            category=category,
            transaction_type='EXPENSE'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        if cat_total > 0:
            category_totals.append({
                'name': category.name,
                'total': float(cat_total),
                'color': category.color,
                'icon': category.icon
            })
    
    # ============================================
    # 6. PREPARAR CONTEXTO PARA EL TEMPLATE
    # ============================================
    
    context = {
        # Lista principal
        'transactions': transactions_list,
        'form': form,
        'categories': categories,
        
        # Filtros activos
        'filters': filters,
        
        # Totales y estadísticas
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_investments': total_investments,
        'balance': balance,
        'transaction_count': transaction_count,
        'avg_transaction': avg_transaction,
        
        # Datos para gráficos
        'category_totals': json.dumps(category_totals),
        'category_data': category_totals,  # También disponible sin JSON
        
        # Fechas útiles
        'today': timezone.now().date(),
        'thirty_days_ago': thirty_days_ago.date(),
        
        # Mensajes adicionales
        'has_filters': bool(filters),
        'is_filtered': any([filters.get('type'), filters.get('category'), 
                           filters.get('start_date'), filters.get('end_date')]),
    }
    
    # ============================================
    # 7. RENDERIZAR TEMPLATE
    # ============================================
    
    return render(request, 'finances/transactions.html', context)


@login_required
def categories(request):
    categories_list = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('categories')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories_list,
        'form': form,
    }
    
    return render(request, 'finances/categories.html', context)

@login_required
def investments(request):
    investments_list = Investment.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.user = request.user
            investment.save()
            messages.success(request, 'Inversión agregada exitosamente.')
            return redirect('investments')
    else:
        form = InvestmentForm()
    
    context = {
        'investments': investments_list,
        'form': form,
    }
    
    return render(request, 'finances/investments.html', context)

@login_required
def reports(request):
    # Get date range for reports
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    
    # Monthly income/expense data
    monthly_data = {}
    current = start_date.replace(day=1)
    
    while current <= end_date:
        month_start = current
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        income = Transaction.objects.filter(
            user=request.user,
            transaction_type='INCOME',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='EXPENSE',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        monthly_data[current.strftime('%Y-%m')] = {
            'income': float(income),
            'expense': float(expense),
            'balance': float(income - expense),
            'label': current.strftime('%b %Y')
        }
        
        current = (current + timedelta(days=32)).replace(day=1)
    
    # Category spending for the last 6 months
    six_months_ago = end_date - timedelta(days=180)
    category_spending = {}
    
    categories = Category.objects.filter(user=request.user, category_type='EXPENSE')
    for category in categories:
        total = Transaction.objects.filter(
            user=request.user,
            category=category,
            transaction_type='EXPENSE',
            date__gte=six_months_ago
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        if total > 0:
            category_spending[category.name] = {
                'total': float(total),
                'color': category.color
            }
    
    context = {
        'monthly_data': json.dumps(monthly_data),
        'category_spending': json.dumps(category_spending),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'finances/reports.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'finances/register.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Here you would typically send an email
            messages.success(request, '¡Mensaje enviado! Te contactaremos pronto.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'finances/contact.html', {'form': form})

@login_required
def delete_transaction(request, transaction_id):
    """
    Vista para eliminar una transacción
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        try:
            transaction_description = transaction.description or "Transacción sin descripción"
            transaction_amount = transaction.amount
            transaction.delete()
            
            messages.success(request, 
                f'✅ Transacción "{transaction_description}" por ${transaction_amount} eliminada exitosamente.'
            )
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar la transacción: {str(e)}')
    
    return redirect('transactions')

@login_required
def get_financial_data(request):
    """API endpoint for chart data"""
    data = {}
    
    # Last 6 months data
    end_date = timezone.now()
    start_date = end_date - timedelta(days=180)
    
    months = []
    income_data = []
    expense_data = []
    
    current = start_date.replace(day=1)
    while current <= end_date:
        month_start = current
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        income = Transaction.objects.filter(
            user=request.user,
            transaction_type='INCOME',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='EXPENSE',
            date__range=[month_start, month_end]
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        months.append(current.strftime('%b'))
        income_data.append(float(income))
        expense_data.append(float(expense))
        
        current = (current + timedelta(days=32)).replace(day=1)
    
    data['months'] = months
    data['income'] = income_data
    data['expense'] = expense_data
    
    return JsonResponse(data)

# Para eliminar categorías
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('categories')

# Para eliminar inversiones
@login_required
def delete_investment(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, user=request.user)
    if request.method == 'POST':
        investment.delete()
        messages.success(request, 'Inversión eliminada exitosamente.')
    return redirect('investments')

# Para editar transacciones
@login_required
def edit_transaction(request, transaction_id):
    """
    Vista para editar una transacción existente
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '✅ Transacción actualizada exitosamente.')
                return redirect('transactions')
            except Exception as e:
                messages.error(request, f'❌ Error al actualizar la transacción: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    context = {
        'form': form,
        'transaction': transaction,
        'categories': Category.objects.filter(user=request.user),
    }
    
    return render(request, 'finances/edit_transaction.html', context)

# API para datos de categorías
@login_required
def get_category_spending(request):

    # Implementa según necesites
    return JsonResponse({})    


@login_required
def get_transaction_stats(request):
    """
    API para obtener estadísticas de transacciones (para AJAX)
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Obtener período del request
            period = request.GET.get('period', 'month')  # month, week, year
            
            # Calcular fechas según período
            today = timezone.now().date()
            
            if period == 'week':
                start_date = today - timedelta(days=7)
            elif period == 'month':
                start_date = today - timedelta(days=30)
            elif period == 'year':
                start_date = today - timedelta(days=365)
            else:
                start_date = today - timedelta(days=30)
            
            # Obtener transacciones del período
            transactions = Transaction.objects.filter(
                user=request.user,
                date__gte=start_date,
                date__lte=today
            )
            
            # Calcular estadísticas
            stats = {
                'total_income': float(transactions.filter(
                    transaction_type='INCOME'
                ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')),
                
                'total_expenses': float(transactions.filter(
                    transaction_type='EXPENSE'
                ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')),
                
                'total_investments': float(transactions.filter(
                    transaction_type='INVESTMENT'
                ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')),
                
                'transaction_count': transactions.count(),
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': today.strftime('%Y-%m-%d'),
            }
            
            return JsonResponse({'success': True, 'stats': stats})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})    

@login_required
def export_transactions(request):
    """
    Vista para exportar transacciones a CSV
    """
    from django.http import HttpResponse
    import csv
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transacciones.csv"'
    
    writer = csv.writer(response)
    
    # Escribir encabezados
    writer.writerow(['Fecha', 'Descripción', 'Categoría', 'Tipo', 'Monto', 'Usuario'])
    
    # Obtener transacciones
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    # Escribir datos
    for transaction in transactions:
        writer.writerow([
            transaction.date.strftime('%d/%m/%Y'),
            transaction.description or '',
            transaction.category.name,
            transaction.get_transaction_type_display(),
            str(transaction.amount),
            transaction.user.username
        ])
    
    return response   