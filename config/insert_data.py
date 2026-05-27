from finance.models import Income, Expense, Category, Goal
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
# Get User
user = User.objects.get(username='sandip')

# -------------------------------
# CREATE CATEGORIES
# -------------------------------

categories = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Travel",
    "Rent",
    "Investment"
]

for cat in categories:
    Category.objects.get_or_create(name=cat)

print("Categories Inserted")


# -------------------------------
# INSERT INCOME DATA
# -------------------------------

income_data = [
    (45000, "Salary", "2025-01-01"),
    (45000, "Salary", "2025-02-01"),
    (47000, "Salary", "2025-03-01"),
    (47000, "Salary", "2025-04-01"),
    (50000, "Salary", "2025-05-01"),
    (50000, "Salary", "2025-06-01"),
    (52000, "Salary", "2025-07-01"),
    (52000, "Salary", "2025-08-01"),
    (55000, "Salary", "2025-09-01"),
    (55000, "Salary", "2025-10-01"),
    (58000, "Salary", "2025-11-01"),
    (60000, "Salary", "2025-12-01"),
]

for amount, source, dt in income_data:
    Income.objects.create(
        user=user,
        amount=amount,
        source=source,
        date=dt
    )

print("Income Data Inserted")


# -------------------------------
# INSERT EXPENSE DATA
# -------------------------------

expense_data = [

    # JANUARY
    (2500, "Food", "2025-01-02"),
    (1200, "Transport", "2025-01-05"),
    (18000, "Rent", "2025-01-06"),
    (3200, "Bills", "2025-01-10"),
    (1500, "Entertainment", "2025-01-15"),
    (2500, "Shopping", "2025-01-20"),
    (3000, "Investment", "2025-01-25"),

    # FEBRUARY
    (2700, "Food", "2025-02-03"),
    (1500, "Transport", "2025-02-06"),
    (18000, "Rent", "2025-02-07"),
    (3400, "Bills", "2025-02-11"),
    (1200, "Entertainment", "2025-02-17"),
    (3500, "Shopping", "2025-02-22"),
    (4000, "Investment", "2025-02-27"),

    # MARCH
    (3200, "Food", "2025-03-04"),
    (1700, "Transport", "2025-03-05"),
    (18000, "Rent", "2025-03-06"),
    (3600, "Bills", "2025-03-10"),
    (2200, "Entertainment", "2025-03-14"),
    (4200, "Shopping", "2025-03-18"),
    (5000, "Investment", "2025-03-25"),

    # APRIL
    (2800, "Food", "2025-04-03"),
    (1300, "Transport", "2025-04-07"),
    (18000, "Rent", "2025-04-08"),
    (3000, "Bills", "2025-04-11"),
    (1800, "Entertainment", "2025-04-16"),
    (2700, "Shopping", "2025-04-20"),
    (3500, "Investment", "2025-04-27"),

    # MAY
    (3500, "Food", "2025-05-02"),
    (1600, "Transport", "2025-05-06"),
    (19000, "Rent", "2025-05-07"),
    (3800, "Bills", "2025-05-10"),
    (2500, "Entertainment", "2025-05-15"),
    (5000, "Shopping", "2025-05-20"),
    (6000, "Investment", "2025-05-28"),

    # JUNE
    (3300, "Food", "2025-06-02"),
    (1400, "Transport", "2025-06-05"),
    (19000, "Rent", "2025-06-08"),
    (3900, "Bills", "2025-06-12"),
    (2000, "Entertainment", "2025-06-15"),
    (4500, "Shopping", "2025-06-18"),
    (5500, "Investment", "2025-06-26"),

    # JULY
    (3600, "Food", "2025-07-03"),
    (1700, "Transport", "2025-07-07"),
    (20000, "Rent", "2025-07-08"),
    (4200, "Bills", "2025-07-11"),
    (2600, "Entertainment", "2025-07-14"),
    (5200, "Shopping", "2025-07-19"),
    (7000, "Investment", "2025-07-29"),

    # AUGUST
    (3400, "Food", "2025-08-02"),
    (1600, "Transport", "2025-08-05"),
    (20000, "Rent", "2025-08-08"),
    (4100, "Bills", "2025-08-12"),
    (2400, "Entertainment", "2025-08-16"),
    (4800, "Shopping", "2025-08-22"),
    (6500, "Investment", "2025-08-28"),

    # SEPTEMBER
    (3900, "Food", "2025-09-03"),
    (1800, "Transport", "2025-09-07"),
    (21000, "Rent", "2025-09-09"),
    (4500, "Bills", "2025-09-13"),
    (3000, "Entertainment", "2025-09-15"),
    (5500, "Shopping", "2025-09-19"),
    (8000, "Investment", "2025-09-27"),

    # OCTOBER
    (4100, "Food", "2025-10-02"),
    (1900, "Transport", "2025-10-04"),
    (21000, "Rent", "2025-10-08"),
    (4700, "Bills", "2025-10-11"),
    (3500, "Entertainment", "2025-10-17"),
    (7000, "Shopping", "2025-10-21"),
    (9000, "Investment", "2025-10-28"),

    # NOVEMBER
    (3800, "Food", "2025-11-03"),
    (1700, "Transport", "2025-11-06"),
    (22000, "Rent", "2025-11-09"),
    (4900, "Bills", "2025-11-12"),
    (3200, "Entertainment", "2025-11-18"),
    (6200, "Shopping", "2025-11-22"),
    (9500, "Investment", "2025-11-29"),

    # DECEMBER
    (5000, "Food", "2025-12-02"),
    (2200, "Transport", "2025-12-05"),
    (22000, "Rent", "2025-12-08"),
    (5500, "Bills", "2025-12-11"),
    (5000, "Entertainment", "2025-12-18"),
    (10000, "Shopping", "2025-12-22"),
    (12000, "Investment", "2025-12-29"),
]

for amount, category_name, dt in expense_data:
    category = Category.objects.get(name=category_name)

    Expense.objects.create(
        user=user,
        amount=amount,
        category=category,
        date=dt
    )

print("Expense Data Inserted")


# -------------------------------
# INSERT GOALS
# -------------------------------

Goal.objects.create(
    user=user,
    name="Buy Mobile",
    target_amount=35000,
    target_months=8,
    start_date=timezone.now()
)

Goal.objects.create(
    user=user,
    name="Emergency Fund",
    target_amount=200000,
    target_months=12,
    start_date=date(2025, 3, 15)
)

Goal.objects.create(
    user=user,
    name="Goa Trip",
    target_amount=50000,
    target_months=7,
    start_date=date(2026, 5, 25)
)

print("Goals Inserted")

print("All Data Inserted Successfully")