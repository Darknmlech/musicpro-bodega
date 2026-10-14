from django.urls import path
from .views import dashboard_view, inventario_view, movimientos_view, login_view, register_view, logout_view

urlpatterns = [
    path('', login_view, name='login'), # La raíz ahora pide iniciar sesión primero
    path('registro/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('inventario/', inventario_view, name='inventario'),
    path('movimientos/', movimientos_view, name='movimientos'),
]