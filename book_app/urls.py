from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
    path('', views.LOGIN, name='login'),
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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)