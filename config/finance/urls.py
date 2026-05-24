from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('income', IncomeViewSet)
router.register('expense', ExpenseViewSet)
router.register('goals', GoalViewSet)
router.register('category', CategoryViewSet)

urlpatterns = router.urls