from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Engineer(models.Model):
    admin = models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username
    
class Ground(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price_per_hour = models.IntegerField(null=True)
 
    def __str__(self):
        return self.name
 
class Booking(models.Model):
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_booking_date = models.DateTimeField()
    end_booking_date = models.DateTimeField()
    is_booked = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
 
    def __str__(self):
        return f"Booking for {self.ground.name} on {self.start_booking_date} + {self.end_booking_date}"
 
    class Meta:
        unique_together = ('ground', 'start_booking_date','end_booking_date')
        
class Income_category(models.Model):
    name =models.CharField(max_length=100)
    description =models.CharField(max_length=100)
    created_at=models.DateTimeField()
    
    def __str__(self) -> str:
        return self.name + " " + self.description

class Income(models.Model):
    income_category_name =models.ForeignKey(Income_category,on_delete=models.CASCADE,blank=True,null=True)
    amount = models.CharField(max_length=100)

class Expence_category(models.Model):
    name =models.CharField(max_length=100)
    created_at=models.DateTimeField()
    
    def __str__(self) -> str:
        return self.name
    
class Expence(models.Model):
    expence_category_name =models.ForeignKey(Expence_category,on_delete=models.CASCADE,blank=True,null=True)
    ex_amount = models.CharField(max_length=100)

class Expense(models.Model):
    expence_category_name =models.ForeignKey(Expence_category,on_delete=models.CASCADE,blank=True,null=True)
    description =models.CharField(max_length=100, null=True,blank=True)
    ex_amount = models.IntegerField()
    created_at=models.DateTimeField(now)
    
    def __str__(self) -> str:
        return f"{self.expence_category_name}"

class Company_information(models.Model):
    company_name=models.CharField(max_length=200)
    address=models.CharField(max_length=200)
    gst_number=models.CharField(max_length=100)
    date=models.DateTimeField()
    
    def __str__(self) -> str:
        return self.company_name
        
class Stock(models.Model):
    company_information=models.ForeignKey(Company_information,on_delete=models.CASCADE,blank=True,null=True)
    product_name = models.CharField(max_length=100)
    qty = models.IntegerField()
    rate = models.IntegerField()
    discount = models.IntegerField()
    cgst=models.IntegerField()
    sgst=models.IntegerField()
    total_amount=models.IntegerField()
    final_total=models.IntegerField(blank=True,null=True)
    
    def __str__(self) -> str:
        return self.product_name
    

class Student(models.Model):
    student_name = models.CharField(max_length=50)
    fees_paid = models.IntegerField()
    date = models.DateTimeField(default=now)

    def __str__(self):
        return self.student_name
    
class Expense_amount(models.Model):
    expense_amount = models.IntegerField()
