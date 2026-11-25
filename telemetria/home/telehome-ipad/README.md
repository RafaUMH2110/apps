# TeleHome · iPad

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Versión para **iPad** de [`telehome`](../telehome/README.md): consulta y manejo de los dispositivos del hogar
(enchufes Wi-Fi con medida de consumo, sensores de temperatura y humedad, luces regulables y persianas) desde el
navegador del dispositivo. Vista dividida: los dispositivos a la izquierda y, a la derecha, la gráfica o el
resumen; modo oscuro automático y modo Administrador.

Es **una sola página** (`index.html`, sin dependencias ni ficheros externos) que habla con el servicio TeleHome ya
instalado. Solo **consulta y maneja** (ver valores, encender y apagar, regular el brillo, subir y bajar persianas,
gráficas, resumen y CSV). **Dar de alta dispositivos, el modo nube y las contraseñas se siguen haciendo en la
interfaz completa.**

## Niveles de acceso

Si el servicio tiene contraseñas puestas, la app arranca en **solo lectura**: se ven los dispositivos y sus medidas,
pero los controles están desactivados. El escudo de la cabecera pide la contraseña y abre una sesión que dura
mientras la pestaña siga abierta; el distintivo de la cabecera dice en qué nivel estás.

| Con qué entras | Ve los datos | Maneja los dispositivos | Configura |
|---|---|---|---|
| Nada | Sí | No | No |
| Contraseña de usuario (`telehome user-password`) | Sí | Sí | No |
| Contraseña de administrador (`telehome admin-password`) | Sí | Sí | Sí |

Configurar se hace siempre en la interfaz completa; esta app nunca cambia ajustes. Si el servicio no tiene ninguna
contraseña puesta, todo está disponible desde el principio.

## Despliegue en Apache (como el resto de apps)

1. El servicio TeleHome debe estar instalado y publicado en Apache en `/rafa/telehome/` (lo hace `instalar-todo`).
2. `instalar-todo` copia el repo `apps` al webroot, así que esta carpeta queda publicada sin nada más que configurar.
3. Ábrela desde el iPad y úsala con *Compartir → Añadir a pantalla de inicio*: se abre a pantalla completa, como una app.

Como la página y la API salen del mismo servidor, no hay CORS ni cabeceras que tocar. Si el servicio pide contraseña
(servicio 0.9.1 o posterior), la app muestra un aviso con el botón «Escribir contraseña» y la pide en su propia hoja,
sin la ventana nativa del navegador. Se guarda en este dispositivo (`localStorage`, clave `telehome.clave`) y se borra
en *Ajustes → Contraseña del servicio → Olvidar*. Si es incorrecta, la app lo dice y la vuelve a pedir. Con servicios
anteriores a 0.9.1 el navegador puede seguir mostrando su propia ventana la primera vez.

## Cómo encuentra la API

1. La URL guardada en *Ajustes → URL de la API* (opcional).
2. `/rafa/telehome/api/` (la ruta del Apache de isa.umh.es y lorca.umh.es).
3. `api/` relativa a la página, por si el servicio sirve esta carpeta directamente.

## Probar en local

```bash
cd ../../../code/telemetria/home/telehome-servicio && python3 -m telehome serve --simulate 3 --no-browser
cd - && python3 servir.py                   # app en http://127.0.0.1:8080/
python3 servir.py --host 0.0.0.0            # visible desde el iPad de tu Wi-Fi (solo para probar)
```

`servir.py` solo usa la biblioteca estándar: sirve esta carpeta y reenvía `/rafa/telehome/*` al servicio, igual que Apache.

## Contenido

| Fichero | Para qué |
|---|---|
| `index.html` | La app completa (HTML, CSS y JavaScript en un fichero); el pie muestra la última modificación |
| `apple-touch-icon.png` | Icono de 180×180 para la pantalla de inicio |
| `servir.py` | Servidor de pruebas (ver arriba) |

**Luces:** cada luz tiene, junto al interruptor y al brillo, un botón de paleta que abre una hoja con interruptor, brillo, blanco cálido↔frío, color y modo (solo lo que admite esa bombilla; hace falta el servicio 0.10.0 o posterior, con uno anterior solo hay brillo).

El núcleo (catálogo de tipos, cliente de la API, modo Administrador y gráfica) es el mismo que el de
[la otra versión](../telehome-iphone/README.md): lo que se corrija aquí conviene corregirlo también allí.

Probada con navegador emulado (iPad, claro y oscuro) contra un servicio simulado con los cuatro tipos de dispositivo;
no se ha probado con dispositivos reales ni en un iPad físico.
