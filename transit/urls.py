from . import views
from django.urls import path
from django.conf import settings

from django.conf.urls.static import static
# from .views import booking_view
urlpatterns = [
    path('', views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('',views.style),
    path('logout',views.logout,name="logout"),
    path('search',views.DestinationDetails,name="search"),
    path('tickets/', views.tickets_view, name='tickets'),
    path('tickets/logout', views.logout, name='logout'),
    path('tickets/login', views.login, name='login'),
    path('parcel_delivery/', views.parcel_delivery, name='parcel_delivery'),
    path('routes/', views.routes,name='routes'),
    path('user-confirmation/<int:route_id>/', views.user_confirmation, name='user_confirmation'),

    path('confirmation/',views.confirmation,name="confirmation")
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)