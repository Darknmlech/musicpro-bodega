from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UsuarioForm
from .models import (
    Categoria,
    DetalleOrden,
    Marca,
    OrdenMovimiento,
    Producto,
    Rol,
    Sucursal,
    Ubicacion,
)


def login_view(request):
  if request.user.is_authenticated:
    return redirect('dashboard')

  error = None
  if request.method == 'POST':
    username = request.POST.get('correo')
    passw = request.POST.get('contrasena')

    user = authenticate(request, username=username, password=passw)
    if user is not None:
      login(request, user)
      return redirect('dashboard')
    else:
      error = 'Correo o contraseña incorrectos.'
      return render(request, 'bodega/login.html', {'error': error})

  return render(request, 'bodega/login.html')


def register_view(request):
  error = None
  if request.method == 'POST':
    nombre = request.POST.get('nombre')
    correo = request.POST.get('correo')
    passw = request.POST.get('contrasena')

    if User.objects.filter(username=correo).exists():
      error = 'Este correo ya está registrado en el sistema.'
    else:
      User.objects.create_user(
          username=correo, email=correo, password=passw, first_name=nombre
      )
      return redirect('login')

  return render(request, 'bodega/register.html', {'error': error})


def logout_view(request):
  logout(request)
  return redirect('login')


@login_required
def dashboard_view(request):
  total_productos = Producto.objects.count()
  alertas_stock = Producto.objects.filter(
      stock_actual__lte=F('stock_minimo')
  ).count()

  ultimos_movimientos_qs = (
      OrdenMovimiento.objects.select_related('usuario', 'tipo', 'sucursal')
      .all()
      .order_by('-fecha_hora')[:5]
  )
  ultimos_movimientos = []
  for o in ultimos_movimientos_qs:
    detalles = DetalleOrden.objects.filter(orden=o).first()
    nombre_usu = (
        getattr(o.usuario, 'nombre_completo', None)
        or getattr(o.usuario, 'username', None)
        or 'Sistema'
    )

    ultimos_movimientos.append({
        'tipo': o.tipo.nombre,
        'producto': detalles.producto.nombre if detalles else 'Varios',
        'cantidad': detalles.cantidad if detalles else 0,
        'usuario': nombre_usu,
        'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M'),
    })

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )

  return render(
      request,
      'bodega/dashboard.html',
      {
          'total_productos': total_productos,
          'alertas_stock': alertas_stock,
          'ultimos_movimientos': ultimos_movimientos,
          'usuario_nombre': usuario_actual,
      },
  )


@login_required
def inventario_view(request):
  productos = Producto.objects.select_related(
      'categoria', 'ubicacion', 'marca'
  ).all()
  lista_productos = []
  for p in productos:
    lista_productos.append({
        'id': p.pk,
        'codigo': p.sku,
        'nombre': p.nombre,
        'categoria': p.categoria.nombre if p.categoria else 'Sin Categoría',
        'ubicacion': (
            f'Z:{p.ubicacion.zona} P:{p.ubicacion.pasillo}'
            if p.ubicacion
            else 'Sin Ubicación'
        ),
        'stock': p.stock_actual,
        'stock_minimo': p.stock_minimo,
        'precio': p.precio,
    })

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/inventario.html',
      {'productos': lista_productos, 'usuario_nombre': usuario_actual},
  )


@login_required
def movimientos_view(request):
  ordenes = (
      OrdenMovimiento.objects.select_related('usuario', 'tipo', 'sucursal')
      .all()
      .order_by('-fecha_hora')[:50]
  )
  movimientos = []
  for o in ordenes:
    detalle = DetalleOrden.objects.filter(orden=o).first()
    nombre_usu = (
        getattr(o.usuario, 'nombre_completo', None)
        or getattr(o.usuario, 'username', None)
        or 'Sistema'
    )

    movimientos.append({
        'fecha': o.fecha_hora.strftime('%Y-%m-%d %H:%M'),
        'tipo': o.tipo.nombre,
        'producto': detalle.producto.nombre if detalle else 'Sin producto',
        'cantidad': detalle.cantidad if detalle else 0,
        'usuario': nombre_usu,
        'sucursal': o.sucursal.nombre if o.sucursal else 'Central',
    })

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/movimientos.html',
      {'movimientos': movimientos, 'usuario_nombre': usuario_actual},
  )


@login_required
def usuarios_list_view(request):
  usuarios = User.objects.all().order_by('-date_joined')
  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/usuarios_list.html',
      {'usuarios': usuarios, 'usuario_nombre': usuario_actual},
  )


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

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/usuario_form.html',
      {
          'form': form,
          'titulo': 'Crear Usuario',
          'usuario_nombre': usuario_actual,
      },
  )


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

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/usuario_form.html',
      {
          'form': form,
          'titulo': 'Editar Usuario',
          'usuario_nombre': usuario_actual,
      },
  )


@login_required
def usuario_toggle_active_view(request, pk):
  usuario = get_object_or_404(User, pk=pk)
  usuario.is_active = not usuario.is_active
  usuario.save()
  return redirect('usuarios_list')


@login_required
def producto_create_view(request):
  error = None
  if request.method == 'POST':
    sku = request.POST.get('sku')
    nombre = request.POST.get('nombre')
    categoria_id = request.POST.get('categoria')
    precio = request.POST.get('precio')
    stock_actual = request.POST.get('stock_actual')
    stock_minimo = request.POST.get('stock_minimo')

    if not sku or not nombre or not precio:
      error = 'Por favor, complete los campos obligatorios (SKU, Nombre, Precio).'
    else:
      try:
        Producto.objects.create(
            sku=sku,
            nombre=nombre,
            categoria_id=categoria_id if categoria_id else None,
            precio=precio,
            stock_actual=stock_actual if stock_actual else 0,
            stock_minimo=stock_minimo if stock_minimo else 0,
        )
        return redirect('inventario')
      except Exception as e:
        error = f'Error al registrar el producto: {e}'

  categorias = Categoria.objects.all()
  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/producto_form.html',
      {
          'error': error,
          'categorias': categorias,
          'usuario_nombre': usuario_actual,
          'titulo': 'Agregar Producto',
      },
  )


@login_required
def producto_edit_view(request, pk):
  producto = get_object_or_404(Producto, pk=pk)
  error = None
  if request.method == 'POST':
    sku = request.POST.get('sku')
    nombre = request.POST.get('nombre')
    categoria_id = request.POST.get('categoria')
    precio = request.POST.get('precio')
    stock_actual = request.POST.get('stock_actual')
    stock_minimo = request.POST.get('stock_minimo')

    if not sku or not nombre or not precio:
      error = 'Por favor, complete los campos obligatorios.'
    else:
      try:
        producto.sku = sku
        producto.nombre = nombre
        producto.categoria_id = categoria_id if categoria_id else None
        producto.precio = precio
        producto.stock_actual = (
            stock_actual if stock_actual else producto.stock_actual
        )
        producto.stock_minimo = (
            stock_minimo if stock_minimo else producto.stock_minimo
        )
        producto.save()
        return redirect('inventario')
      except Exception as e:
        error = f'Error al actualizar: {e}'

  categorias = Categoria.objects.all()
  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/producto_form.html',
      {
          'producto': producto,
          'error': error,
          'categorias': categorias,
          'usuario_nombre': usuario_actual,
          'titulo': 'Editar Producto',
      },
  )


@login_required
def producto_delete_view(request, pk):
  producto = get_object_or_404(Producto, pk=pk)
  if request.method == 'POST':
    producto.delete()
    return redirect('inventario')

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )
  return render(
      request,
      'bodega/producto_confirm_delete.html',
      {'producto': producto, 'usuario_nombre': usuario_actual},
  )


@login_required
def reportes_view(request):
  productos_todos = Producto.objects.all()
  productos_criticos = Producto.objects.filter(
      stock_actual__lte=F('stock_minimo')
  )
  productos_caros = Producto.objects.order_by('-precio')[:10]
  productos_por_categoria = Producto.objects.values('categoria__nombre').annotate(
      total=Count('pk')
  )

  categorias = Categoria.objects.all()
  marcas = Marca.objects.all()
  sucursales = Sucursal.objects.all()
  todas_ordenes = OrdenMovimiento.objects.all().order_by('-fecha_hora')

  categoria_id = request.GET.get('categoria_id')
  productos_por_cat_seleccionada = None
  if categoria_id:
    productos_por_cat_seleccionada = Producto.objects.filter(
        categoria_id=categoria_id
    )

  marca_id = request.GET.get('marca_id')
  productos_por_marca = None
  if marca_id:
    productos_por_marca = Producto.objects.filter(marca_id=marca_id)

  sucursal_id = request.GET.get('sucursal_id')
  ordenes_por_sucursal = None
  if sucursal_id:
    ordenes_por_sucursal = (
        OrdenMovimiento.objects.filter(sucursal_id=sucursal_id)
        .select_related('usuario', 'tipo', 'sucursal')
        .order_by('-fecha_hora')
    )

  orden_id = request.GET.get('orden_id')
  detalles_orden_seleccionada = None
  if orden_id:
    detalles_orden_seleccionada = DetalleOrden.objects.filter(
        orden_id=orden_id
    ).select_related('producto')

  conteo_por_tipo = OrdenMovimiento.objects.values('tipo__nombre').annotate(
      total=Count('pk')
  )

  f_inicio = request.GET.get('f_inicio')
  f_fin = request.GET.get('f_fin')
  ordenes_por_fecha = None
  if f_inicio and f_fin:
    ordenes_por_fecha = (
        OrdenMovimiento.objects.filter(
            fecha_hora__date_range=[f_inicio, f_fin]
        )
        .select_related('sucursal', 'tipo', 'usuario')
        .order_by('-fecha_hora')
    )

  top_sucursales = (
      DetalleOrden.objects.values('orden__sucursal__nombre')
      .annotate(total_unidades=Sum('cantidad'))
      .order_by('-total_unidades')[:5]
  )
  productos_mas_solicitados = (
      DetalleOrden.objects.values('producto__sku', 'producto__nombre')
      .annotate(total_solicitado=Sum('cantidad'))
      .order_by('-total_solicitado')[:10]
  )
  top_marca_proveedor = (
      Producto.objects.values('marca__nombre')
      .annotate(
          total_productos_diferentes=Count('sku', distinct=True)
      )
      .order_by('-total_productos_diferentes')[:5]
  )

  valor_inventario = (
      Producto.objects.annotate(
          subtotal=ExpressionWrapper(
              F('stock_actual') * F('precio'), output_field=DecimalField()
          )
      ).aggregate(total=Sum('subtotal'))['total']
      or 0
  )

  skus_solicitados = DetalleOrden.objects.values_list(
      'producto_id', flat=True
  ).distinct()
  productos_no_solicitados = Producto.objects.exclude(pk__in=skus_solicitados)

  hace_un_mes = timezone.now() - timedelta(days=30)
  salidas_ultimo_mes = (
      DetalleOrden.objects.filter(orden__fecha_hora__gte=hace_un_mes)
      .values('producto__sku', 'producto__nombre')
      .annotate(total_salidas=Sum('cantidad'))
      .order_by('-total_salidas')[:10]
  )

  sucursales_pendientes = (
      OrdenMovimiento.objects.filter(tipo__nombre__icontains='Pendiente')
      .values('sucursal__nombre', 'id', 'fecha_hora')
      .distinct()
  )

  categoria_mayor_valor = (
      Producto.objects.values('categoria__nombre')
      .annotate(
          valor_total_cat=Sum(
              ExpressionWrapper(
                  F('stock_actual') * F('precio'), output_field=DecimalField()
              )
          )
      )
      .order_by('-valor_total_cat')[:5]
  )

  promedio_unidades_por_solicitud = (
      DetalleOrden.objects.aggregate(promedio=Avg('cantidad'))['promedio'] or 0
  )

  f_p20_inicio = request.GET.get('f_p20_inicio')
  f_p20_fin = request.GET.get('f_p20_fin')
  top5_productos_periodo = None
  if f_p20_inicio and f_p20_fin:
    top5_productos_periodo = (
        DetalleOrden.objects.filter(
            orden__fecha_hora__date_range=[f_p20_inicio, f_p20_fin]
        )
        .values('producto__sku', 'producto__nombre')
        .annotate(total_unidades=Sum('cantidad'))
        .order_by('-total_unidades')[:5]
    )

  usuario_actual = (
      getattr(request.user, 'first_name', None) or request.user.username
  )

  context = {
      'productos_todos': productos_todos,
      'productos_criticos': productos_criticos,
      'productos_caros': productos_caros,
      'productos_por_categoria': productos_por_categoria,
      'categorias': categorias,
      'marcas': marcas,
      'sucursales': sucursales,
      'todas_ordenes': todas_ordenes,
      'productos_por_cat_seleccionada': productos_por_cat_seleccionada,
      'productos_por_marca': productos_por_marca,
      'ordenes_por_sucursal': ordenes_por_sucursal,
      'detalles_orden_seleccionada': detalles_orden_seleccionada,
      'conteo_por_tipo': conteo_por_tipo,
      'ordenes_por_fecha': ordenes_por_fecha,
      'top_sucursales': top_sucursales,
      'productos_mas_solicitados': productos_mas_solicitados,
      'top_marca_proveedor': top_marca_proveedor,
      'valor_inventario': valor_inventario,
      'productos_no_solicitados': productos_no_solicitados,
      'salidas_ultimo_mes': salidas_ultimo_mes,
      'sucursales_pendientes': sucursales_pendientes,
      'categoria_mayor_valor': categoria_mayor_valor,
      'promedio_unidades_por_solicitud': promedio_unidades_por_solicitud,
      'top5_productos_periodo': top5_productos_periodo,
      'usuario_nombre': usuario_actual,
  }

  return render(request, 'bodega/reportes.html', context)