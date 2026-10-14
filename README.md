# Music Pro - Módulo de Bodega Central y Distribución

Prototipo web desarrollado en Django para la gestión y control de inventarios de Music Pro.

## Integrantes
* Dante

## Características del Sistema
- Autenticación y Seguridad: Sistema de registro e inicio de sesión basado en sesiones de Django para proteger las rutas principales.
- Gestión de Inventario: Control en tiempo real de productos, categorías, marcas, ubicaciones y alertas de stock bajo.
- Trazabilidad: Registro de órdenes y detalles de movimientos de bodega (ingresos y salidas).
- Panel de Administración: CRUD completo integrado con el panel de administración de Django (`/admin`).

## Requisitos e Instalación
1. Activar el entorno virtual: `venv\Scripts\activate`
2. Instalar dependencias: `pip install django`, `pip install django faker`, 
3. Ejecutar el servidor: `python manage.py runserver`

## Aplicar migraciones de la base de datos
python manage.py migrate

## Poblar la base de datos con datos de prueba
python poblar.py

## Flujo de Navegación
[ Dashboard ] -> [ Inventario ] -> [ Movimientos ]

