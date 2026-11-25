# TeleHome Pro

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

La versión avanzada de [TeleHome](../telehome/README.md): la misma app (un solo `index.html`, mismos tipos, gráficas, resumen, CSV y niveles de acceso) más lo que hace falta para manejar bien las **luces**: escenas guardadas, grupos, transiciones graduales, temporizadores y parámetros por bombilla. Es una app aparte; la genérica no cambia.

Necesita el servicio **TeleHome 0.11.0 o posterior** ([documentación](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-servicio#telehome-pro-escenas-grupos-transiciones-y-temporizadores-0110)). Con un servicio anterior, o sin servicio, los controles Pro no aparecen (el panel avisa) o funcionan en el **modo demostración**, que simula todo en el navegador.

## Qué añade

| Función | Qué hace | Quién puede |
|---|---|---|
| **Escenas** | Un toque deja varios dispositivos como indiques (encendido, brillo, blanco o color de cada luz). Se crean desde cero o con **Capturar el estado actual**. Máx. 24 | Aplicar: usuario de confianza; crear y editar: administrador |
| **Grupos** | Interruptor, brillo y blancos rápidos para varias luces a la vez; los miembros que no admiten la orden (un enchufe no tiene brillo) se saltan. Máx. 8 | Igual |
| **Transiciones** | Selector «Transición» en el panel de la luz (inmediata, 2 s … 15 min): brillo, blanco y color van poco a poco al nuevo valor. También en las órdenes de grupo y en las programaciones | Usuario de confianza |
| **Temporizadores** | «Apagar en 15 min / 30 min / 1 h / 2 h» desde el panel de la luz; se ve la hora y se cancela. La franja «En curso» lista los pendientes y las transiciones activas | Usuario de confianza |
| **Parámetros de la bombilla** | Brillo mínimo y máximo (TeleHome recorta antes de mandar), kelvin del blanco más cálido y más frío (solo para mostrar «2 700 K»), códigos, DPS y escalas de Tuya, y **Ver datos de la bombilla** (códigos que devuelve) | Administrador |
| **Modos de Tuya** | Botones «Escena Tuya» y «Música»: pone el modo que la bombilla tenga guardado en la app de Tuya (TeleHome no cambia sus colores) | Usuario de confianza |
| **Programaciones** | Nueva acción «Aplicar una escena», destino «Grupo: …» y campo de transición en segundos | Administrador |

## Cosas que conviene saber

- **Los temporizadores están en la memoria del servicio**: si se reinicia, se pierden. Para algo a una hora fija usa una programación, que sí se guarda.
- **Las transiciones cuestan llamadas a Tuya** por la nube: mínimo 4 s entre pasos y como mucho 20 pasos, es decir, unas 15 llamadas para una transición de un minuto. En red local el paso mínimo es 1,5 s. Una orden manual sobre la luz cancela la transición.
- Con escenas y grupos no hay condiciones en las programaciones.
- Los modos «Escena Tuya» y «Música» no están verificados con bombillas reales, y el modo local de las luces solo se ha probado con bombillas simuladas.
- Máximo 7 dispositivos en el servicio (enchufes y luces juntos).
- Solo hay versión web: las apps de iPhone e iPad (`telehome-iphone`, `telehome-ipad`) siguen con los controles de la versión 0.10.0 (brillo, blancos y color).

## Modo demostración

Sin servicio, la app arranca con ocho dispositivos simulados, dos luces entre ellos, un grupo «Salón» y dos escenas («Cine» y «Lectura»). Escenas, grupos y temporizadores se guardan en el navegador (`localStorage`, claves `telehomepro_demo_v1` y `telehomepro_demo_pro_v1`; «Reiniciar demo» los borra). En la demostración las transiciones son inmediatas.

## Conexión

Igual que la genérica: la página servida por el propio servicio, o una ruta del mismo servidor escrita en el pie (p. ej. `/rafa/telehome/`). La app Pro reconoce las funciones del servicio por el campo `features` de `api/health` (`"escenas"` activa el panel Pro). Para publicarla junto al servicio, copia `index.html` a la carpeta que sirva el servidor.

## API que usa (además de la de TeleHome)

```
POST   api/scenes · PUT|DELETE api/scenes/<id> · POST api/scenes/<id>/apply
POST   api/groups · PUT|DELETE api/groups/<id> · POST api/groups/<id>/command
POST   api/devices/<id>/command        → { action, value, fade? }   (fade: segundos, 0-3600)
POST   api/devices/<id>/timer          → { minutes: 1-1440, action: "off"|"on", fade? } · DELETE lo cancela
GET    api/devices/<id>/raw            → códigos o DPS que devuelve la bombilla (administrador)
PUT    api/devices/<id>                → level_min, level_max, kelvin_min, kelvin_max, code_*, dp_*, scale_*
```

`api/state` añade `features`, `scenes`, `groups`, `timers` y `fades`; cada luz lleva además `level_min`, `level_max`, `kelvin_min` y `kelvin_max`.

## Estructura del fichero

Es el `index.html` de la app genérica con un bloque nuevo, «TeleHome Pro», delante del ciclo de la interfaz (`renderPro`, `enlazarLuzPro`, escenas, grupos, parámetros) y los diálogos `#dlgScene`, `#dlgGroup` y `#dlgParams`. El motor de demostración se amplía con escenas, grupos, temporizadores y parámetros. Cada app es autocontenida: si cambias la genérica, los cambios comunes se llevan a mano a esta.
