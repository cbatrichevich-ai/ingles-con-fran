# APTARI — Mensaje → Pedido — Laboratorio V0

Prueba aislada para validar una función candidata del Asistente de Ventas.

## Hipótesis
Convertir un mensaje de WhatsApp, escrito o de audio, en un borrador de pedido revisable puede ahorrar trabajo real.

## Alcance del laboratorio
- Pegar texto manualmente.
- Recibir texto compartido desde Android.
- Elegir un archivo de audio.
- Recibir un audio compartido desde otra app.
- Transcribir audio en el teléfono con Vosk y modelo español liviano.
- Extraer sin inventar: cliente si está mencionado, pedido probable, logística, fecha/hora, importe y observaciones.
- Marcar dudas cuando faltan datos o la extracción no es segura.
- Dejar todo editable antes de copiar el pedido.

## Deliberadamente fuera de alcance
- Leer chats de WhatsApp.
- Automatizar WhatsApp.
- Enviar pedidos automáticamente.
- Integración con APTARI Asistente de Ventas antes de validar utilidad.

## Nota técnica
La compilación de laboratorio descarga `vosk-model-small-es-0.42` durante GitHub Actions y lo incorpora al APK. El modelo es Apache 2.0 y está pensado para dispositivos móviles.

El APK de laboratorio se verifica también con `apksigner` antes de publicarse como artefacto de prueba.
