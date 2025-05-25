from django import forms
from .models import Expense
from django import forms
from .models import Category
from django import forms
from .models import Budget, Category

from django import forms
from .models import Budget, Category
# forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class BudgetForm(forms.ModelForm):
    """Form to add a budget for a category."""
    class Meta:
        model = Budget
        fields = ['category', 'monthly_limit']
    
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Select Category")
    monthly_limit = forms.FloatField(label="Monthly Budget Limit", min_value=0)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }
class DateFilterForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
