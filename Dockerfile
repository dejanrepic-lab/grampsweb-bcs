ARG UPSTREAM_IMAGE=ghcr.io/gramps-project/grampsweb:latest
FROM ${UPSTREAM_IMAGE}

ARG UPSTREAM_DIGEST=unknown
ARG UPSTREAM_VERSION=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="Gramps Web BCS"
LABEL org.opencontainers.image.description="Gramps Web with Serbian Latin UI and BCS relationship names"
LABEL org.opencontainers.image.source="https://github.com/dejanrepic-lab/grampsweb-bcs"
LABEL org.opencontainers.image.url="https://github.com/dejanrepic-lab/grampsweb-bcs"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="${UPSTREAM_VERSION}"
LABEL io.github.dejanrepic-lab.grampsweb-bcs.upstream-digest="${UPSTREAM_DIGEST}"
LABEL io.github.dejanrepic-lab.grampsweb-bcs.upstream-version="${UPSTREAM_VERSION}"

COPY patch_rel_hr.py patch_sr_latin.py verify_image.py /tmp/grampsweb-bcs/
RUN python3 /tmp/grampsweb-bcs/patch_rel_hr.py \
    && python3 /tmp/grampsweb-bcs/patch_sr_latin.py \
    && python3 -c 'import re; value = "${UPSTREAM_VERSION}"; assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?", value), value' \
    && install -D -m 0644 /dev/null /usr/local/lib/grampsweb-bcs/upstream-version \
    && printf '%s\n' "${UPSTREAM_VERSION}" > /usr/local/lib/grampsweb-bcs/upstream-version \
    && python3 /tmp/grampsweb-bcs/verify_image.py \
    && install -D -m 0644 /tmp/grampsweb-bcs/verify_image.py /usr/local/lib/grampsweb-bcs/verify_image.py \
    && rm -rf /tmp/grampsweb-bcs
