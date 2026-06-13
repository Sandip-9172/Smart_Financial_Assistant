import os
import sys
import django
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error

# ==========================================
# PROJECT ROOT
# ==========================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

sys.path.append(BASE_DIR)

# ==========================================
# DJANGO SETTINGS
# ==========================================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

# ==========================================
# IMPORT MODELS
# ==========================================

from finance.models import Expense

# ==========================================
# FETCH DATA
# ==========================================

expenses = Expense.objects.select_related('category').all()

data = []

for expense in expenses:
    data.append({
        "year": expense.date.year,       # <-- added year
        "month": expense.date.month,
        "category": expense.category.name,
        "amount": expense.amount
    })

# ==========================================
# DATAFRAME
# ==========================================

df = pd.DataFrame(data)

if df.empty:
    print("No expense data found. Please add some expenses first.")
    sys.exit()

print("Raw Data Sample:")
print(df.head())

# ==========================================
# AGGREGATE: GROUP BY YEAR + MONTH + CATEGORY
# This gives total spent per category per month
# ==========================================

df_monthly = df.groupby(
    ['year', 'month', 'category'],
    as_index=False
).agg(
    total_amount=('amount', 'sum')
)

print("\nMonthly Aggregated Data:")
print(df_monthly.head(10))
print(f"\nTotal training rows: {len(df_monthly)}")

# ==========================================
# ENCODE CATEGORY
# ==========================================

encoder = LabelEncoder()

df_monthly['category_encoded'] = encoder.fit_transform(
    df_monthly['category']
)

print(f"\nCategories found: {list(encoder.classes_)}")

# ==========================================
# FEATURES & TARGET
# year + month + category → total_amount
# ==========================================

X = df_monthly[['year', 'month', 'category_encoded']]

y = df_monthly['total_amount']

# ==========================================
# NEED MINIMUM DATA CHECK
# ==========================================

if len(df_monthly) < 5:
    print("\nWarning: Very little data. Model accuracy may be low.")
    print("Add more expense history for better predictions.")

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ==========================================
# TRAIN MODEL
# ==========================================

model = LinearRegression()

model.fit(X_train, y_train)

# ==========================================
# PREDICTION TEST
# ==========================================

predictions = model.predict(X_test)

error = mean_absolute_error(y_test, predictions)

print(f"\nModel MAE (Mean Absolute Error): ₹{round(error, 2)}")
print("(Lower is better — this is avg prediction error in ₹)")

# ==========================================
# SAVE MODEL & ENCODER
# ==========================================

os.makedirs('finance/saved_models', exist_ok=True)

joblib.dump(
    model,
    'finance/saved_models/expense_model.pkl'
)

joblib.dump(
    encoder,
    'finance/saved_models/category_encoder.pkl'
)

print("\nModel Trained & Saved Successfully!")
print("File: finance/saved_models/expense_model.pkl")