# TeleHome Pro

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

La versión avanzada de [TeleHome](../telehome/README.md): la misma app (un solo `index.html`, mismos tipos, gráficas, resumen, CSV y niveles de acceso) más lo que hace falta para manejar bien las **luces**: escenas guardadas, grupos, transiciones graduales, temporizadores y parámetros por bombilla. Es una app aparte; la genérica no cambia.

Necesita el servicio **TeleHome 0.11.0 o posterior** (con la **0.12.0** se añaden deshacer, acciones rápidas, temporizadores para enchufes y escenas con transición; con la **0.13.0**, la gestión de estancias) ([documentación](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-servicio#telehome-pro-escenas-grupos-transiciones-y-temporizadores-0110)). Con un servicio anterior, o sin servicio, los controles Pro no aparecen (el panel avisa) o funcionan en el **modo demostración**, que simula todo en el navegador.

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
| **Deshacer** | Tras aplicar una escena, mandar a un grupo o apagar en bloque, el aviso ofrece **Deshacer**: devuelve cada dispositivo al estado que tenía justo antes (servicio 0.12.0) | Usuario de confianza |
| **Acciones rápidas** | «Apagar las luces» y «Apagar todo» en la cabecera del panel, también con deshacer (servicio 0.12.0) | Usuario de confianza |
| **Escena puesta** | La escena que coincide con el estado actual aparece marcada, para saber de un vistazo cuál está aplicada | — |
| **Estancias** | Pestaña *Ajustes → Estancias*: definir, renombrar, borrar y ordenar las estancias. Renombrar la cambia en todos sus dispositivos; borrarla los deja sin estancia, sin borrar ninguno. Al añadir o editar un dispositivo, la estancia se elige en un desplegable con las que ya hay, o se crea una nueva ahí mismo (servicio 0.13.0) | Administrador |
| **Temporizador de cualquier cosa** | «+ Temporizador» (u «Otro…» en el panel de la luz) abre un diálogo para elegir dispositivo —**también enchufes**—, tiempo, apagar o encender y transición (servicio 0.12.0) | Usuario de confianza |

## Cosas que conviene saber

- **Los temporizadores se guardan en el servicio** (0.12.0): un reinicio no los pierde. Si uno vence mientras el servicio está parado, al arrancar se cumple si fue hace menos de 15 minutos y se descarta si fue hace más. Con un servicio 0.11.0 siguen estando solo en memoria. Para algo a una hora fija, una programación.
- **Las transiciones cuestan llamadas a Tuya** por la nube: mínimo 4 s entre pasos y como mucho 20 pasos, es decir, unas 15 llamadas para una transición de un minuto. En red local el paso mínimo es 1,5 s. La app dice cuántos pasos costará al elegir la duración. Una orden manual sobre la luz cancela la transición.
- **El orden de las estancias manda** en la agrupación «Por estancia» de la lista de dispositivos; los que no tengan estancia van al final.
- **«Deshacer» no es un viaje en el tiempo**: guarda el estado que tenían los dispositivos *en la app* justo antes de la orden y lo vuelve a aplicar. Si algo estaba sin conexión, ese dispositivo se queda fuera.
- Con escenas y grupos no hay condiciones en las programaciones.
- Los modos «Escena Tuya» y «Música» no están verificados con bombillas reales, y el modo local de las luces solo se ha probado con bombillas simuladas.
- Máximo 7 dispositivos en el servicio (enchufes y luces juntos).
- Solo hay versión web: las apps de iPhone e iPad (`telehome-iphone`, `telehome-ipad`) siguen con los controles de la versión 0.10.0 (brillo, blancos y color).

## Modo demostración

Sin servicio, la app arranca con ocho dispositivos simulados, dos luces entre ellos, un grupo «Salón» y dos escenas («Cine» y «Lectura»). Escenas, grupos y temporizadores se guardan en el navegador (`localStorage`, claves `telehomepro_demo_v1` y `telehomepro_demo_pro_v1`; «Reiniciar demo» los borra). La demostración simula también el servicio 0.12.0 (escena puntual, deshacer, acciones rápidas y temporizadores de enchufe); las transiciones, eso sí, son inmediatas.

## Conexión

Igual que la genérica: la página servida por el propio servicio, o una ruta del mismo servidor escrita en el pie (p. ej. `/rafa/telehome/`). La app Pro reconoce las funciones del servicio por el campo `features` de `api/health` (`"escenas"` activa el panel Pro). Para publicarla junto al servicio, copia `index.html` a la carpeta que sirva el servidor.

## API que usa (además de la de TeleHome)

```
POST   api/scenes · PUT|DELETE api/scenes/<id> · POST api/scenes/<id>/apply   → { fade? }
POST   api/scenes/apply                → { items, fade? }  escena puntual: no se guarda (deshacer, apagar todo)
POST   api/rooms · PUT|DELETE api/rooms/<id> · PUT api/rooms { ids }   estancias: crear, renombrar, borrar, ordenar
POST   api/groups · PUT|DELETE api/groups/<id> · POST api/groups/<id>/command
POST   api/devices/<id>/command        → { action, value, fade? }   (fade: segundos, 0-3600)
POST   api/devices/<id>/timer          → { minutes: 1-1440, action: "off"|"on", fade? } · DELETE lo cancela
GET    api/devices/<id>/raw            → códigos o DPS que devuelve la bombilla (administrador)
PUT    api/devices/<id>                → level_min, level_max, kelvin_min, kelvin_max, code_*, dp_*, scale_*
```

`api/state` añade `features`, `limits`, `rooms`, `scenes`, `groups`, `timers` y `fades`; cada luz lleva además `level_min`, `level_max`, `kelvin_min` y `kelvin_max`. De `limits` salen los topes y el coste estimado de una transición, en vez de llevarlos escritos en la app.

## Estructura del fichero

Es el `index.html` de la app genérica con un bloque nuevo, «TeleHome Pro», delante del ciclo de la interfaz (`renderPro`, `enlazarLuzPro`, escenas, grupos, parámetros) los diálogos `#dlgScene`, `#dlgGroup`, `#dlgTimer` y `#dlgParams`, y la pestaña «Estancias» (`renderRooms`). El panel se redibuja solo cuando cambia algo (`firmaPro`) y nunca mientras se está tocando un control: con un refresco cada 3 s, redibujar a ciegas cortaba el arrastre del deslizador de brillo del grupo. El motor de demostración se amplía con escenas, grupos, temporizadores y parámetros. Cada app es autocontenida: si cambias la genérica, los cambios comunes se llevan a mano a esta.
