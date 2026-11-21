#!/usr/bin/env bash
# TeleHome en lorca.umh.es: instala o actualiza TODO en un solo paso (sin HTTPS).
#
#   sudo ./instalar-lorca.sh                   instala o actualiza servicio + app + Apache
#   sudo ./instalar-lorca.sh --quitar          retira el servicio y la configuración de Apache (conserva datos y app)
#   ./instalar-lorca.sh --ayuda
#
# Qué hace:
#   1. Descarga el servicio TeleHome Enchufes (repo RafaUMH2110/code) y lo instala como servicio systemd «telehome»
#      (solo escucha en 127.0.0.1:8765).
#   2. Descarga la app TeleHome (repo RafaUMH2110/apps) y la copia al webroot de Apache.
#   3. Configura Apache para que la app y el servicio estén en el MISMO origen (proxy inverso), así no hace falta CORS:
#         http://lorca.umh.es/rafa/telehome/        → la app
#         http://lorca.umh.es/rafa/telehome-api/    → el servicio (proxy a 127.0.0.1:8765)
#   4. Recarga Apache. Al abrir la app, escribe en «Servicio TeleHome» la ruta  /rafa/telehome-api/
#
# Opciones (todas opcionales):
#   --nombre NOMBRE     nombre del servidor            (lorca.umh.es)
#   --webroot DIR       raíz web de Apache             (/var/www/htdocs)
#   --ruta RUTA         carpeta de la app en la web    (rafa/telehome)
#   --api RUTA          ruta web del servicio          (rafa/telehome-api)
#   --puerto N          puerto local del servicio      (8765)
#   --alias NOMBRE      otro nombre o IP con el que se accede al servidor (repetible)
#   --permitir CIDR     limita el acceso a esa red, p. ej. 158.42.0.0/16 (repetible; sin esto, acceso abierto)
#   --sin-apache        no toca Apache (solo servicio y copia de la app)
#   --sin-password      no pregunta por la contraseña del servicio
#   --rama RAMA         rama de los repositorios       (main)
#   --quitar            desinstala (servicio y configuración de Apache)
#
# AVISO: sin HTTPS, la contraseña y los datos viajan SIN CIFRAR. Pon contraseña y, si puedes, usa --permitir para
# limitar el acceso a la red de la universidad, o accede mediante túnel SSH.
set -euo pipefail

NOMBRE="lorca.umh.es"
WEBROOT="/var/www/htdocs"
RUTA="rafa/telehome"
API="rafa/telehome-api"
PUERTO=8765
RAMA="main"
ALIAS=()
PERMITIR=()
APACHE=1
PEDIR_PASSWORD=1
ACCION="instalar"

REPO_CODIGO="https://github.com/RafaUMH2110/code.git"
REPO_APPS="https://github.com/RafaUMH2110/apps.git"
FUENTES="/opt/telehome-fuentes"          # clones de trabajo (solo lectura)

while [ $# -gt 0 ]; do
  case "$1" in
    --nombre) shift; NOMBRE="${1:?Falta el nombre}" ;;
    --webroot) shift; WEBROOT="${1:?Falta el directorio}" ;;
    --ruta) shift; RUTA="${1:?Falta la ruta}" ;;
    --api) shift; API="${1:?Falta la ruta}" ;;
    --puerto) shift; PUERTO="${1:?Falta el puerto}" ;;
    --alias) shift; ALIAS+=("${1:?Falta el nombre}") ;;
    --permitir) shift; PERMITIR+=("${1:?Falta la red}") ;;
    --sin-apache) APACHE=0 ;;
    --sin-password) PEDIR_PASSWORD=0 ;;
    --rama) shift; RAMA="${1:?Falta la rama}" ;;
    --quitar) ACCION="quitar" ;;
    -h|--help|--ayuda) sed -n '2,36p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $1" >&2; exit 2 ;;
  esac
  shift
done

RUTA="${RUTA#/}"; RUTA="${RUTA%/}"; API="${API#/}"; API="${API%/}"
msg()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
aviso(){ printf '\033[33m! %s\033[0m\n' "$*" >&2; }
fallo(){ printf '\033[31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

# ---- validaciones ----------------------------------------------------------------
case "$PUERTO" in ''|*[!0-9]*) fallo "El puerto debe ser un número" ;; esac
for n in "$NOMBRE" ${ALIAS[@]+"${ALIAS[@]}"}; do
  case "$n" in ''|*[!0-9A-Za-z.:-]*) fallo "Nombre no válido: $n" ;; esac
done
for c in ${PERMITIR[@]+"${PERMITIR[@]}"}; do
  case "$c" in ''|*[!0-9A-Fa-f.:/]*) fallo "Red no válida (usa CIDR, p. ej. 158.42.0.0/16): $c" ;; esac
done
case "$RUTA$API$WEBROOT" in *[!0-9A-Za-z._/-]*) fallo "Rutas con caracteres no admitidos" ;; esac
[ "$RUTA" != "$API" ] || fallo "--ruta y --api no pueden ser iguales"

[ "$(id -u)" -eq 0 ] || fallo "Ejecútalo con sudo."

# ---- Apache: Debian/Ubuntu (apache2) o RHEL/Fedora (httpd) --------------------------
if [ -d /etc/apache2 ]; then
  AP_TIPO="debian"; AP_SERVICIO="apache2"; AP_CONF="/etc/apache2/conf-available/telehome.conf"
elif [ -d /etc/httpd ]; then
  AP_TIPO="rhel"; AP_SERVICIO="httpd"; AP_CONF="/etc/httpd/conf.d/telehome.conf"
else
  AP_TIPO=""; AP_SERVICIO=""; AP_CONF=""
fi

# ---- desinstalar ---------------------------------------------------------------------
if [ "$ACCION" = "quitar" ]; then
  msg "Retirando TeleHome"
  if [ -n "$AP_TIPO" ] && [ -f "$AP_CONF" ]; then
    [ "$AP_TIPO" = "debian" ] && a2disconf telehome >/dev/null 2>&1 || true
    rm -f "$AP_CONF"
    [ "$AP_TIPO" = "debian" ] && rm -f /etc/apache2/conf-enabled/telehome.conf
    apachectl configtest >/dev/null 2>&1 && systemctl reload "$AP_SERVICIO" || aviso "Revisa Apache a mano."
    echo "Configuración de Apache retirada."
  fi
  if [ -x "$FUENTES/code/telemetria/home/telehome-enchufes/linux/instalar-linux.sh" ]; then
    "$FUENTES/code/telemetria/home/telehome-enchufes/linux/instalar-linux.sh" --quitar || true
  elif systemctl list-unit-files telehome.service >/dev/null 2>&1; then
    systemctl disable --now telehome 2>/dev/null || true
    rm -f /etc/systemd/system/telehome.service /usr/local/bin/telehome
    systemctl daemon-reload
  fi
  echo "Se conservan los datos (/var/lib/telehome) y la app copiada en $WEBROOT/$RUTA."
  exit 0
fi

# ---- dependencias ------------------------------------------------------------------
msg "Comprobando requisitos"
instalar_paquete() {
  if command -v apt-get >/dev/null 2>&1; then apt-get install -y "$@"
  elif command -v dnf >/dev/null 2>&1; then dnf install -y "$@"
  elif command -v yum >/dev/null 2>&1; then yum install -y "$@"
  else return 1; fi
}
command -v git >/dev/null 2>&1 || { echo "Instalando git…"; instalar_paquete git || fallo "Instala git."; }
command -v python3 >/dev/null 2>&1 || { echo "Instalando python3…"; instalar_paquete python3 || fallo "Instala Python 3.9 o superior."; }
python3 - <<'PY' || fallo "Se necesita Python 3.9 o superior."
import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)
PY
if ! python3 -c 'import ensurepip, venv' >/dev/null 2>&1; then
  echo "Instalando soporte de entornos virtuales (python3-venv)…"
  instalar_paquete python3-venv || fallo "Instala python3-venv."
fi
if [ "$APACHE" -eq 1 ]; then
  [ -n "$AP_TIPO" ] || fallo "No encuentro Apache (/etc/apache2 ni /etc/httpd). Instálalo o usa --sin-apache."
  command -v apachectl >/dev/null 2>&1 || command -v apache2ctl >/dev/null 2>&1 || fallo "No encuentro apachectl."
fi
[ -d "$WEBROOT" ] || fallo "No existe el webroot $WEBROOT (usa --webroot)."
echo "Todo en orden."

# ---- 1. descargar el código (clon ligero, solo las carpetas necesarias) ------------------
clonar() {   # clonar URL DESTINO CARPETA
  local url="$1" dest="$2" carpeta="$3"
  if [ -d "$dest/.git" ]; then
    git -C "$dest" fetch -q --depth 1 origin "$RAMA"
    git -C "$dest" reset -q --hard "origin/$RAMA"
  else
    rm -rf "$dest"; mkdir -p "$(dirname "$dest")"
    git clone -q --depth 1 --branch "$RAMA" --filter=blob:none --sparse "$url" "$dest"
    git -C "$dest" sparse-checkout set "$carpeta"
  fi
}
msg "Descargando el servicio TeleHome Enchufes"
clonar "$REPO_CODIGO" "$FUENTES/code" "telemetria/home/telehome-enchufes"
SRV="$FUENTES/code/telemetria/home/telehome-enchufes"
[ -x "$SRV/linux/instalar-linux.sh" ] || chmod +x "$SRV/linux/instalar-linux.sh"
grep -q -- "--allow-origin" "$SRV/linux/instalar-linux.sh" || fallo "El repositorio no tiene la versión 0.5.x del servicio (falta --allow-origin)."
VERSION="$(sed -n 's/^__version__ *= *"\(.*\)"/\1/p' "$SRV/telehome_enchufes/__init__.py" | head -1)"
echo "Versión del servicio: ${VERSION:-desconocida}"

msg "Descargando la app TeleHome"
clonar "$REPO_APPS" "$FUENTES/apps" "telemetria/home/telehome"
APP="$FUENTES/apps/telemetria/home/telehome/index.html"
[ -f "$APP" ] || fallo "No encuentro telemetria/home/telehome/index.html en el repositorio apps."

# ---- 2. instalar el servicio (systemd «telehome», solo en 127.0.0.1) ------------------------
msg "Instalando el servicio TeleHome (systemd)"
ARGS=(--puerto "$PUERTO" --allow-host "$NOMBRE")
for a in ${ALIAS[@]+"${ALIAS[@]}"}; do ARGS+=(--allow-host "$a"); done
"$SRV/linux/instalar-linux.sh" "${ARGS[@]}"
sleep 2
if curl -fsS "http://127.0.0.1:$PUERTO/api/health" >/dev/null 2>&1; then
  echo "El servicio responde en 127.0.0.1:$PUERTO."
else
  aviso "El servicio no responde todavía: revisa  journalctl -u telehome -n 30"
fi

# ---- 3. copiar la app al webroot ---------------------------------------------------------
msg "Copiando la app a $WEBROOT/$RUTA"
mkdir -p "$WEBROOT/$RUTA"
install -m 644 "$APP" "$WEBROOT/$RUTA/index.html"
# mismo propietario que el resto del webroot
dueno="$(stat -c '%U:%G' "$WEBROOT")" && chown -R "$dueno" "$WEBROOT/$RUTA" 2>/dev/null || true

# ---- 4. Apache: proxy inverso en el mismo origen ----------------------------------------------
if [ "$APACHE" -eq 1 ]; then
  msg "Configurando Apache ($AP_TIPO)"
  if [ "$AP_TIPO" = "debian" ]; then
    a2enmod proxy proxy_http headers >/dev/null
  elif command -v getenforce >/dev/null 2>&1 && [ "$(getenforce)" = "Enforcing" ]; then
    setsebool -P httpd_can_network_connect 1 || aviso "No pude ajustar SELinux (httpd_can_network_connect)."
  fi
  REQUIERE="Require all granted"
  if [ ${#PERMITIR[@]} -gt 0 ]; then
    REQUIERE="Require ip 127.0.0.1 ::1"
    for c in "${PERMITIR[@]}"; do REQUIERE="$REQUIERE $c"; done
  fi
  cat > "$AP_CONF" <<CONF
# TeleHome (generado por instalar-lorca.sh): el servicio local en la misma web que la app
ProxyPreserveHost Off
ProxyPass        /$API/ http://127.0.0.1:$PUERTO/ retry=0 timeout=60
ProxyPassReverse /$API/ http://127.0.0.1:$PUERTO/

<Location "/$API/">
    $REQUIERE
</Location>
<Directory "$WEBROOT/$RUTA">
    $REQUIERE
</Directory>
CONF
  [ "$AP_TIPO" = "debian" ] && a2enconf telehome >/dev/null
  CTL="apachectl"; command -v apachectl >/dev/null 2>&1 || CTL="apache2ctl"
  if $CTL configtest >/dev/null 2>&1; then
    systemctl reload "$AP_SERVICIO"
    echo "Apache recargado."
  else
    $CTL configtest || true
    fallo "La configuración de Apache no es válida (se ha dejado $AP_CONF para que la revises)."
  fi
else
  aviso "Con --sin-apache debes configurar tú el proxy:  ProxyPass /$API/ http://127.0.0.1:$PUERTO/"
fi

# ---- 5. contraseña ----------------------------------------------------------------------------------------
if [ "$PEDIR_PASSWORD" -eq 1 ] && [ -t 0 ]; then
  msg "Contraseña del servicio"
  echo "Sin HTTPS la contraseña viaja sin cifrar; aun así es mejor que dejar el acceso abierto."
  read -r -p "¿Poner o cambiar la contraseña ahora? [S/n] " r
  case "${r:-S}" in [sS]*|[yY]*|"") telehome password || aviso "No se pudo cambiar la contraseña." ;; esac
fi

# ---- resumen ----------------------------------------------------------------------------------------------------
msg "Listo"
cat <<FIN
App:        http://$NOMBRE/$RUTA/
Servicio:   http://$NOMBRE/$API/        (proxy a 127.0.0.1:$PUERTO; no se expone el puerto)
Versión:    ${VERSION:-?}

En la app, pie de página → «Servicio TeleHome»: escribe   /$API/   y pulsa Conectar.

Siguientes pasos (modo nube de Tuya):
  sudo telehome cloud-setup --region eu --access-id TU_ACCESS_ID    # pide el Access Secret
  sudo telehome cloud-import                                       # añade tus enchufes (máx. 7)
  sudo telehome password                                           # si no la pusiste ahora

Actualizar a la última versión:  sudo ./instalar-lorca.sh   (repite las mismas opciones)
Registro del servicio:           journalctl -u telehome -f
Retirar:                         sudo ./instalar-lorca.sh --quitar

AVISO: este servidor no usa HTTPS: la contraseña y los datos viajan sin cifrar.
FIN
