
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict, OrderedDict
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date
from datetime import date, timedelta
import io
import xlsxwriter
from xhtml2pdf import pisa
from .models import Expense, Category, Budget
from .forms import ExpenseForm, DateFilterForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import CategoryForm
from django.shortcuts import render, redirect
from .forms import BudgetForm
from django.contrib.auth.decorators import login_required
from .models import Budget
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Expense
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
# views.py

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login

# views.py
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def delete_expense(request, expense_id):
    """Allow the user to delete an expense."""
    # Fetch the expense to be deleted or return a 404 error if not found
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    # Delete the expense
    expense.delete()
    
    # Send a success message
    messages.success(request, "Expense deleted successfully!")
    
    # Redirect back to the dashboard
    return redirect('dashboard')


def add_budget(request):
    """Allow the user to add a budget to a category."""
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            # Save the budget if valid
            budget = form.save(commit=False)
            budget.user = request.user  # Associate the budget with the logged-in user
            budget.save()
            return redirect('dashboard')  # Redirect to dashboard after saving the budget
    else:
        form = BudgetForm()

    return render(request, 'tracker/add_budget.html', {'form': form})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user  # Optional, only if Category is user-specific
            category.save()
            messages.success(request, "Category added successfully!")
            return redirect('dashboard')
    else:
        form = CategoryForm()

    return render(request, 'tracker/add_category.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')  # Redirect after success



def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Get the 'next' URL
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            return redirect('dashboard')  # Fallback if no next
    else:
        form = AuthenticationForm()

    # Pass 'next' to the template so it gets included in the form
    return render(request, 'registration/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })



@login_required
def export_excel(request):
    raw_start = request.GET.get('start_date')
    raw_end = request.GET.get('end_date')

    start_date = parse_date(raw_start) if raw_start else date.today().replace(day=1)
    end_date = parse_date(raw_end) if raw_end else date.today()

    if not start_date or not end_date:
        return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)

    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

  # Update the headers
    headers = ['Date', 'Category', 'Amount']
    for col, header in enumerate(headers):
     worksheet.write(0, col, header)

# Write data rows
    for row, expense in enumerate(expenses, start=1):
     worksheet.write(row, 0, str(expense.date))
    worksheet.write(row, 1, expense.category.name)
    worksheet.write(row, 2, float(expense.amount))


    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=expenses.xlsx'
    return response


@login_required
def export_pdf(request):
    raw_start = request.GET.get('start_date')
    raw_end = request.GET.get('end_date')

    start_date = parse_date(raw_start) if raw_start else date.today().replace(day=1)
    end_date = parse_date(raw_end) if raw_end else date.today()

    if not start_date or not end_date:
        return HttpResponse("Invalid date format. Use YYYY-MM-DD.", status=400)

    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).order_by('-date')

    context = {
        'expenses': expenses,
        'start_date': start_date,
        'end_date': end_date,
        'user': request.user
    }

    html = render_to_string('tracker/pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


@login_required
def dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)

    start_date = request.GET.get('start_date') or month_start
    end_date = request.GET.get('end_date') or today
    date_filter_form = DateFilterForm(request.GET if request.GET.get('start_date') else None)

    expenses = Expense.objects.filter(user=request.user, date__range=[start_date, end_date]).order_by('-date')
    budgets = Budget.objects.filter(user=request.user)

    alerts = []
    category_spending = {}

    for budget in budgets:
        spent = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0

        category_spending[budget.category.name] = spent

        if spent > budget.monthly_limit:
            alerts.append(f"You exceeded your {budget.category.name} budget!")

    form = ExpenseForm()
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')

    chart_labels = list(category_spending.keys())
    chart_data = list(category_spending.values())

    six_months_ago = today - timedelta(days=180)
    monthly_data = (
        Expense.objects.filter(user=request.user, date__gte=six_months_ago)
        .annotate(month=TruncMonth('date'))
        .values('month', 'category__name')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    category_totals = defaultdict(lambda: OrderedDict())
    months_order = []

    for entry in monthly_data:
        month_label = entry['month'].strftime('%b %Y')
        if month_label not in months_order:
            months_order.append(month_label)
        category_totals[entry['category__name']][month_label] = entry['total']

    bar_labels = months_order
    bar_datasets = []
    colors = ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']

    for idx, (category, data) in enumerate(category_totals.items()):
        values = [data.get(month, 0) for month in bar_labels]
        bar_datasets.append({
            'label': category,
            'backgroundColor': colors[idx % len(colors)],
            'data': values
        })

    return render(request, 'tracker/dashboard.html', {
        'form': form,
        'expenses': expenses,
        'alerts': alerts,
        'category_spending': category_spending,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'bar_labels': bar_labels,
        'bar_datasets': bar_datasets,
        'date_filter_form': date_filter_form
    })
