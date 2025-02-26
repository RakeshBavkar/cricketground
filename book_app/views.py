import json
from django.shortcuts import redirect, render, get_object_or_404
from .models import Ground, Booking, User, Engineer,Income_category,Income,Stock,Company_information,Student,Expence_category,Expense,Expense_amount,BackupBooking,Bookings,Payment,TimeSlot,SuperBooking
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from book_app.EmailBackEnd import EmailBackEnd
from django.core.mail import send_mail
from booking_project.settings import EMAIL_HOST_USER
from django.db import IntegrityError
from django.urls import reverse
from django.db.models import Count
import io
import qrcode
import base64
from django.utils import timezone
from datetime import timedelta
def base(request):
    return render(request, 'base/base.html')

def index(request):
    pass
    return render(request, 'index.html')

def LOGIN(request):
    pass
    return render(request, 'login/login.html')

#User login
def doLogin(request):
    if request.method == "POST":
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))

        if user != None:
            login(request, user)
            return redirect('index')            
        else:
            messages.error(request, 'Incorrect Email or Password')
            return redirect('login')
        
#User logout
def do_logout(request):
    logout(request)
    return redirect('login')

#Player registration
def add_player(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        password =request.POST.get('password')

        print(first_name,last_name,email,username,address,gender,password)

        if User.objects.filter(email=email).exists():
            messages.warning(request,'Email already exists')
            return redirect('add_engineer')
        if User.objects.filter(username=username).exists():
            messages.warning(request,'Username already exists')
            return redirect('add_engineer')
        else:
            user = User(
                first_name = first_name,
                last_name = last_name,
                email = email,
                username = username,              
            )
            user.set_password(password)
            user.save()
            print(user)
        engineer = Engineer(
            admin=user,
            address = address,
            gender = gender,
        )
        engineer.save()
        messages.success(request,'Player Successfully Added !')
        return redirect('add_player')

    return render(request,'add_player.html')

#Booking view in calender format
@login_required
def book_slot(request):
    grounds = Ground.objects.all()
    
    # Fetch bookings that are active in the future
    bookings = Booking.objects.filter(start_booking_date__gte=datetime.now(), end_booking_date__gte=datetime.now())

    booked_slots = {
        booking.start_booking_date: booking.is_booked for booking in bookings
    }

    if request.method == "POST":
        ground_id = request.POST.get('ground_id')
        start_booking_date_str = request.POST.get('start_booking_date')
        end_booking_date_str = request.POST.get('end_booking_date')

        start_booking_date = parse_datetime(start_booking_date_str)
        end_booking_date = parse_datetime(end_booking_date_str)

        ground = get_object_or_404(Ground, id=ground_id)

        # Check if slot is already booked
        existing_booking = Booking.objects.filter(
            ground=ground,
            start_booking_date__lt=end_booking_date,
            end_booking_date__gt=start_booking_date,
            is_booked=True
        ).exists()

        if  existing_booking:
            return JsonResponse({'status': 'error', 'message': 'Slot already booked.'})   
        else: 

            # Calculate duration in hours
            duration_in_hours = (end_booking_date - start_booking_date).total_seconds() / 3600  
            total_cost = duration_in_hours * ground.price_per_hour        

            # Create and save booking
            booking = Booking.objects.create(
                ground=ground,
                user=request.user,
                start_booking_date=start_booking_date,
                end_booking_date=end_booking_date,
                is_booked=True,
                total_amount=total_cost  # Store total amount in the database
            )
            redirect_url = reverse('booking_success')  # Dynamically generate the correct URL
            print(f"✅ Redirecting to: {redirect_url}")  # Debugging

            return JsonResponse({
                'status': 'success',
                'message': 'Booking successful.',
                'redirect_url': redirect_url
            })
    else:
        return render(request, 'booking/book_slot.html', {
            'grounds': grounds,
            'booked_slots': booked_slots,
        })

#Slot booking
@login_required
def calendar_view(request):
    ground_records = Booking.objects.filter(is_booked=True).order_by('start_booking_date')

    # Dictionary to store all bookings grouped by date
    booked_details = {}

    for record in ground_records:
        start_date = record.start_booking_date.date()
        end_date = record.end_booking_date.date()
        
        while start_date <= end_date:
            date_str = start_date.strftime('%Y-%m-%d')
            
            if date_str not in booked_details:
                booked_details[date_str] = []
            
            booked_details[date_str].append({
                'ground': record.ground.name,
                'user': record.user.username,
                'start_time': record.start_booking_date.strftime('%H:%M'),
                'end_time': record.end_booking_date.strftime('%H:%M'),
                'total_amount': str(record.total_amount) if record.total_amount else "N/A"
            })
            
            start_date += timedelta(days=1)

    context = {
        'booked_details_json': json.dumps(booked_details),  # Convert to JSON for frontend
    }

    return render(request, 'booking/calendar.html', context)


#Cancel Booking
@login_required
def cancel_booking(request, booking_id):
    # Fetch the booking object by its ID
    booking = get_object_or_404(Booking, id=booking_id)

    # If the request is POST, proceed with cancellation (deletion)
    if request.method == 'POST':
        # Optionally, back up the booking data before deletion (soft backup)
        BackupBooking.objects.create(
            ground=booking.ground,
            user=booking.user,
            start_booking_date=booking.start_booking_date,
            end_booking_date=booking.end_booking_date,
            total_amount=booking.total_amount,
        )

        # Delete the booking (hard delete)
        booking.delete()

        # After cancellation, redirect to booking list or any other page
        # return redirect('booking_list')  # Replace with actual URL name for booking list or success page
    context ={
        'booking':booking
    }
    # If the request is GET, render the confirmation page
    return render(request, 'booking/cancel_booking.html')

#Ground booking information
def show_booking(request):
    booking = Booking.objects.all()    
    context = {
        'booking':booking,
    }
    return render(request,'booking/show_booking.html',context)

#Forgot Password logic
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print('I am from Email',email)
        if User.objects.filter(email=email).exists():
            user=User.objects.get(email=email)
            print('User Exists')
            # email = EmailMessage('Password Reset', 'Body', to=['rakeshbavkar21@gmail.com'])
            # email.send()
            send_mail('Reset Your Password : ',f'Current User :- {user} click here  http://127.0.0.1:8000/booking/new_password_page/{user}/', EMAIL_HOST_USER, {email}, fail_silently=True)
            return HttpResponse('Password Reset link send to your email')
        return render(request,'forgot_password.html')
        
    return render(request,'forgot_password.html')

#Password reset logic
def new_password_page(request,user):
    userid = User.objects.get(username=user)
    print(userid)
    if request.method == 'POST':
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')
        
        print(pass1,pass2)
        if pass1 == pass2:
            userid.set_password(pass1)
            userid.save()
            return HttpResponse('Password Reset')
        else:
            return HttpResponse('Password does not match')
        
        # return render(request,'new_password_page.html')
    return render(request,'new_password_page.html')

#Add income category
def income_category(request):
    if request.method=='POST':
        income_category_name = request.POST.get('income_category_name')
        description = request.POST.get('description')
        date = request.POST.get('date')
        if Income_category.objects.filter(name=income_category_name,description=description).exists():
            messages.warning(request,'Same Name Category already exists ..!')
            return redirect('income_category')
        else:
            category =Income_category(name=income_category_name,description=description,created_at=date)
            category.save()
        
    return render(request,'income_category.html')

#add income against category
def income(request):
    std = Student.objects.all()
    if request.method=="POST":
        student_name = request.POST.get("student_name")
        student_fees = request.POST.get("amount")
        data = Student(student_name = student_name, fees_paid = student_fees)
        data.save()
    return render(request,'student_income.html')

#show income against category and final income
def show_income(request):
    category = request.GET.get('category', '')  # Get selected category
    total_income = 0
    income_data = []

    # Calculate Stadium Booking income
    stadium_income = sum(booking.total_amount for booking in Booking.objects.all())
    print(stadium_income)
    stock_income = sum(stoc.total_amount for stoc in Stock.objects.all())
    print(stock_income)
    student_income = sum(st.fees_paid for st in Student.objects.all())
    print(stadium_income)
    print(stock_income)
    total_expense = Expense_amount.objects.all().last()
    total_ex = total_expense.expense_amount

    # Calculate Student Fees income

    # Total of all incomes
    final_income = stadium_income + stock_income+student_income-total_ex

    if category == "stadium_booking":
        income_data = Booking.objects.all()
        total_income = stadium_income
    elif category == "stock_income":
        income_data = Stock.objects.all()
        total_income = stock_income
    elif category == "student_fees":
        income_data = Student.objects.all()
        total_income = student_income
    Context = {
        'category': category,
        'income_data': income_data,
        'total_income': total_income,
        'final_income': final_income,
        'total_ex':total_ex
    }

    return render(request,'show_income.html',Context)

#Add company information
def company_information(request):
    if request.method=='POST':
        company_name=request.POST.get('company_name')
        address=request.POST.get('address')
        gst_number=request.POST.get('gst_no')
        date=request.POST.get('date')
        
        company_details=Company_information(company_name=company_name,
                                            address=address,
                                            gst_number=gst_number,
                                            date=date,
                                            )
        company_details.save()
    return render(request,'company_info.html')

#Add stock here
def stock(request):
    company_info=Company_information.objects.all()
    if request.method=='POST':
        com_info=request.POST.get('company_name')
        company_information=Company_information.objects.get(id=com_info)
        product_name=request.POST.get('product_name')
        qty=request.POST.get('qty')
        rate=request.POST.get('rate')
        discount=request.POST.get('discount')
        cgst=request.POST.get('cgst')
        sgst=request.POST.get('sgst')
        t= int(qty)*int(rate)
        total_discount=(t*int(discount)/100)
        total_dis=t-total_discount
        cgst_total=total_dis*int(cgst)/100
        sgst_total=total_dis*int(sgst)/100
        total=total_dis+cgst_total+sgst_total        
        
        stock_item=Stock(company_information=company_information,
                        product_name=product_name,
                        qty=qty,
                        rate=rate,
                        discount=discount,
                        cgst=cgst,
                        sgst=sgst,
                        total_amount=total,
                        )
        stock_item.save()           
    context={
        
        'company_info':company_info,
        
    }
        
    return render(request,'stock.html',context)

#Show stock details
def stock_details(request):
    company_id = request.GET.get('category', '')  # Get selected company ID

    # Get all companies for the dropdown
    companies = Company_information.objects.all()

    # If a company is selected, filter stock data; otherwise, show an empty list
    stock_display = Stock.objects.filter(company_information__id=company_id) if company_id else []

    # Calculate final total (only if stock data exists)
    final_total = sum(stock_display.values_list('total_amount', flat=True)) if stock_display else 0

    context = {
        'stock_display': stock_display,
        'final_total': final_total,
        'companies': companies,
        'selected_company': int(company_id) if company_id else '',  # Keep dropdown selection
    }

    return render(request, 'stock_details.html', context)    

def expense_category(request):
    if request.method == 'POST':
        expense_name = request.POST.get("expense_name")
        date = request.POST.get('date')

        if Expence_category.objects.filter(name=expense_name).exists():
            messages.warning(request,'Same Name Category already exists ..!')
            return redirect('income_category')
        else:
            category =Expence_category(name=expense_name, created_at=date)
            category.save()

    return render(request, "expence_category.html")

def expense(request):
    ex = Expence_category.objects.all()
    
    if request.method == 'POST':
        expense_name = request.POST.get('expense')
        description = request.POST.get('expense_ds')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        print(date)
        exp = Expence_category.objects.filter(name=expense_name).first()
    
        data = Expense(expence_category_name = exp, ex_amount = amount, created_at = date, description = description)
        data.save()
        messages.success(request,'Expense added successfully ..!')
    else:
            messages.error(request,"Expense Category not found!")
            
       
    
    Context = {
        'ex':ex
        
    }
    return render(request, 'expense.html',Context)

def show_expense(request):
    Ex = Expense.objects.all()

    # Convert ex_amount to float before summing
    total_amount = sum(totals.ex_amount for totals in Ex)
    ex_amount = Expense_amount(expense_amount= total_amount)
    ex_amount.save()

    context = {
        'ex': Ex,  # Pass expenses list
        'total_amount': total_amount  # Ensure consistency
    }
    return render(request, 'show_expense.html', context)

def booking_list(request):
    # Fetch all bookings for the current user
    bookings = Payment.objects.all()
    context ={
        'bookings':bookings
    }
    return render(request, 'booking/booking_list.html',context)


    

# Payment View
def home(request):
    grounds = Ground.objects.all()
    time_slots = TimeSlot.objects.values_list("slot", flat=True)  # Fetch all slots
    selected_date = request.GET.get("date")  # Get selected date from URL

    if request.method == "POST":
        ground_id = request.POST.get("ground_id")
        date = request.POST.get("date")
        time_slot_str = request.POST.get("time_slot")

        ground = Ground.objects.get(id=ground_id)
        time_slot = TimeSlot.objects.filter(slot=time_slot_str).first()

        if not time_slot:
            return render(request, "home.html", {
                "grounds": grounds,
                "time_slots": time_slots,
                "error": "Invalid time slot selected!",
            })

        # Check if slot is already booked
        if SuperBooking.objects.filter(ground=ground, date=date, time_slot=time_slot, is_paid=True).exists():
            return render(request, "home.html", {
                "grounds": grounds,
                "time_slots": time_slots,
                "error": "This slot is already booked!",
                "selected_date": selected_date,
            })

        # Check if slot is temporarily locked
        existing_lock = SuperBooking.objects.filter(
            ground=ground,
            date=date,
            time_slot=time_slot,
            temp_lock_until__gt=timezone.now()  # Check if lock is still valid
        ).first()

        if existing_lock:
            return render(request, "home.html", {
                "grounds": grounds,
                "time_slots": time_slots,
                "error": "This slot is temporarily locked. Try again later.",
                "selected_date": selected_date,
            })

        # Calculate total cost based on slot duration
        slot_duration = 2 if "AM" in time_slot.slot else 3.5
        total_cost = ground.price_per_hour * slot_duration

        # Save booking in session
        request.session["booking_data"] = {
            "ground_id": ground.id,
            "date": date,
            "time_slot": time_slot_str,
            "total_cost": total_cost,
            "ground": ground.name
        }

        return redirect("payment_page")

    # Fetch booked + locked slots for each ground (only for selected date)
    for ground in grounds:
        booked_slots = SuperBooking.objects.filter(ground=ground, is_paid=True)

        locked_slots = SuperBooking.objects.filter(
            ground=ground,
            temp_lock_until__gt=timezone.now()  # Slots locked but not paid
        )

        if selected_date:
            booked_slots = booked_slots.filter(date=selected_date)
            locked_slots = locked_slots.filter(date=selected_date)

        # Combine booked and locked slots
        ground.booked_slots = list(booked_slots.values_list("time_slot__slot", flat=True))
        ground.locked_slots = list(locked_slots.values_list("time_slot__slot", flat=True))

    return render(request, "home.html", {
        "grounds": grounds,
        "time_slots": time_slots,
        "selected_date": selected_date,  # Pass selected date to template
    })

@login_required
def payment(request):
    bookings = Booking.objects.order_by('-id')[:10]
    all_book = Booking.objects.filter(id__in=Payment.objects.values('booking').annotate(payment_count=Count('id')).filter(payment_count__lt=2).values('booking'))


   
    total_amount = None
    team_payment = None
    selected_booking = None

    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        booking = Booking.objects.get(id=booking_id)
        selected_booking = booking

        # Check if payment already exists for this booking
        payment_exists = Payment.objects.filter(booking=booking, user=request.user).exists()
        payments = Payment.objects.filter(booking=booking)

        if payments.count() >= 2:
            return render(request, 'paymentss.html')

        if payment_exists:
            return render(request, 'payment_page.html')

        # Calculate the total amount and divide it for two teams (each pays half)
        total_amount = booking.total_amount
        amount_to_pay = total_amount / 2
        team_payment = amount_to_pay

        # If it's Team A making the first payment
        if booking.user == request.user:
            paid_payment = amount_to_pay
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                paid_payment=paid_payment
            )
            message = f"Payment successful. You have paid ₹{paid_payment:.2f}."

        else:
            # Team B making the remaining payment
            remaining_payment = total_amount - amount_to_pay
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                paid_payment=remaining_payment
            )
            message = f"Payment successful. You have paid ₹{remaining_payment:.2f}."

        return render(request, 'Make_Payment.html', {'message': message, 'payment': payment})

    return render(request, 'Make_Payment.html', {
        'bookings': bookings,
        'total_amount': total_amount,
        'team_payment': team_payment,
        'selected_booking': selected_booking,
        'all_book':all_book
    })

def payment_exists(request):
    return render(request, 'payment_page.html')

def paymentss(request):
    return render(request, 'paymentss.html')

def booking_success(request):
    return render(request, 'booking/booking_success.html')

def payment_status(request):
    bookings = Payment.objects.filter(user=request.user)
    context ={
        'bookings':bookings
    }
    return render(request, 'payment_status.html',context)

def payment_page(request):
    booking_data = request.session.get("booking_data", {})

    if not booking_data:
        return redirect("home")  # Redirect to home if session data is missing

    try:
        ground = Ground.objects.get(id=booking_data["ground_id"])
    except Ground.DoesNotExist:
        return redirect("home")  # Redirect if ground doesn't exist

    if request.method == "POST":
        team_name = request.POST.get("team_name")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")

        # Store user details in session before proceeding to payment
        request.session["booking_data"].update({
            "team_name": team_name,
            "email": email,
            "contact_number": contact_number
        })
        request.session.modified = True  # Ensure session updates are saved

        return redirect("generate_qr")  # Redirect to QR code generation

    return render(request, "payments.html", {"ground": booking_data["ground_id"],
        "date": booking_data["date"],
        "time_slot": booking_data["time_slot"],
        "total_cost": booking_data["total_cost"],
        "ground": {
        "id": ground.id,
        "name": ground.name,  # Replace with actual field names in your model
        "location": ground.location
    }})



def generate_qr(request):
    booking_data = request.session.get("booking_data", {})

    if not booking_data or not all(key in booking_data for key in ["team_name", "email", "contact_number"]):
        return redirect("payment_page")  # Ensure user has filled the form
    
    ground = Ground.objects.get(id=booking_data["ground_id"])
    time_slot = TimeSlot.objects.get(slot=booking_data["time_slot"])

    # Check for existing locked or booked slots
    existing_booking = SuperBooking.objects.filter(
        ground=ground,
        date=booking_data["date"],
        time_slot=time_slot
    ).first()

    if existing_booking:
        if existing_booking.is_paid:
            return redirect("home")  # Redirect if already booked
        if existing_booking.temp_lock_until and existing_booking.temp_lock_until > timezone.now():
            temp_lock_until = existing_booking.temp_lock_until  # Use existing lock time
        else:
            temp_lock_until = timezone.now() + timedelta(minutes=1)  # Reset lock
            existing_booking.temp_lock_until = temp_lock_until
            existing_booking.save()
    else:
        temp_lock_until = timezone.now() + timedelta(minutes=1)  # New lock
        SuperBooking.objects.create(
            ground=ground,
            date=booking_data["date"],
            time_slot=time_slot,
            total_cost=booking_data["total_cost"],
            team_name=booking_data["team_name"],
            email=booking_data["email"],
            contact_number=booking_data["contact_number"],
            temp_lock_until=temp_lock_until
        )

    # UPI Payment Details
    upi_id = "yourname@upi"  # Replace with your actual UPI ID
    upi_link = f"upi://pay?pa={upi_id}&pn=Ground Booking&mc=&tid=&tr=&tn=Ground Booking&am={booking_data['total_cost']}&cu=INR"

    # Generate QR code with UPI Payment Link
    qr = qrcode.make(upi_link)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    if request.method == "POST":  # Simulating payment success
        existing_booking.is_paid = True
        existing_booking.temp_lock_until = None
        existing_booking.save()

        # Clear session data after booking is confirmed
        request.session.pop("booking_data", None)

        return redirect("home")  # Redirect to home after successful booking

    return render(request, "generate_qr.html", {
        "qr_code": qr_base64,
        "booking_data": booking_data,
        "ground": ground,
        "lock_expiry": temp_lock_until.strftime("%Y-%m-%d %H:%M:%S")  # Send lock expiry time
    })
