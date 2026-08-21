# Hallazgos confirmados sobre ZIP congelado

- Base real: 96 enAudio + 96 esAudio; 215 archivos de audio.
- Hora NO usa playContent: openModule deriva a renderHoraV7 y los botones llaman playHoraV7.
- playHoraV7 al terminar sólo muestra "Elegí otro parlante para escuchar"; nunca solicita reconocimiento.
- El parche rechazado añadió SpeechRecognizer al circuito playContent, pero dejó intacto playHoraV7.
- Por tanto el fallo de activación de las 8 tarjetas de Hora es determinista y reproducible por inspección del flujo real.
- 187.wav existe en la base y debe preservarse; el parche rechazado lo retiró del flujo de repetición general.

Próximo criterio de reparación: unificar el final de audio inglés de Hora con el mismo coordinador de escucha usado por las demás tarjetas, manteniendo audio español sin micrófono y cancelando escucha previa antes de toda reproducción/navegación.
