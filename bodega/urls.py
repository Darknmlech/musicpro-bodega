from django.urls import path
from .views import (
    dashboard_view, inventario_view, movimientos_view, 
    login_view, register_view, logout_view,
    usuarios_list_view, usuario_create_view, usuario_edit_view, usuario_toggle_active_view,
    producto_create_view, producto_edit_view, producto_delete_view
)

urlpatterns = [
    path('', login_view, name='login'),
    path('registro/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('inventario/', inventario_view, name='inventario'),
    path('movimientos/', movimientos_view, name='movimientos'),
    
    path('usuarios/', usuarios_list_view, name='usuarios_list'),
    path('usuarios/crear/', usuario_create_view, name='usuario_create'),
    path('usuarios/editar/<int:pk>/', usuario_edit_view, name='usuario_edit'),
    path('usuarios/estado/<int:pk>/', usuario_toggle_active_view, name='usuario_toggle_active'),
    
    path('productos/crear/', producto_create_view, name='producto_create'),
    path('productos/editar/<str:pk>/', producto_edit_view, name='producto_edit'),
    path('productos/eliminar/<str:pk>/', producto_delete_view, name='producto_delete'),
]