from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.shortcuts import get_object_or_404
from datetime import datetime
from django.core.files.base import ContentFile
import qrcode
import io
from .models import Feature, Confirmation
from django.db.models import Q
from io import BytesIO
import base64
from django.utils.html import format_html
# Create your views here.

def index(request):
    return render(request, 'index.html')

def register(request):
    print("CSRF Token (Cookie):", request.COOKIES.get('csrftoken'))
    print("CSRF Token (POST):", request.POST.get('csrfmiddlewaretoken'))
    if request.method == 'POST':
        print("POST request received")
        print(request.POST)
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Passwords mismatch')
            return render(request, 'register.html')
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Invalid credentials")
            return redirect('login')
    else:
        return render(request, 'login.html')

def style(request):
    return render(request, 'style.css')

def logout(request):
    auth.logout(request)
    return redirect('/')

def DestinationDetails(request):
    if request.method == 'GET':
        from_location = request.GET.get('from_location')
        to_location = request.GET.get('to_location')
        booking_date_str = request.GET.get('bookingdate')
        
        if not (from_location and to_location and booking_date_str):
            messages.error(request, 'Please fill in all the required fields including Date.')
            return redirect('index')
        
        booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date() if booking_date_str else None
        booking_date_str = str(booking_date)
        request.session['booking_date'] = booking_date_str
        print(from_location, to_location, booking_date)
        routes = Feature.objects.filter(Q(fromdesti__icontains=from_location) | Q(todesti__icontains=to_location))
        if routes:
            return render(request, 'Destinationdetails.html', {'routes': routes})
        else:
            messages.info(request, "No routes found. Please search for other places.")
            return render(request, 'Destinationdetails.html')

@login_required
def user_confirmation(request, route_id):
    route = get_object_or_404(Feature, pk=route_id)
    return render(request, 'userconfirmation.html', {'fromdesti': route.fromdesti, 'todesti': route.todesti,
                                                      'booking_date': request.session.get('booking_date')})

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_image_base64 = buffer.getvalue()
    return qr_code_image_base64

def generate_qr_code1(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_code_image_base64
from django.conf import settings
@login_required
def confirmation(request):
    if request.method == 'POST':
        print(request.POST)
        from_location = request.POST.get('fromdesti')
        to_location = request.POST.get('todesti')
        passenger_name = request.POST.get('passenger_name')
        email = request.POST.get('email')
        selected_payment_mode = request.GET.get('selected_payment_mode')
        booking_date = request.session.get('booking_date')
    

        print(passenger_name, email, selected_payment_mode, f'Fromdesti: {from_location}, Todesti: {to_location}')
        unique_code = f"{request.user}_{from_location}_{to_location}"
        confirmation_obj = Confirmation.objects.create(
            user=request.user,
            from_location=from_location,
            to_location=to_location,
            passenger_name=passenger_name,
            email=email,
            payment_mode=selected_payment_mode,
            booking_date=booking_date,
        )
        send_mail("Thank you for your Booking",
                  f"{passenger_name} your Ticket is successfully booked from {from_location} to {to_location} on {booking_date}. Here is your QR CODE ",
                  settings.EMAIL_HOST_USER,
                  [email],
                  fail_silently=True,
                  html_message=f'<p>{passenger_name}, your Ticket is successfully booked from {from_location} to {to_location} on {booking_date}. Here is your QR CODE:</p><br><img src="cid:qr_code_image" alt="QR Code">'
                  )
        qr_code_data_mail = f"Ticket Code: {unique_code}\nFrom: {from_location}\nTo: {to_location}"
        qr_code_data_successhtml = f"Ticket Code: {unique_code}\nFrom: {from_location}\nTo: {to_location}"
        qr_code_image_mail_send = generate_qr_code(qr_code_data_mail)
        qr_code_image_success_html=generate_qr_code1(qr_code_data_successhtml)
        

        
        msg = EmailMultiAlternatives(
            "Thank you for your Booking",
            f"{passenger_name} your Ticket is successfully booked from {from_location} to {to_location} on {booking_date}. Here is your QR CODE ",
            settings.EMAIL_HOST_USER,
            [email],
        )
        msg.attach_alternative(f'<img src="cid:qr_code_image" alt="QR Code">', "text/html")
        msg.mixed_subtype = 'related'
# Attach the QR code image directly without using confirmation_obj.qr_code.path
        msg.attach("qr_code_image.png", qr_code_image_mail_send, "image/png")
        msg.send()
        print(qr_code_image_mail_send)
        return render(request, 'success.html', {
            'from_location': from_location,
            'to_location': to_location,
            'passenger_name': passenger_name,
            'email': email,
            'booking_date': booking_date,
            'qr_code_image': qr_code_image_success_html,
        })

    return render(request, 'conformation.html')
   
def tickets_view(request):
    if request.user.is_authenticated:
        user_tickets = Confirmation.objects.filter(user=request.user)
        if user_tickets:
            return render(request, 'tickets.html', {'user_tickets': user_tickets, 'user': request.user})
        else:
            return render(request, 'tickets.html', {'user_tickets': None, 'user': request.user, 'message': 'No Tickets found'})
    else:
        return HttpResponse("<h1>Please <a href='{% url 'login' %}'>login/register</a> to view your tickets.</h1>")


        
def routes(request):
    features=Feature.objects.all()
    return render(request, 'routes.html',{'features':features})
def parcel_delivery(request):
    return render(request,'parcel_delivery.html')


