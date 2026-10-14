import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicpro.settings')
django.setup()

from faker import Faker
from bodega.models import Categoria, Marca, Ubicacion, Producto, Rol, Usuario, Sucursal, TipoMovimiento, OrdenMovimiento, DetalleOrden

fake = Faker('es_CL')

# Crear registros base necesarios
cat, _ = Categoria.objects.get_or_create(nombre="Cuerdas", descripcion="Guitarras")
marca, _ = Marca.objects.get_or_create(nombre="Fender", contacto="contacto@fender.com")
ubic, _ = Ubicacion.objects.get_or_create(zona="A", pasillo="1", estante="2")
rol, _ = Rol.objects.get_or_create(nombre="Bodeguero")
usu, _ = Usuario.objects.get_or_create(nombre_completo="Bodeguero01", correo_electronico="b@musicpro.cl", contrasena="123", rol=rol)
suc, _ = Sucursal.objects.get_or_create(nombre="Santiago", direccion="Alameda", telefono="123456")
tipo, _ = TipoMovimiento.objects.get_or_create(nombre="Ingreso", operacion="+")

print("Generando productos y movimientos de prueba...")
for i in range(10):
    prod = Producto.objects.create(
        sku=f"SKU-{random.randint(1000,9999)}",
        nombre=f"Guitarra {fake.word()}",
        stock_actual=random.randint(5, 30),
        stock_minimo=5,
        precio=random.randint(100000, 500000),
        categoria=cat,
        marca=marca,
        ubicacion=ubic
    )
    
    # 1. Crear la cabecera del movimiento
    orden = OrdenMovimiento.objects.create(
        usuario=usu,
        tipo=tipo,
        sucursal=suc,
        observaciones="Carga automática"
    )

    # 2. Crear el detalle asociado con el producto y la cantidad
    DetalleOrden.objects.create(
        orden=orden,
        producto=prod,
        cantidad=random.randint(1, 10)
    )

print("¡Datos de prueba creados con éxito!")