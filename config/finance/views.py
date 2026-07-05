from rest_framework import viewsets
from .models import Income, Expense, Goal, Category
from django.db.models import Sum
from .serializers import *
from datetime import date,datetime

# ML models 
from finance.ml_models.predict import predict_expense

class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Create your views here.
from finance.ml_models.goal_ml import (
    goal_success_probability,
    smart_saving_recommendation,
    predict_completion_date,
    goal_risk_alert,
    suggest_optimal_goal,
)

# frontend views 
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request,
                          'register.html',
                          {'error': 'Username already exists'})

        # Create user
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect('/login/')
    return render(request, 'register.html')

# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')

        else:
            
            return render(
                request,
                'login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'login.html')

# ---------------- DASHBOARD ----------------
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):

    # ---------- TOTAL INCOME ----------
    total_income = Income.objects.filter(
        user=request.user
    ).aggregate(
        Sum('amount')
    )['amount__sum']

    # ---------- TOTAL EXPENSE ----------
    total_expense = Expense.objects.filter(
        user=request.user
    ).aggregate(
        Sum('amount')
    )['amount__sum']

    # ---------- HANDLE NONE VALUES ----------
    if total_income is None:
        total_income = 0

    if total_expense is None:
        total_expense = 0

    # ---------- SAVINGS ----------
    savings = total_income - total_expense

    # ---------- ACTIVE GOALS ----------
    active_goals = Goal.objects.filter(
        user=request.user
    ).count()


    # EXPENSE ANALYSIS
    expense_analysis = Expense.objects.filter(
        user=request.user
    ).values(
        'category__name'
    ).annotate(
        total=Sum('amount')

    )

    # CHART DATA
    labels = []
    data = []

    for item in expense_analysis:
        labels.append(
            item['category__name']
        )

        data.append(
            float(item['total'])
        )

    # ---------- ALL CATEGORIES FOR DROPDOWN ----------
    categories = Category.objects.all()
 
    # ---------- SELECTED CATEGORY PREDICTION ----------
    selected_category = None
    predicted_amount  = None
 
    if request.method == 'POST':
        selected_category = request.POST.get('category')
 
        if selected_category:
            from finance.ml_models.predict import predict_next_month
            predicted_amount = predict_next_month(selected_category)
 
    # ---------- CONTEXT ----------
    context = {
        'total_income':       total_income,
        'total_expense':      total_expense,
        'savings':            savings,
        'active_goals':       active_goals,
        'labels':             labels,
        'data':               data,
        'categories':         categories,
        'selected_category':  selected_category,
        'predicted_amount':   predicted_amount,
    }
    return render(request, 'dashboard.html', context)


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect('/')

###########################################################
# ---------------- Home Page ----------------
def home_view(request):
    return render(request,'home_page.html')

##########################################################
# ---------------- Add_income Page ----------------
@login_required
def add_income(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        source = request.POST['source']
        date = request.POST['date']

        Income.objects.create(
            user=request.user,
            amount=amount,
            source=source,
            date=date
        )

        return render(request,'add_income.html',{'success': True})
    return render(request,'add_income.html')

##########################################################
# ---------------- View _income Page ----------------
@login_required
def view_income(request):
    incomes = Income.objects.filter(
        user=request.user
    ).order_by('-date')

    total_income = incomes.aggregate(
        Sum('amount')
    )['amount__sum']

    if total_income is None:
        total_income = 0

    return render(request,'view_income.html',{
            'incomes': incomes,
            'total_income': total_income})

##########################################################
# ---------------- Add_expense Page ----------------
@login_required
def add_expense(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        amount = request.POST['amount']
        category_id = request.POST['category']
        date = request.POST['date']
        category = Category.objects.get(
            id=category_id
        )

        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            date=date
        )
        
        return render(request,'add_expense.html',{'success': True,'categories': categories})
    return render(request,'add_expense.html',{'categories': categories})
    
##########################################################
# ----------------View_expense Page ----------------
@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(
        user=request.user
    ).order_by('-date')

    total_expense = expenses.aggregate(
        Sum('amount')
    )['amount__sum']

    if total_expense is None:
        total_expense = 0

    return render(request,'view_expense.html',{'expenses': expenses,'total_expense': total_expense})
    
##########################################################    
#----------------VIEW GOAL Page--------------
 # Replace your view_goals() in views.py with this:

@login_required
def view_goals(request):
    from datetime import date
    from django.db.models.functions import TruncMonth

    goals      = Goal.objects.filter(user=request.user)
    today      = date.today()
    this_month = today.month
    this_year  = today.year

    # -------------------------------------------------------
    # AVG MONTHLY INCOME & EXPENSE — for Feature 5 suggester
    # -------------------------------------------------------
    monthly_income_qs = (
        Income.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
    )
    monthly_expense_qs = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
    )

    avg_monthly_income = (
        sum(x['total'] for x in monthly_income_qs) / monthly_income_qs.count()
        if monthly_income_qs.count() > 0 else 0
    )
    avg_monthly_expense = (
        sum(x['total'] for x in monthly_expense_qs) / monthly_expense_qs.count()
        if monthly_expense_qs.count() > 0 else 0
    )

    # -------------------------------------------------------
    # BUILD GOAL DATA
    # -------------------------------------------------------
    goal_data = []

    for goal in goals:

        months_passed = (
            (today.year  - goal.start_date.year) * 12 +
            (today.month - goal.start_date.month)
        )
        months_remaining = max(0, goal.target_months - months_passed)

        # ---------------------------------------------------
        # CUMULATIVE SAVINGS SINCE GOAL START DATE
        # Total income - total expense from goal start → today
        # ---------------------------------------------------
        income_since_start = Income.objects.filter(
            user=request.user,
            date__gte=goal.start_date       # >= goal start date
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        expense_since_start = Expense.objects.filter(
            user=request.user,
            date__gte=goal.start_date       # >= goal start date
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # How much actually saved since goal started
        saved_so_far = max(0, income_since_start - expense_since_start)

        # ---------------------------------------------------
        # CURRENT MONTH SAVINGS (for "this month" display)
        # ---------------------------------------------------
        current_month_income = Income.objects.filter(
            user=request.user,
            date__month=this_month,
            date__year=this_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        current_month_expense = Expense.objects.filter(
            user=request.user,
            date__month=this_month,
            date__year=this_year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        current_month_savings = current_month_income - current_month_expense

        # ---------------------------------------------------
        # AVG MONTHLY SAVINGS RATE (last 3 months) — for predictions
        # ---------------------------------------------------
        monthly_rates = []
        for i in range(1, 4):
            m = this_month - i
            y = this_year
            if m <= 0:
                m += 12
                y -= 1

            inc = Income.objects.filter(
                user=request.user, date__month=m, date__year=y
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            exp = Expense.objects.filter(
                user=request.user, date__month=m, date__year=y
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            monthly_rates.append(inc - exp)

        avg_monthly_savings = sum(monthly_rates) / len(monthly_rates) if monthly_rates else 0

        # ---------------------------------------------------
        # CORE CALCULATIONS (cumulative-aware)
        # ---------------------------------------------------

        # Overall progress % based on cumulative savings
        progress = min(100, round((saved_so_far / goal.target_amount) * 100, 2)) if goal.target_amount > 0 else 0

        # Remaining amount after deducting what's already saved
        true_remaining = max(0, round(goal.target_amount - saved_so_far, 2))

        # Required per month going forward (reduced by what's already saved)
        if months_remaining > 0:
            adjusted_monthly_required = round(true_remaining / months_remaining, 2)
        elif true_remaining > 0:
            adjusted_monthly_required = true_remaining   # overdue, full amount needed
        else:
            adjusted_monthly_required = 0                # goal achieved

        # How much more needed THIS month vs what's already saved this month
        still_needed_this_month = max(0, round(adjusted_monthly_required - current_month_savings, 2))

        # Status
        if true_remaining <= 0:
            status = "Achieved! 🎉"
        elif current_month_savings >= adjusted_monthly_required:
            status = "On Track ✅"
        else:
            status = "Behind This Month ⚠️"

        # ---- FEATURE 1: Success Probability ----
        ml_probability = goal_success_probability(
            current_savings      = saved_so_far,
            target_amount        = goal.target_amount,
            months_remaining     = months_remaining,
            monthly_savings_rate = avg_monthly_savings
        )

        # ---- FEATURE 2: Smart Recommendation ----
        ml_recommendation = smart_saving_recommendation(
            target_amount       = true_remaining,        # only remaining amount
            target_months       = max(1, months_remaining),
            avg_monthly_savings = avg_monthly_savings
        )

        # ---- FEATURE 3: Completion Date ----
        ml_completion = predict_completion_date(
            current_savings      = saved_so_far,
            target_amount        = goal.target_amount,
            monthly_savings_rate = avg_monthly_savings,
            start_date           = goal.start_date
        )

        # ---- FEATURE 4: Risk Alert ----
        ml_risk = goal_risk_alert(
            current_savings      = saved_so_far,
            target_amount        = goal.target_amount,
            target_months        = goal.target_months,
            months_passed        = months_passed,
            monthly_savings_rate = avg_monthly_savings
        )

        # Attach all values to goal object
        goal.saved_so_far              = round(saved_so_far, 2)
        goal.progress                  = progress
        goal.true_remaining            = true_remaining
        goal.adjusted_monthly_required = adjusted_monthly_required
        goal.current_month_savings     = round(current_month_savings, 2)
        goal.still_needed_this_month   = still_needed_this_month
        goal.avg_monthly_savings       = round(avg_monthly_savings, 2)
        goal.months_passed             = months_passed
        goal.months_remaining          = months_remaining
        goal.status                    = status
        goal.ml_probability            = ml_probability
        goal.ml_recommendation         = ml_recommendation
        goal.ml_completion             = ml_completion
        goal.ml_risk                   = ml_risk

        goal_data.append(goal)

    # ---- FEATURE 5: Optimal Goal Suggestion ----
    ml_suggestion = suggest_optimal_goal(avg_monthly_income, avg_monthly_expense)

    return render(request, 'view_goals.html', {
        'goals':         goal_data,
        'ml_suggestion': ml_suggestion,
    })
 
# ---------------------------------------------------------------
# REPLACE your existing set_goal() with this:
# ---------------------------------------------------------------
 
@login_required
def set_goal(request):
    # Feature 5: show suggestion on the form page too
     
    from django.db.models.functions import TruncMonth
 
    monthly_income_qs = (
        Income.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
    )
    monthly_expense_qs = (
        Expense.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
    )
 
    avg_monthly_income  = (
        sum(x['total'] for x in monthly_income_qs) / monthly_income_qs.count()
        if monthly_income_qs.count() > 0 else 0
    )
    avg_monthly_expense = (
        sum(x['total'] for x in monthly_expense_qs) / monthly_expense_qs.count()
        if monthly_expense_qs.count() > 0 else 0
    )
 
    ml_suggestion = suggest_optimal_goal(avg_monthly_income, avg_monthly_expense)
 
    if request.method == 'POST':
        name          = request.POST['name']
        target_amount = request.POST['target_amount']
        target_months = request.POST['target_months']
        start_date    = request.POST['start_date']
 
        Goal.objects.create(
            user=request.user,
            name=name,
            target_amount=target_amount,
            target_months=target_months,
            start_date=start_date
        )
        return render(request, 'set_goal.html', {
            'success': True,
            'ml_suggestion': ml_suggestion
        })
 
    return render(request, 'set_goal.html', {'ml_suggestion': ml_suggestion})
     

##########################################################
    # ------------- View Report ---------------
@login_required
def view_report(request):
    report = None
    category_labels = []
    category_data = []
    comparison_labels = []
    comparison_data = []
    insights = []

    if request.method == 'POST':
        month = int(request.POST['month'])
        year = int(request.POST['year'])

        # ---------- INCOME ----------
        incomes = Income.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        )

        # ---------- EXPENSE ----------
        expenses = Expense.objects.filter(
            user=request.user,
            date__month=month,
            date__year=year
        )

        # ---------- TOTAL INCOME ----------
        total_income = incomes.aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        # ---------- TOTAL EXPENSE ----------
        total_expense = expenses.aggregate(
            Sum('amount')
        )['amount__sum'] or 0

        # ---------- SAVINGS ----------
        savings = total_income - total_expense

        # CATEGORY ANALYTICS
        category_expense = expenses.values(
            'category__name'
        ).annotate(
            total=Sum('amount')
        )

        for item in category_expense:
            category_labels.append(
                item['category__name']
            )
            
            category_data.append(
                float(item['total'])
            )

        # MONTHLY COMPARISON
        for m in range(1, 13):
            monthly_total = Expense.objects.filter(
                user=request.user,
                date__month=m,
                date__year=year
            ).aggregate(
                Sum('amount')
            )['amount__sum'] or 0

            comparison_labels.append(m)
            comparison_data.append(float(monthly_total))

        # AI INSIGHTS
        if total_expense > total_income:
            insights.append(
                "Your expenses are higher than your income."
            )

        if savings > 0:
            insights.append(
                "Great! You saved money this month."
            )

        if category_expense:
            highest = max(
                category_expense,
                key=lambda x: x['total']
            )

            insights.append(
                f"Highest spending category: {highest['category__name']}"
            )

        # REPORT
        report = {
            'month': month,
            'year': year,
            'total_income': total_income,
            'total_expense': total_expense,
            'savings': savings,
            'expenses': expenses
        }

    return render(request,'view_report.html',
        {
            'report': report,
            'category_labels': category_labels,
            'category_data': category_data,
            'comparison_labels': comparison_labels,
            'comparison_data': comparison_data,
            'insights': insights
        }
    )
    
    # ------- Download report -------------
from django.http import HttpResponse
import csv

@login_required
def download_report(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    expenses = Expense.objects.filter(
        user=request.user,
        date__month=month,
        date__year=year
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="report_{month}_{year}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'Amount',
        'Category',
        'Date'
    ])

    for expense in expenses:
        writer.writerow([
            expense.amount,
            expense.category.name,
            expense.date
        ])

    return response