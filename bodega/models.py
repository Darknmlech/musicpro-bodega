from django.db import models

# Create your models here.

class Ubicacion(models.Model):
    zona = models.CharField(max_length=50)
    pasillo = models.CharField(max_length=50)
    estante = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Zona {self.zona} - Pasillo {self.pasillo}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    sku = models.CharField(max_length=50, primary_key=True, verbose_name="SKU")
    nombre = models.CharField(max_length=150)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"[{self.sku}] {self.nombre}"

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    nombre_completo = models.CharField(max_length=150)
    correo_electronico = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=128)
    estado_activo = models.BooleanField(default=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre_completo

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nombre

class TipoMovimiento(models.Model):
    nombre = models.CharField(max_length=50)
    operacion = models.CharField(max_length=10)
    
    def __str__(self):
        return self.nombre

class OrdenMovimiento(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoMovimiento, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)

class DetalleOrden(models.Model):
    cantidad = models.IntegerField()
    orden = models.ForeignKey(OrdenMovimiento, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, to_field='sku')
    