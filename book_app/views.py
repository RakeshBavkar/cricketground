import json
from django.shortcuts import redirect, render, get_object_or_404
from .models import Ground, Booking, User, Engineer,Income_category,Income,Stock,Company_information,Student,Expence_category,Expense,Expense_amount
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from book_app.EmailBackEnd import EmailBackEnd
from django.core.mail import send_mail
from booking_project.settings import EMAIL_HOST_USER

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

        if existing_booking:
            return JsonResponse({'status': 'error', 'message': 'Slot already booked.'})    

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

        return JsonResponse({'status': 'success', 'message': 'Booking successful.', 'total_amount': total_cost})

    return render(request, 'booking/book_slot.html', {
        'grounds': grounds,
        'booked_slots': booked_slots,
    })

#Slot booking
@login_required
def calendar_view(request):
    ground_records = Booking.objects.filter(is_booked=True).order_by('start_booking_date')

    # Generate all booked dates between start and end for each booking
    booked_dates = set()
    for record in ground_records:
        start_date = record.start_booking_date.date()
        end_date = record.end_booking_date.date()
        while start_date <= end_date:
            booked_dates.add(start_date.strftime('%Y-%m-%d'))
            start_date += timedelta(days=1)  # Move to the next day

    context = {
        'ground_records_json': json.dumps(list(booked_dates)),  # Convert to JSON list for frontend
    }

    return render(request, 'booking/calendar.html', context)

#Cancel Booking
@login_required
def cancel_booking(request):    
    if request.method == "POST":
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        # Cancel the booking
        # booking.is_booked = False
        # booking.save()
        booking.delete()
        # return JsonResponse({'status': 'success', 'message': 'Booking cancelled.'})
        return redirect('cancel_booking')    
    return render(request,'booking/cancel_booking.html')

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