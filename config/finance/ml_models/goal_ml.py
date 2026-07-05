# finance/ml_models/goal_ml.py
# All 5 ML features for Goal Achievement

from datetime import date, timedelta
import calendar

# ============================================================
# FEATURE 1 — GOAL SUCCESS PROBABILITY
# Returns 0-100% chance of achieving the goal
# ============================================================

def goal_success_probability(current_savings, target_amount, months_remaining, monthly_savings_rate):
    """
    Predicts % probability of achieving the goal.

    Args:
        current_savings (float):      Total savings so far (income - expense)
        target_amount (float):        Goal target amount
        months_remaining (int):       Months left to reach the goal
        monthly_savings_rate (float): Avg amount saved per month recently

    Returns:
        dict: { 'probability': int, 'label': str, 'color': str }
    """

    if target_amount <= 0:
        return {'probability': 0, 'label': 'Invalid Goal', 'color': 'gray'}

    # How much more is needed
    remaining = max(0, target_amount - current_savings)

    if remaining == 0:
        return {'probability': 100, 'label': 'Achieved!', 'color': 'green'}

    if monthly_savings_rate <= 0 or months_remaining <= 0:
        return {'probability': 0, 'label': 'At Risk', 'color': 'red'}

    # Projected savings if current rate continues
    projected = current_savings + (monthly_savings_rate * months_remaining)

    # Raw probability based on projection vs target
    raw_prob = (projected / target_amount) * 100

    # Clamp between 0 and 100
    probability = min(100, max(0, round(raw_prob)))

    # Label and color
    if probability >= 80:
        label = 'On Track'
        color = 'green'
    elif probability >= 50:
        label = 'Needs Attention'
        color = 'orange'
    else:
        label = 'At Risk'
        color = 'red'

    return {
        'probability': probability,
        'label': label,
        'color': color
    }


# ============================================================
# FEATURE 2 — SMART MONTHLY SAVING RECOMMENDATION
# Suggests a realistic monthly saving target
# ============================================================

def smart_saving_recommendation(target_amount, target_months, avg_monthly_savings):
    """
    Compares required monthly saving vs realistic saving ability.

    Args:
        target_amount (float):        Goal target
        target_months (int):          Duration set by user
        avg_monthly_savings (float):  User's average monthly savings from history

    Returns:
        dict: { 'required': float, 'realistic': float, 'feasible': bool,
                'suggested_months': int, 'message': str }
    """

    required = round(target_amount / target_months, 2) if target_months > 0 else 0
    realistic = round(avg_monthly_savings, 2)
    feasible = realistic >= required

    # Suggest how many months it would actually take
    if realistic > 0:
        suggested_months = round(target_amount / realistic)
    else:
        suggested_months = None

    if feasible:
        message = f"You can comfortably save ₹{required}/month. Goal is achievable!"
    elif suggested_months:
        message = (
            f"You can realistically save ₹{realistic}/month. "
            f"Consider extending your goal to {suggested_months} months."
        )
    else:
        message = "Your current savings rate is too low. Try reducing expenses first."

    return {
        'required': required,
        'realistic': realistic,
        'feasible': feasible,
        'suggested_months': suggested_months,
        'message': message
    }


# ============================================================
# FEATURE 3 — COMPLETION DATE PREDICTION
# Predicts the actual finish date based on saving velocity
# ============================================================

def predict_completion_date(current_savings, target_amount, monthly_savings_rate, start_date):
    """
    Predicts when the goal will actually be completed.

    Args:
        current_savings (float):      Savings so far
        target_amount (float):        Goal target
        monthly_savings_rate (float): Avg monthly savings
        start_date (date):            Goal start date

    Returns:
        dict: { 'predicted_date': str, 'months_needed': int, 'on_time': bool, 'message': str }
    """

    remaining = max(0, target_amount - current_savings)

    if remaining == 0:
        return {
            'predicted_date': 'Already Achieved!',
            'months_needed': 0,
            'on_time': True,
            'message': 'Congratulations! Goal already reached.'
        }

    if monthly_savings_rate <= 0:
        return {
            'predicted_date': 'Unknown',
            'months_needed': None,
            'on_time': False,
            'message': 'Cannot predict — no positive savings trend found.'
        }

    # Months needed from today
    months_needed = round(remaining / monthly_savings_rate)

    # Calculate predicted end date
    today = date.today()
    predicted_month = today.month + months_needed
    predicted_year  = today.year + (predicted_month - 1) // 12
    predicted_month = ((predicted_month - 1) % 12) + 1

    # Last valid day of that month
    last_day = calendar.monthrange(predicted_year, predicted_month)[1]
    predicted_date = date(predicted_year, predicted_month, last_day)

    message = f"At your current saving rate, you'll reach this goal by {predicted_date.strftime('%B %Y')}."

    return {
        'predicted_date': predicted_date.strftime('%B %Y'),
        'months_needed': months_needed,
        'on_time': True,   # view_goals will compare against target
        'message': message
    }


# ============================================================
# FEATURE 4 — GOAL RISK ALERT
# Early warning if user is heading off track
# ============================================================

def goal_risk_alert(current_savings, target_amount, target_months, months_passed, monthly_savings_rate):
    """
    Detects risk BEFORE the goal becomes 'Delayed'.

    Args:
        current_savings (float):      Savings so far
        target_amount (float):        Goal target
        target_months (int):          Total months for goal
        months_passed (int):          Months elapsed since start
        monthly_savings_rate (float): Avg monthly savings

    Returns:
        dict: { 'risk_level': str, 'shortfall': float, 'message': str } or None
    """

    months_remaining = max(0, target_months - months_passed)

    if months_remaining == 0:
        return None   # Goal period over, no point alerting

    # What should have been saved by now (expected pace)
    expected_by_now = (target_amount / target_months) * months_passed

    # Shortfall vs expected
    shortfall = max(0, expected_by_now - current_savings)

    # Projected total at current rate
    projected_total = current_savings + (monthly_savings_rate * months_remaining)
    projected_shortfall = max(0, target_amount - projected_total)

    # Determine risk level
    if projected_shortfall == 0:
        return None   # No risk, don't show alert

    pct_short = (projected_shortfall / target_amount) * 100

    if pct_short >= 40:
        risk_level = 'High'
        message = (
            f"🔴 High Risk: You may fall ₹{round(projected_shortfall, 2)} short of your goal. "
            f"Consider increasing monthly savings immediately."
        )
    elif pct_short >= 15:
        risk_level = 'Medium'
        message = (
            f"🟠 Caution: At current pace, you'll be ₹{round(projected_shortfall, 2)} short. "
            f"Try to save a little more each month."
        )
    else:
        risk_level = 'Low'
        message = (
            f"🟡 Minor Risk: Small shortfall of ₹{round(projected_shortfall, 2)} projected. "
            f"You're close — keep it up!"
        )

    return {
        'risk_level': risk_level,
        'shortfall': round(projected_shortfall, 2),
        'message': message
    }


# ============================================================
# FEATURE 5 — OPTIMAL GOAL SUGGESTER
# Suggests a realistic goal amount and duration on set_goal page
# ============================================================

def suggest_optimal_goal(avg_monthly_income, avg_monthly_expense):
    """
    Suggests a realistic savings goal based on income/expense history.

    Args:
        avg_monthly_income (float):  Average monthly income
        avg_monthly_expense (float): Average monthly expense

    Returns:
        dict: { 'monthly_savings': float, 'suggested_3m': float,
                'suggested_6m': float, 'suggested_12m': float, 'message': str }
              or None if not enough data
    """

    if avg_monthly_income <= 0:
        return None

    monthly_savings = max(0, avg_monthly_income - avg_monthly_expense)

    if monthly_savings <= 0:
        return {
            'monthly_savings': 0,
            'suggested_3m': 0,
            'suggested_6m': 0,
            'suggested_12m': 0,
            'message': "Your expenses exceed income. Focus on reducing expenses before setting a goal."
        }

    suggested_3m  = round(monthly_savings * 3,  2)
    suggested_6m  = round(monthly_savings * 6,  2)
    suggested_12m = round(monthly_savings * 12, 2)

    message = (
        f"Based on your history, you save about ₹{round(monthly_savings, 2)}/month. "
        f"You can aim for ₹{suggested_6m} in 6 months or ₹{suggested_12m} in 12 months."
    )

    return {
        'monthly_savings': round(monthly_savings, 2),
        'suggested_3m':    suggested_3m,
        'suggested_6m':    suggested_6m,
        'suggested_12m':   suggested_12m,
        'message':         message
    }