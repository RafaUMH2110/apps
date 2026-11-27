# appindex
Índice de artifacts de Rafa, servido junto con el resto de apps en el repo `apps`.

Las dos páginas (`index.html` y `temas/index.html`) las genera `.github/scripts/generate_index.py` a partir de las apps del repo. Los enlaces a las apps son **relativos** (`../moda/genimod/`), no URLs de GitHub Pages: así el catálogo abre siempre la copia que tiene al lado, tanto en https://rafaumh2110.github.io/apps/ como en un servidor propio donde se despliegue el repo (p. ej. http://lorca.umh.es/rafa/apps/). Solo son absolutos los enlaces externos declarados en `.github/scripts/enlaces_externos.json`.
