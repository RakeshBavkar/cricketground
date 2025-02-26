from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid

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


class BackupBooking(models.Model):
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_booking_date = models.DateTimeField()
    end_booking_date = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    backup_created_at = models.DateTimeField(auto_now_add=True)  # Time of backup
    # Add any other necessary fields that you want to back up

    def __str__(self):
        return f"Backup of Booking for {self.ground.name} from {self.start_booking_date} to {self.end_booking_date}"
    

class Bookings(models.Model):
    booking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    team1_name = models.CharField(max_length=100)
    team2_name = models.CharField(max_length=100, null=True, blank=True)
    mobile_number_team1 = models.CharField(max_length=15)
    mobile_number_team2 = models.CharField(max_length=15, null=True, blank=True)
    email_team1 = models.EmailField()
    email_team2 = models.EmailField(null=True, blank=True)
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    date = models.DateTimeField()
    time_slot = models.CharField(max_length=20)
    total_cost = models.IntegerField()
    cost_per_team = models.IntegerField(null=True, blank=True)
    payment_status_team1 = models.BooleanField(default=False)  # Team 1 Payment
    payment_status_team2 = models.BooleanField(default=False)  # Team 2 Payment
    status = models.CharField(max_length=20, default="Pending")  # Pending / Confirmed

    def __str__(self):
        return f"{self.team1_name} vs {self.team2_name if self.team2_name else 'Waiting'}"
    

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paid_payment = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.booking.ground.name} by {self.user.username} on {self.payment_time}"

    class Meta:
        unique_together = ('booking', 'user')  # Ensures only one payment per user for each booking


class TimeSlot(models.Model):
    SLOT_CHOICES = [
        ("7 - 9 AM", "7 - 9 AM"),
        ("9 - 11 AM", "9 - 11 AM"),
        ("11 - 2:30 PM", "11 - 2:30 PM"),
        ("2:30 - 6 PM", "2:30 - 6 PM"),
    ]
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES, unique=True)

    def __str__(self):
        return self.slot

class SuperBooking(models.Model):
    ground = models.ForeignKey(Ground, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    team_name = models.CharField(max_length=255, null=True, blank=True)  # Allow null values
    email = models.EmailField(null=True, blank=True)  # Allow null values
    contact_number = models.CharField(max_length=15, null=True, blank=True)  # Allow null values
    is_paid = models.BooleanField(default=False)  # Track payment status
    temp_lock_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.team_name or 'No Team'} - {self.ground.name} on {self.date} at {self.time_slot.slot}"
