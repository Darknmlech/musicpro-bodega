from django.shortcuts import render

PRODUCTOS_MOCK = [
    {'codigo': 'GUT-001', 'nombre': 'Guitarra Eléctrica Fender', 'categoria': 'Cuerdas', 'stock': 15, 'ubicación': 'Rack A-12', 'estado': 'Disponible'},
    {'codigo': 'AMP-002', 'nombre': 'Amplificador Marshall 50W', 'categoria': 'Audio', 'stock': 3, 'ubicación': 'Rack B-04', 'estado': 'Stock Crítico'},
    {'codigo': 'BAT-003', 'nombre': 'Batería Acústica Pearl', 'categoria': 'Percusión', 'stock': 0, 'ubicación': 'Rack C-01', 'estado': 'Agotado'},
]

MOVIMIENTOS_MOCK = [
    {'fecha': '2026-09-01', 'tipo': 'Ingreso', 'producto': 'Guitarra Eléctrica Fender', 'cantidad': 5, 'usuario': 'admin_bodega'},
    {'fecha': '2026-09-03', 'tipo': 'Salida', 'producto': 'Amplificador Marshall 50W', 'cantidad': 2, 'usuario': 'juan_despacho'},
]

def dashboard(request):
    context = {
        'total_productos': len(PRODUCTOS_MOCK),
        'total_movimientos': len(MOVIMIENTOS_MOCK),
    }
    return render(request, 'bodega/dashboard.html', context)

def inventario(request):
    return render(request, 'bodega/inventario.html', {'productos': PRODUCTOS_MOCK})

def movimientos(request):
    return render(request, 'bodega/movimientos.html', {'movimientos': MOVIMIENTOS_MOCK})