#!/usr/bin/env bash

# Jednokratna instalacija GHCR slike i sigurnog updatera na ZimaOS/CasaOS.

set -Eeuo pipefail

REPOSITORY="dejanrepic-lab/grampsweb-bcs"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPOSITORY}/${BRANCH}"
INSTALL_DIR="/usr/local/lib/grampsweb-bcs"
SYSTEMD_DIR="/etc/systemd/system"
CONFIG_FILE="/etc/default/grampsweb-bcs"
REMOTE_IMAGE="ghcr.io/dejanrepic-lab/grampsweb-bcs:latest"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
    log "GREŠKA: $*"
    exit 1
}

[[ "${EUID}" -eq 0 ]] || die "Pokreni instalaciju sa sudo."
command -v curl >/dev/null 2>&1 || die "Naredba curl nije pronađena."
command -v docker >/dev/null 2>&1 || die "Docker nije pronađen."

temporary_dir="$(mktemp -d /tmp/grampsweb-bcs-install.XXXXXX)"
trap 'rm -rf -- "${temporary_dir}"' EXIT

install_project_file() {
    local source_name="$1"
    local destination="$2"
    local mode="$3"
    local source_path="${SCRIPT_DIR}/${source_name}"

    if [[ -f "${source_path}" ]]; then
        install -D -m "${mode}" "${source_path}" "${destination}"
    else
        source_path="${temporary_dir}/${source_name}"
        curl --fail --location --silent --show-error \
            "${RAW_BASE}/${source_name}" \
            --output "${source_path}"
        install -D -m "${mode}" "${source_path}" "${destination}"
    fi
}

find_compose_file() {
    local candidate

    if [[ -n "${GRAMPSWEB_COMPOSE_DIR:-}" ]]; then
        for candidate in compose.yaml docker-compose.yml docker-compose.yaml; do
            [[ -f "${GRAMPSWEB_COMPOSE_DIR}/${candidate}" ]] && {
                printf '%s\n' "${GRAMPSWEB_COMPOSE_DIR}/${candidate}"
                return 0
            }
        done
        return 1
    fi

    for candidate in \
        /var/lib/casaos/apps/heartwarming_matthias/compose.yaml \
        /var/lib/casaos/apps/heartwarming_matthias/docker-compose.yml \
        /var/lib/casaos/apps/heartwarming_matthias/docker-compose.yaml
    do
        [[ -f "${candidate}" ]] && {
            printf '%s\n' "${candidate}"
            return 0
        }
    done

    while IFS= read -r -d '' candidate; do
        if grep -Eq 'container_name:[[:space:]]*grampsweb([[:space:]]|$)' "${candidate}"; then
            printf '%s\n' "${candidate}"
            return 0
        fi
    done < <(find /var/lib/casaos/apps -maxdepth 3 -type f \
        \( -name compose.yaml -o -name docker-compose.yml -o -name docker-compose.yaml \) \
        -print0 2>/dev/null)

    return 1
}

compose_file="$(find_compose_file)" || die "Nisam pronašao Gramps Web compose.yaml."
compose_dir="$(dirname "${compose_file}")"
[[ "${compose_dir}" =~ ^/[A-Za-z0-9._/-]+$ ]] || die "Compose putanja sadrži neočekivane znakove: ${compose_dir}"

log "Pronađen Gramps Web stack: ${compose_dir}"

systemctl disable --now grampsweb-bcs-update.timer >/dev/null 2>&1 || true

install_project_file update-grampsweb-bcs.sh "${INSTALL_DIR}/update-grampsweb-bcs.sh" 0755
install_project_file grampsweb-bcs-update.service "${SYSTEMD_DIR}/grampsweb-bcs-update.service" 0644
install_project_file grampsweb-bcs-update.timer "${SYSTEMD_DIR}/grampsweb-bcs-update.timer" 0644
printf 'GRAMPSWEB_COMPOSE_DIR=%s\n' "${compose_dir}" > "${CONFIG_FILE}"
chmod 0644 "${CONFIG_FILE}"

systemctl daemon-reload

log "Provjeravam javnu Docker sliku prije izmjene stacka."
GRAMPSWEB_COMPOSE_DIR="${compose_dir}" "${INSTALL_DIR}/update-grampsweb-bcs.sh" --check-only

local_count="$(grep -Ec '^[[:space:]]*image:[[:space:]]*grampsweb-bcs:local[[:space:]]*$' "${compose_file}" || true)"
remote_count="$(grep -Ec "^[[:space:]]*image:[[:space:]]*${REMOTE_IMAGE//\//\\/}[[:space:]]*$" "${compose_file}" || true)"
official_count="$(grep -Ec '^[[:space:]]*image:[[:space:]]*ghcr.io/gramps-project/grampsweb:latest[[:space:]]*$' "${compose_file}" || true)"

if (( local_count + remote_count + official_count < 2 )); then
    die "Nisam pronašao očekivane image linije za servise grampsweb i grampsweb_celery; compose nije mijenjan."
fi

compose_backup="${compose_file}.pre-grampsweb-bcs-$(date '+%Y%m%d-%H%M%S').bak"
install -m 0600 "${compose_file}" "${compose_backup}"
log "Sigurnosna kopija compose fajla: ${compose_backup}"

sed -E -i \
    -e "s#^([[:space:]]*image:[[:space:]]*)grampsweb-bcs:local[[:space:]]*\$#\\1${REMOTE_IMAGE}#" \
    -e "s#^([[:space:]]*image:[[:space:]]*)ghcr.io/gramps-project/grampsweb:latest[[:space:]]*\$#\\1${REMOTE_IMAGE}#" \
    "${compose_file}"

updated_count="$(grep -Ec "^[[:space:]]*image:[[:space:]]*${REMOTE_IMAGE//\//\\/}[[:space:]]*$" "${compose_file}" || true)"
if (( updated_count < 2 )); then
    install -m 0600 "${compose_backup}" "${compose_file}"
    die "Compose izmjena nije prošla provjeru; vraćena je sigurnosna kopija."
fi

log "Prebacujem kontejnere na gotovu GitHub sliku."
if ! GRAMPSWEB_COMPOSE_DIR="${compose_dir}" "${INSTALL_DIR}/update-grampsweb-bcs.sh" --force; then
    log "Updater je prijavio grešku. Compose kopija je sačuvana na ${compose_backup}."
    exit 1
fi

systemctl enable --now grampsweb-bcs-update.timer

echo
echo "Instalacija je završena. ZIP-ovi i lokalni docker build više nisu potrebni."
echo "Ručna provjera:"
echo "  sudo systemctl start grampsweb-bcs-update.service"
echo "Dnevnik:"
echo "  sudo journalctl -u grampsweb-bcs-update.service -n 100 --no-pager"
echo "Sljedeći termin:"
echo "  sudo systemctl list-timers grampsweb-bcs-update.timer --no-pager"
