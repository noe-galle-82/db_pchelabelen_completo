# 📦 CRUD de Productos - API Documentation

¡El CRUD de productos está listo! Aquí tienes todos los endpoints disponibles:

## 🔗 Base URL
```
http://127.0.0.1:8000/api/productos/
```

## 🔐 Autenticación
Todos los endpoints requieren autenticación JWT. Incluye en los headers:
```
Authorization: Bearer tu_token_jwt
```

## 📋 Endpoints Disponibles

### 1. **Listar todos los productos**
```http
GET /api/productos/
```

**Respuesta:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "nombre": "Laptop Dell",
      "precio": "1200.00",
      "cantidad": 15,
      "categoria": "Electrónicos",
      "imagen": null,
      "creado": "2025-10-03T16:20:00Z"
    }
  ]
}
```

### 2. **Crear un nuevo producto**
```http
POST /api/productos/
Content-Type: application/json

{
  "nombre": "Mouse Inalámbrico",
  "precio": 25.99,
  "cantidad": 50,
  "categoria": "Accesorios"
}
```

**Respuesta:**
```json
{
  "message": "Producto creado exitosamente",
  "data": {
    "id": 2,
    "nombre": "Mouse Inalámbrico",
    "precio": "25.99",
    "cantidad": 50,
    "categoria": "Accesorios",
    "imagen": null,
    "creado": "2025-10-03T16:25:00Z"
  }
}
```

### 3. **Obtener un producto específico**
```http
GET /api/productos/1/
```

### 4. **Actualizar un producto**
```http
PUT /api/productos/1/
Content-Type: application/json

{
  "nombre": "Laptop Dell Inspiron",
  "precio": 1100.00,
  "cantidad": 12,
  "categoria": "Electrónicos"
}
```

### 5. **Actualizar parcialmente un producto**
```http
PATCH /api/productos/1/
Content-Type: application/json

{
  "precio": 1050.00
}
```

### 6. **Eliminar un producto**
```http
DELETE /api/productos/1/
```

**Respuesta:**
```json
{
  "message": "Producto \"Laptop Dell\" eliminado exitosamente"
}
```

## 🎯 Endpoints Especiales

### 7. **Obtener todas las categorías**
```http
GET /api/productos/categorias/
```

**Respuesta:**
```json
{
  "categorias": ["Electrónicos", "Accesorios", "Ropa", "Hogar"]
}
```

### 8. **Productos con poco stock**
```http
GET /api/productos/productos_bajo_stock/
GET /api/productos/productos_bajo_stock/?umbral=5
```

**Respuesta:**
```json
{
  "message": "Productos con menos de 10 unidades",
  "data": [
    {
      "id": 3,
      "nombre": "Teclado Mecánico",
      "precio": "89.99",
      "cantidad": 3,
      "categoria": "Accesorios",
      "imagen": null,
      "creado": "2025-10-03T15:30:00Z"
    }
  ]
}
```

### 9. **Actualizar solo el stock**
```http
PATCH /api/productos/1/actualizar_stock/
Content-Type: application/json

{
  "cantidad": 25
}
```

**Respuesta:**
```json
{
  "message": "Stock actualizado a 25 unidades",
  "data": {
    "id": 1,
    "nombre": "Laptop Dell",
    "precio": "1200.00",
    "cantidad": 25,
    "categoria": "Electrónicos",
    "imagen": null,
    "creado": "2025-10-03T16:20:00Z"
  }
}
```

## 🔍 Filtros y Búsqueda

### Filtrar por categoría:
```http
GET /api/productos/?categoria=Electrónicos
```

### Buscar por nombre:
```http
GET /api/productos/?search=laptop
```

### Ordenar resultados:
```http
GET /api/productos/?ordering=precio          # Menor a mayor
GET /api/productos/?ordering=-precio         # Mayor a menor
GET /api/productos/?ordering=nombre          # A-Z
GET /api/productos/?ordering=-creado         # Más recientes primero
```

### Combinar filtros:
```http
GET /api/productos/?categoria=Electrónicos&search=dell&ordering=-precio
```

## 🛠️ Validaciones

- **Precio**: Debe ser mayor a 0
- **Cantidad**: No puede ser negativa
- **Nombre**: Requerido, máximo 120 caracteres
- **Categoría**: Máximo 80 caracteres

## 📱 Ejemplos con JavaScript (Frontend)

### Crear producto:
```javascript
const crearProducto = async (producto) => {
  const response = await fetch('http://127.0.0.1:8000/api/productos/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(producto)
  });
  return await response.json();
};
```

### Obtener productos:
```javascript
const obtenerProductos = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/productos/', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  return await response.json();
};
```

## 🎉 ¡Tu CRUD está listo!

Puedes empezar a usar estos endpoints inmediatamente. El servidor está corriendo en:
**http://127.0.0.1:8000/**

Panel de administración (para ver datos):
**http://127.0.0.1:8000/admin/**