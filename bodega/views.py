from django.shortcuts import render, redirect
from django.db.models import F
from .models import Producto, OrdenMovimiento, DetalleOrden, Usuario, Rol

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        passw = request.POST.get('contrasena')
        try:
            user = Usuario.objects.get(correo_electronico=correo, contrasena=passw)
            request.session['usuario_id'] = user.id
            request.session['usuario_nombre'] = user.nombre_completo
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            error = "Correo o contraseña incorrectos."
            return render(request, 'bodega/login.html', {'error': error})
    return render(request, 'bodega/login.html')

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        passw = request.POST.get('contrasena')
        
        rol, _ = Rol.objects.get_or_create(nombre="Bodeguero")
        
        Usuario.objects.create(
            nombre_completo=nombre,
            correo_electronico=correo,
            contrasena=passw,
            rol=rol
        )
        return redirect('login')
    return render(request, 'bodega/register.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

def dashboard_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    total_productos = Producto.objects.count()
    alertas_stock = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    
    ultimos_movimientos_qs = OrdenMovimiento.objects.all().order_by('-fecha_hora')[:5]
    ultimos_movimientos = []
    for o in ultimos_movimientos_qs:
        detalles = DetalleOrden.objects.filter(orden=o).first()
        ultimos_movimientos.append({
            'tipo': o.tipo.nombre,
            'producto': detalles.producto.nombre if detalles else 'Varios',
            'cantidad': detalles.cantidad if detalles else 0,
            'usuario': o.usuario.nombre_completo,
            'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M')
        })

    return render(request, 'bodega/dashboard.html', {
        'total_productos': total_productos,
        'alertas_stock': alertas_stock,
        'ultimos_movimientos': ultimos_movimientos,
        'usuario_nombre': request.session.get('usuario_nombre')
    })

def inventario_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    productos = Producto.objects.select_related('categoria', 'ubicacion').all()
    lista_productos = [{
        'codigo': p.sku,
        'nombre': p.nombre,
        'categoria': p.categoria.nombre,
        'ubicacion': f"Z:{p.ubicacion.zona} P:{p.ubicacion.pasillo}",
        'stock': p.stock_actual,
        'stock_minimo': p.stock_minimo
    } for p in productos]
    
    return render(request, 'bodega/inventario.html', {
        'productos': lista_productos,
        'usuario_nombre': request.session.get('usuario_nombre')
    })

def movimientos_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    ordenes = OrdenMovimiento.objects.select_related('usuario', 'tipo').all().order_by('-fecha_hora')[:50]
    movimientos = []
    for o in ordenes:
        detalle = DetalleOrden.objects.filter(orden=o).first()
        movimientos.append({
            'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M'),
            'tipo': o.tipo.nombre,
            'producto': detalle.producto.nombre if detalle else 'Sin producto',
            'cantidad': detalle.cantidad if detalle else 0,
            'usuario': o.usuario.nombre_completo
        })
        
    return render(request, 'bodega/movimientos.html', {
        'movimientos': movimientos,
        'usuario_nombre': request.session.get('usuario_nombre')
    })