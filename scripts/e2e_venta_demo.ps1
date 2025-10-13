# Requires: running server at 127.0.0.1:8000 and a valid username/password
param(
  [string]$Username,
  [string]$Password,
  [decimal]$OpeningAmount = 10000,
  [int]$ProductoId = 0,
  [int]$LoteId = 0
)

$ErrorActionPreference = 'Stop'
$api = "http://127.0.0.1:8000/api"

Write-Host "1) Obteniendo token..."
$auth = Invoke-RestMethod -Method Post -Uri "$api/token/" -ContentType 'application/json' -Body (@{username=$Username; password=$Password} | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($auth.access)" }

Write-Host "2) Abriendo caja..."
Invoke-RestMethod -Method Post -Uri "$api/caja/abrir/" -Headers $headers -ContentType 'application/json' -Body (@{openingAmount=$OpeningAmount} | ConvertTo-Json) | Out-Null

if ($ProductoId -eq 0) {
  Write-Host "3) Creando producto de prueba..."
  $prod = Invoke-RestMethod -Method Post -Uri "$api/productos/" -Headers $headers -ContentType 'application/json' -Body (@{nombre='Demo Prod'; precio=1500; cantidad=0} | ConvertTo-Json)
  $ProductoId = $prod.id
}

if ($LoteId -eq 0) {
  Write-Host "4) Creando lote de prueba..."
  $lote = Invoke-RestMethod -Method Post -Uri "$api/lotes/" -Headers $headers -ContentType 'application/json' -Body (@{producto=$ProductoId; cantidad_inicial=10; cantidad_disponible=10; costo_unitario=1000} | ConvertTo-Json)
  $LoteId = $lote.id
}

Write-Host "5) Registrando venta..."
$ventaBody = @{ medioPago='EFECTIVO'; idempotencyKey="demo-$(Get-Date -Format 'yyyyMMddHHmmss')"; items=@(@{productoId=$ProductoId; loteId=$LoteId; cantidad=2; precioUnitario=1500}) } | ConvertTo-Json -Depth 5
$ventaResp = Invoke-RestMethod -Method Post -Uri "$api/ventas/" -Headers $headers -ContentType 'application/json' -Body $ventaBody
$ventaResp

Write-Host "6) Consultando sesión de caja..."
Invoke-RestMethod -Method Get -Uri "$api/caja/sesion_abierta/" -Headers $headers

Write-Host "7) Cerrando caja..."
Invoke-RestMethod -Method Post -Uri "$api/caja/cerrar/" -Headers $headers -ContentType 'application/json' -Body (@{countedAmount=$OpeningAmount} | ConvertTo-Json)
