from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Producto, OrdenMovimiento, DetalleOrden, Rol
from .forms import UsuarioForm, ProductoForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('correo')
        passw = request.POST.get('contrasena')
        
        user = authenticate(request, username=username, password=passw)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error = "Correo o contraseña incorrectos."
            return render(request, 'bodega/login.html', {'error': error})
            
    return render(request, 'bodega/login.html')

def register_view(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        passw = request.POST.get('contrasena')
        
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=passw,
            first_name=nombre
        )
        return redirect('login')
    return render(request, 'bodega/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    total_productos = Producto.objects.count()
    alertas_stock = Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count()
    
    ultimos_movimientos_qs = OrdenMovimiento.objects.all().order_by('-fecha_hora')[:5]
    ultimos_movimientos = []
    for o in ultimos_movimientos_qs:
        detalles = DetalleOrden.objects.filter(orden=o).first()
        
        # Obtener nombre de usuario de forma segura sin causar AttributeError
        if hasattr(o.usuario, 'get_full_name') and callable(o.usuario.get_full_name):
            nombre_usu = o.usuario.get_full_name()
        else:
            nombre_usu = getattr(o.usuario, 'nombre', None) or getattr(o.usuario, 'username', None) or str(o.usuario)

        ultimos_movimientos.append({
            'tipo': o.tipo.nombre,
            'producto': detalles.producto.nombre if detalles else 'Varios',
            'cantidad': detalles.cantidad if detalles else 0,
            'usuario': nombre_usu,
            'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M')
        })

    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username

    return render(request, 'bodega/dashboard.html', {
        'total_productos': total_productos,
        'alertas_stock': alertas_stock,
        'ultimos_movimientos': ultimos_movimientos,
        'usuario_nombre': usuario_actual
    })

@login_required
def inventario_view(request):
    productos = Producto.objects.select_related('categoria', 'ubicacion').all()
    lista_productos = [{
        'id': p.pk,  # Solucionado usando .pk en lugar de .id
        'codigo': p.sku,
        'nombre': p.nombre,
        'categoria': p.categoria.nombre,
        'ubicacion': f"Z:{p.ubicacion.zona} P:{p.ubicacion.pasillo}",
        'stock': p.stock_actual,
        'stock_minimo': p.stock_minimo
    } for p in productos]
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username

    return render(request, 'bodega/inventario.html', {
        'productos': lista_productos,
        'usuario_nombre': usuario_actual
    })

@login_required
def movimientos_view(request):
    ordenes = OrdenMovimiento.objects.select_related('usuario', 'tipo').all().order_by('-fecha_hora')[:50]
    movimientos = []
    for o in ordenes:
        detalle = DetalleOrden.objects.filter(orden=o).first()
        
        if hasattr(o.usuario, 'get_full_name') and callable(o.usuario.get_full_name):
            nombre_usu = o.usuario.get_full_name()
        else:
            nombre_usu = getattr(o.usuario, 'nombre', None) or getattr(o.usuario, 'username', None) or str(o.usuario)

        movimientos.append({
            'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M'),
            'tipo': o.tipo.nombre,
            'producto': detalle.producto.nombre if detalle else 'Sin producto',
            'cantidad': detalle.cantidad if detalle else 0,
            'usuario': nombre_usu
        })
        
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
        
    return render(request, 'bodega/movimientos.html', {
        'movimientos': movimientos,
        'usuario_nombre': usuario_actual
    })


@login_required
def usuarios_list_view(request):
    usuarios = User.objects.all().order_by('-date_joined')
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/usuarios_list.html', {
        'usuarios': usuarios,
        'usuario_nombre': usuario_actual
    })

@login_required
def usuario_create_view(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/usuario_form.html', {
        'form': form, 
        'titulo': 'Crear Usuario',
        'usuario_nombre': usuario_actual
    })

@login_required
def usuario_edit_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('usuarios_list')
    else:
        form = UsuarioForm(instance=usuario)
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/usuario_form.html', {
        'form': form, 
        'titulo': 'Editar Usuario',
        'usuario_nombre': usuario_actual
    })

@login_required
def usuario_toggle_active_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return redirect('usuarios_list')


@login_required
def producto_create_view(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventario')
    else:
        form = ProductoForm()
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/producto_form.html', {
        'form': form, 
        'titulo': 'Agregar Producto',
        'usuario_nombre': usuario_actual
    })

@login_required
def producto_edit_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('inventario')
    else:
        form = ProductoForm(instance=producto)
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/producto_form.html', {
        'form': form, 
        'titulo': 'Editar Producto',
        'usuario_nombre': usuario_actual
    })

@login_required
def producto_delete_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('inventario')
    
    usuario_actual = getattr(request.user, 'first_name', None) or getattr(request.user, 'nombre', None) or request.user.username
    return render(request, 'bodega/producto_confirm_delete.html', {
        'producto': producto,
        'usuario_nombre': usuario_actual
    })