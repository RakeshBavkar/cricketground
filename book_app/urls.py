from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.LOGIN, name='login'),
    path('payment/', views.payment, name='payment'),
    path('paymentss/', views.paymentss, name='paymentss'),
    path('payment/payment_exists', views.payment_exists, name='payment_exists'),
    path('index/',views.index,name='index'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('calendar_view/ ', views.calendar_view, name='calendar_view'),
    path('book/', views.book_slot, name='book_slot'),
    path('cancel/', views.cancel_booking, name='cancel_booking'),
    path('show_booking/',views.show_booking,name='show_booking'),    
    path('do_logout/', views.do_logout, name='do_logout'),
    path('add_player/',views.add_player,name='add_player'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('new_password_page/<str:user>/',views.new_password_page,name='new_password_page'),
    path('income_category/',views.income_category,name='income_category'),
    path('income/',views.income,name='income'),
    path('show_income/',views.show_income,name='show_income'),
    path('stock/',views.stock,name='stock'),
    path('stock_details/',views.stock_details,name='stock_details'),
    path('company_information/',views.company_information,name='company_information'),
    path('expense_category', views.expense_category, name='expense_category'),
    path('expense', views.expense, name='expense'),
    path('show_expense', views.show_expense, name='show_expense'),
    path('booking_list', views.booking_list, name='booking_list'),
    path('booking_success', views.booking_success, name='booking_success'),
    path('payment_status', views.payment_status, name='payment_status'),
    path('payment_page/', views.payment_page, name='payment_page'),
    path('generate_qr/', views.generate_qr, name='generate_qr'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)