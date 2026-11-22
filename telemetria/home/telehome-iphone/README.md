# TeleHome · iPhone

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Versión para **iPhone** de [`telehome`](../telehome/README.md): consulta y manejo de los dispositivos del hogar
(enchufes Wi-Fi con medida de consumo, sensores de temperatura y humedad, luces regulables y persianas) desde el
navegador del dispositivo. Una columna con cuatro pestañas abajo (Dispositivos, Gráfica, Resumen y Ajustes),
interruptores de 44 pt, confirmación antes de apagar, modo oscuro automático y modo Administrador.

Es **una sola página** (`index.html`, sin dependencias ni ficheros externos) que habla con el servicio TeleHome ya
instalado. Solo **consulta y maneja** (ver valores, encender y apagar, regular el brillo, subir y bajar persianas,
gráficas, resumen y CSV). **Dar de alta dispositivos, el modo nube y las contraseñas se siguen haciendo en la
interfaz completa.**

## Modo Administrador

Si el servicio tiene contraseña de administrador (`telehome admin-password`), la app arranca en **solo lectura**:
se ven los dispositivos y sus medidas, pero los controles están desactivados. El escudo de la cabecera pide la
contraseña y abre una sesión que dura mientras la pestaña siga abierta. Sin contraseña de administrador en el
servicio, todo está disponible desde el principio.

## Despliegue en Apache (como el resto de apps)

1. El servicio TeleHome debe estar instalado y publicado en Apache en `/rafa/telehome/` (lo hace `instalar-todo`).
2. `instalar-todo` copia el repo `apps` al webroot, así que esta carpeta queda publicada sin nada más que configurar.
3. Ábrela desde el iPhone y úsala con *Compartir → Añadir a pantalla de inicio*: se abre a pantalla completa, como una app.

Como la página y la API salen del mismo servidor, no hay CORS ni cabeceras que tocar. Si el servicio pide contraseña,
el navegador la pide al conectar; si no puede, la app muestra un aviso con un botón que abre la interfaz completa.

## Cómo encuentra la API

1. La URL guardada en *Ajustes → URL de la API* (opcional).
2. `/rafa/telehome/api/` (la ruta del Apache de isa.umh.es y lorca.umh.es).
3. `api/` relativa a la página, por si el servicio sirve esta carpeta directamente.

## Probar en local

```bash
cd ../../../code/telemetria/home/telehome-enchufes && python3 -m telehome_enchufes serve --simulate 3 --no-browser
cd - && python3 servir.py                   # app en http://127.0.0.1:8080/
python3 servir.py --host 0.0.0.0            # visible desde el iPhone de tu Wi-Fi (solo para probar)
```

`servir.py` solo usa la biblioteca estándar: sirve esta carpeta y reenvía `/rafa/telehome/*` al servicio, igual que Apache.

## Contenido

| Fichero | Para qué |
|---|---|
| `index.html` | La app completa (HTML, CSS y JavaScript en un fichero); el pie muestra la última modificación |
| `apple-touch-icon.png` | Icono de 180×180 para la pantalla de inicio |
| `servir.py` | Servidor de pruebas (ver arriba) |

El núcleo (catálogo de tipos, cliente de la API, modo Administrador y gráfica) es el mismo que el de
[la otra versión](../telehome-ipad/README.md): lo que se corrija aquí conviene corregirlo también allí.

Probada con navegador emulado (iPhone, claro y oscuro) contra un servicio simulado con los cuatro tipos de dispositivo;
no se ha probado con dispositivos reales ni en un iPhone físico.
