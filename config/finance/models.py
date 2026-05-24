from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    source = models.CharField(max_length=100)
    date = models.DateField()
    
    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    
    def __str__(self):
        return self.name
        
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    date = models.DateField()
    
    def __str__(self):
        return self.user.username

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.FloatField()
    saved_amount = models.FloatField(default=0)
    
    def __str__(self):
        return self.user.username