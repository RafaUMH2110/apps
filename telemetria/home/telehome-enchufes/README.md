# TeleHome Enchufes Web

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Panel web de un solo fichero (`index.html`) para ver y controlar hasta 7 enchufes Wi-Fi Energeeks (Tuya): potencia, tensión, corriente, energía, histórico (1 h a 30 días), gráficas y exportación a CSV.

Es la interfaz del servicio **TeleHome Enchufes** del repo [`code`](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-enchufes). Tiene dos modos:

| Modo | Cuándo | Qué hace |
|---|---|---|
| **Servicio** | La página la sirve el propio servicio, o escribes en el pie la ruta del servicio en el mismo servidor (p. ej. `/rafa/telehome/enchufes/`) | Muestra y controla tus enchufes reales |
| **Demostración** | No se encuentra el servicio (p. ej. en GitHub Pages) | Tres enchufes simulados; puedes encenderlos, apagarlos, añadir otros y exportar CSV. Los datos se guardan solo en el navegador (`localStorage`, clave `telehome_demo_v1`; «Reiniciar demo» los borra) |

Notas:
- La conexión solo admite rutas del **mismo servidor** (empiezan por `/`): el servicio rechaza otros orígenes. En el servidor con `instalar-todo`, el servicio queda en `<entrada>telehome/enchufes/`.
- La nube de Tuya y el descubrimiento de la red necesitan el servicio real; en la demostración devuelven un aviso.
- Detalles del servicio, instalación y claves de Tuya: README del servicio en `code`.
