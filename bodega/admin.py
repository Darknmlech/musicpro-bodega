from django.contrib import admin
from .models import (
    Categoria, Marca, Ubicacion, Producto, 
    Rol, Usuario, Sucursal, TipoMovimiento, 
    OrdenMovimiento, DetalleOrden
)

admin.site.register(Categoria)
admin.site.register(Marca)
admin.site.register(Ubicacion)
admin.site.register(Producto)
admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Sucursal)
admin.site.register(TipoMovimiento)
admin.site.register(OrdenMovimiento)
admin.site.register(DetalleOrden)