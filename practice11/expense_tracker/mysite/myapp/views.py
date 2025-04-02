from django.shortcuts import render, redirect
from .filters import ExpenseFilter
from .forms import ExpenseForm
from .models import Category, Expense, GroupExpense
from django.db.models import Sum
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from .filters import ExpenseFilter
from .forms import ExpenseForm
from .models import Category, Expense, GroupExpense
from django.db.models import Sum
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  

@login_required
def index(request):
    if request.method == "POST":
        if 'add_expense' in request.POST:  
            expense = ExpenseForm(request.POST, user=request.user)
            if expense.is_valid():
                expense = expense.save(commit=False)
                expense.user = request.user
                expense.save()
                print(f"Added expense: {expense.name}, {expense.amount}, {expense.category}, {expense.date}")
                return redirect('index')
            else:
                print(f"Form errors: {expense.errors}")
        elif 'add_category' in request.POST:  
            name = request.POST.get('category_name')
            if name:
                Category.objects.create(name=name, user=request.user)
                print(f"Added category: {name}")
                return redirect('index')
    
    expenses = Expense.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    expense_filter = ExpenseFilter(request.GET, queryset=expenses, user=request.user)
    filtered_expenses = expense_filter.qs
    
    total_expenses = filtered_expenses.aggregate(Sum('amount'))
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    yearly_sum = filtered_expenses.filter(date__gt=last_year).aggregate(Sum('amount'))
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    monthly_sum = filtered_expenses.filter(date__gt=last_month).aggregate(Sum('amount'))
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    weekly_sum = filtered_expenses.filter(date__gt=last_week).aggregate(Sum('amount'))    
    daily_sums = filtered_expenses.values('date').order_by('date').annotate(sum=Sum('amount'))
    categorical_sums = filtered_expenses.values('category').order_by('category').annotate(sum=Sum('amount'))
    
    expense_form = ExpenseForm(user=request.user)
    
    return render(request, 'myapp/index.html', {
        'expense_form': expense_form,
        'expenses': filtered_expenses,
        'total_expenses': total_expenses,
        'yearly_sum': yearly_sum,
        'monthly_sum': monthly_sum,
        'weekly_sum': weekly_sum,
        'daily_sums': daily_sums,
        'categorical_sums': categorical_sums,
        'categories': categories,
        'filter': expense_filter
    })

@login_required
def edit(request, id): 
    expense = Expense.objects.get(id=id, user=request.user) 
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'myapp/edit.html', {'expense_form': form})

@login_required
def delete(request, id):
    expense = Expense.objects.get(id=id, user=request.user)
    if request.method == "POST" and 'delete' in request.POST:
        expense.delete()
    return redirect('index') 

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        Category.objects.create(name=name, user=request.user)
    return redirect('index')

@login_required
def add_group_expense(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        users = request.POST.getlist('users')  
        if name and amount and users:
            group_expense = GroupExpense.objects.create(
                name=name,
                amount=amount,
                date=datetime.date.today()
            )
            group_expense.users.set(users)
            if str(request.user.id) not in users:
                group_expense.users.add(request.user)
            print(f"Added group expense: {group_expense.name}, {group_expense.amount}, Users: {group_expense.users.all()}")
            return redirect('group_expense_list')
    all_users = User.objects.all()
    return render(request, 'myapp/add_group_expense.html', {'users': all_users})

@login_required
def group_expense_list(request):
    expenses = GroupExpense.objects.filter(users=request.user)
    return render(request, 'myapp/group_expense_list.html', {'expenses': expenses})
