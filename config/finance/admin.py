from django.contrib import admin

# Register your models here.
from .models import Income, Expense, Goal, Category

admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Goal)
admin.site.register(Category)