import joblib
import pandas as pd
from datetime import datetime

# ==========================================
# LOAD MODEL & ENCODER
# ==========================================

model = joblib.load(
    'finance/saved_models/expense_model.pkl'
)

encoder = joblib.load(
    'finance/saved_models/category_encoder.pkl'
)

# ==========================================
# PREDICT MONTHLY EXPENSE
# ==========================================

def predict_expense(month, category_name, year=None):
    """
    Predicts total expense for a given month, year, and category.

    Args:
        month (int):         Month number (1-12)
        category_name (str): Category name e.g. "Food", "Transport"
        year (int):          Year e.g. 2025. Defaults to current year.

    Returns:
        float: Predicted total expense for that month/category
               Returns 0.0 if category is unknown (not in training data)
    """

    # Default year to current if not provided
    if year is None:
        year = datetime.now().year

    # ---- HANDLE UNKNOWN CATEGORY ----
    # If the category wasn't in training data, return 0
    if category_name not in encoder.classes_:
        print(f"Warning: '{category_name}' not found in training data.")
        return 0.0

    # ---- ENCODE CATEGORY ----
    category_encoded = encoder.transform([category_name])[0]

    # ---- BUILD INPUT ----
    # Must match training features: year, month, category_encoded
    input_data = pd.DataFrame({
        'year':             [year],
        'month':            [month],
        'category_encoded': [category_encoded]
    })

    # ---- PREDICT ----
    prediction = model.predict(input_data)

    # Clamp to 0 (no negative expenses)
    result = max(0.0, round(prediction[0], 2))

    return result


# ==========================================
# PREDICT NEXT MONTH HELPER
# ==========================================

def predict_next_month(category_name):
    """
    Convenience function — automatically predicts for next month.

    Args:
        category_name (str): e.g. "Food"

    Returns:
        float: Predicted expense for next month
    """
    now = datetime.now()

    # Calculate next month and year
    if now.month == 12:
        next_month = 1
        next_year  = now.year + 1
    else:
        next_month = now.month + 1
        next_year  = now.year

    return predict_expense(next_month, category_name, next_year)