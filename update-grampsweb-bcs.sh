#!/usr/bin/env bash

# Sigurno ažuriranje gotove Gramps Web BCS slike sa GitHub Container Registryja.

set -Eeuo pipefail

REMOTE_IMAGE="ghcr.io/dejanrepic-lab/grampsweb-bcs:latest"
ROLLBACK_IMAGE="grampsweb-bcs:rollback"
VERSION_LABEL="io.github.dejanrepic-lab.grampsweb-bcs.upstream-version"
COMPOSE_DIR="${GRAMPSWEB_COMPOSE_DIR:-/var/lib/casaos/apps/heartwarming_matthias}"
DOCKER_CONFIG_DIR="/tmp/grampsweb-bcs-docker-config"
LOCK_FILE="/run/lock/grampsweb-bcs-update.lock"
BACKUP_DIR="/DATA/Backups/grampsweb-auto-update"
SERVICES=(grampsweb grampsweb_celery)
FORCE_UPDATE=false
CHECK_ONLY=false

for argument in "$@"; do
    case "${argument}" in
        --force)
            FORCE_UPDATE=true
            ;;
        --check-only)
            CHECK_ONLY=true
            ;;
        *)
            echo "Upotreba: $0 [--force] [--check-only]" >&2
            exit 2
            ;;
    esac
done

log() {
    printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
    log "GREŠKA: $*"
    exit 1
}

compose() {
    (cd "${COMPOSE_DIR}" && docker compose "$@")
}

image_version() {
    local reference="$1"
    local value
    value="$(docker image inspect --format "{{index .Config.Labels \"${VERSION_LABEL}\"}}" "${reference}" 2>/dev/null || true)"
    [[ "${value}" == "<no value>" ]] && value=""
    printf '%s\n' "${value}"
}

valid_version() {
    [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$ ]]
}

[[ "${EUID}" -eq 0 ]] || die "Pokreni updater kao root (sudo)."
command -v docker >/dev/null 2>&1 || die "Docker nije pronađen."
command -v flock >/dev/null 2>&1 || die "Naredba flock nije pronađena."
[[ -f "${COMPOSE_DIR}/compose.yaml" || -f "${COMPOSE_DIR}/docker-compose.yml" || -f "${COMPOSE_DIR}/docker-compose.yaml" ]] || die "Compose stack nije pronađen u ${COMPOSE_DIR}."

mkdir -p "$(dirname "${LOCK_FILE}")" "${DOCKER_CONFIG_DIR}"
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
    log "Drugo ažuriranje je već u toku; izlazim."
    exit 0
fi

export DOCKER_CONFIG="${DOCKER_CONFIG_DIR}"

running_image_id="$(docker inspect --format '{{.Image}}' grampsweb 2>/dev/null || true)"
[[ -n "${running_image_id}" ]] || die "Aktivni kontejner grampsweb nije pronađen."
running_version="$(image_version "${running_image_id}")"

if valid_version "${running_version}"; then
    log "Trenutno instalirana Gramps Web verzija: ${running_version}."
else
    log "Trenutna slika nema zabilježen broj Gramps Web verzije."
fi

log "Preuzimam posljednju provjerenu Gramps Web BCS sliku."
docker pull "${REMOTE_IMAGE}"
remote_image_id="$(docker image inspect --format '{{.Id}}' "${REMOTE_IMAGE}")"
remote_version="$(image_version "${REMOTE_IMAGE}")"
valid_version "${remote_version}" || die "Preuzeta BCS slika nema važeću oznaku Gramps Web verzije."

embedded_version="$(docker run --rm --entrypoint cat "${REMOTE_IMAGE}" \
    /usr/local/lib/grampsweb-bcs/upstream-version)"
[[ "${embedded_version}" == "${remote_version}" ]] || die "Broj verzije u slici ne odgovara njenoj Docker oznaci."
log "Posljednja provjerena dostupna Gramps Web verzija: ${remote_version}."

log "Provjeravam BCS odnose i srpsku latinicu u preuzetoj slici."
docker run --rm --entrypoint python3 "${REMOTE_IMAGE}" \
    /usr/local/lib/grampsweb-bcs/verify_image.py

if [[ "${CHECK_ONLY}" == true ]]; then
    log "Provjera verzije ${remote_version} je uspješna; aktivni kontejneri nisu mijenjani."
    exit 0
fi

if [[ "${FORCE_UPDATE}" == false && "${running_image_id}" == "${remote_image_id}" ]]; then
    log "Već koristiš Gramps Web BCS ${remote_version}; ništa nije mijenjano."
    exit 0
fi

if valid_version "${running_version}"; then
    log "Ažuriram Gramps Web sa ${running_version} na ${remote_version}."
else
    log "Ažuriram Gramps Web na provjerenu verziju ${remote_version}."
fi

docker tag "${running_image_id}" "${ROLLBACK_IMAGE}"

declare -a backup_sources=()
while IFS='|' read -r destination source; do
    case "${destination}" in
        /root/.gramps|/root/.gramps/grampsdb|/app/users)
            [[ -n "${source}" ]] && backup_sources+=("${source}")
            ;;
    esac
done < <(docker inspect --format '{{range .Mounts}}{{printf "%s|%s\n" .Destination .Source}}{{end}}' grampsweb)

if (( ${#backup_sources[@]} < 2 )); then
    die "Nisam pronašao oba očekivana mounta (baza i korisnici); zaustavljam ažuriranje radi sigurnosti."
fi

mkdir -p "${BACKUP_DIR}"
backup_file="${BACKUP_DIR}/pre-update-$(date '+%Y%m%d-%H%M%S').tar.gz"

log "Zaustavljam Gramps i Celery radi konzistentne kopije baze."
if ! compose stop "${SERVICES[@]}"; then
    compose up -d "${SERVICES[@]}" || true
    die "Nije uspjelo uredno zaustavljanje servisa."
fi

log "Pravim sigurnosnu kopiju baze i korisnika: ${backup_file}"
if ! tar --xattrs --acls -czf "${backup_file}" "${backup_sources[@]}"; then
    compose up -d "${SERVICES[@]}" || true
    die "Sigurnosna kopija nije uspjela; prethodni Gramps je ponovo pokrenut."
fi

rollback() {
    local reason="$1"
    log "Nova verzija nije uspješno pokrenuta: ${reason}"
    if valid_version "${running_version}"; then
        log "Vraćam prethodnu Gramps Web verziju ${running_version}."
    else
        log "Vraćam prethodnu Docker sliku."
    fi
    docker tag "${ROLLBACK_IMAGE}" "${REMOTE_IMAGE}"
    compose up -d --force-recreate "${SERVICES[@]}" || true
    die "Ažuriranje je prekinuto; provjeri: journalctl -u grampsweb-bcs-update.service"
}

log "Ponovo pravim Gramps Web i Celery kontejnere."
if ! compose up -d --force-recreate "${SERVICES[@]}"; then
    rollback "docker compose up nije uspio"
fi

log "Čekam da Gramps Web postane zdrav."
deadline=$((SECONDS + 240))
while (( SECONDS < deadline )); do
    web_status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' grampsweb 2>/dev/null || true)"
    celery_status="$(docker inspect --format '{{.State.Status}}' grampsweb_celery 2>/dev/null || true)"

    if [[ "${web_status}" == "healthy" && "${celery_status}" == "running" ]]; then
        active_image_id="$(docker inspect --format '{{.Image}}' grampsweb)"
        [[ "${active_image_id}" == "${remote_image_id}" ]] || rollback "kontejner ne koristi preuzetu BCS sliku"

        log "Ažuriranje na Gramps Web ${remote_version} je uspješno. Gramps Web je zdrav, a BCS zakrpa je aktivna."
        docker image rm "${ROLLBACK_IMAGE}" >/dev/null 2>&1 || true

        mapfile -t saved_backups < <(find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'pre-update-*.tar.gz' | sort -r)
        if (( ${#saved_backups[@]} > 5 )); then
            for old_backup in "${saved_backups[@]:5}"; do
                [[ "${old_backup}" == "${BACKUP_DIR}"/pre-update-*.tar.gz ]] && rm -- "${old_backup}"
            done
        fi
        exit 0
    fi

    if [[ "${web_status}" == "unhealthy" || "${web_status}" == "exited" || "${celery_status}" == "exited" || "${celery_status}" == "dead" ]]; then
        rollback "grampsweb=${web_status}, celery=${celery_status}"
    fi
    sleep 5
done

rollback "isteklo je vrijeme čekanja (grampsweb=${web_status:-nepoznato}, celery=${celery_status:-nepoznato})"
