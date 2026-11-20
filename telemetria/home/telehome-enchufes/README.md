# TeleHome Enchufes · Demostración

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Demostración, en un solo fichero (`index.html`), de la app para ver y controlar hasta 7 enchufes Wi-Fi Energeeks (Tuya): potencia, tensión, corriente, energía, histórico (1 h a 30 días), gráficas y exportación a CSV. **Para usar enchufes reales**, abre la interfaz del propio servicio (p. ej. `http://<equipo>:8765/` o `/rafa/telehome/enchufes/` en el servidor) o las versiones para iPhone e iPad del repo `code`; esta página es sobre todo para enseñar la app sin hardware.

Usa la misma interfaz que el servicio **TeleHome Enchufes** del repo [`code`](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-enchufes). Tiene dos modos:

| Modo | Cuándo | Qué hace |
|---|---|---|
| **Servicio** | La página la sirve el propio servicio, o escribes en el pie la ruta del servicio en el mismo servidor (p. ej. `/rafa/telehome/enchufes/`) | Muestra y controla tus enchufes reales |
| **Demostración** | No se encuentra el servicio (p. ej. en GitHub Pages) | Tres enchufes simulados; puedes encenderlos, apagarlos, añadir otros y exportar CSV. Los datos se guardan solo en el navegador (`localStorage`, clave `telehome_demo_v1`; «Reiniciar demo» los borra) |

Notas:
- La conexión solo admite rutas del **mismo servidor** (empiezan por `/`): el servicio rechaza otros orígenes. En el servidor con `instalar-todo`, el servicio queda en `<entrada>telehome/enchufes/`.
- La nube de Tuya y el descubrimiento de la red necesitan el servicio real; en la demostración devuelven un aviso.
- No aparece en la página de entrada del servidor (`instalar-todo`), donde ya está la interfaz real; sí en el catálogo de GitHub Pages.
- Se genera a partir de la interfaz del servicio (misma página más el modo demostración), así que comparten diseño y versión.
- Detalles del servicio, instalación y claves de Tuya: README del servicio en `code`.
