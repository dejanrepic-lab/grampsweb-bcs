ARG UPSTREAM_IMAGE=ghcr.io/gramps-project/grampsweb:latest
FROM ${UPSTREAM_IMAGE}

ARG UPSTREAM_DIGEST=unknown
ARG VCS_REF=unknown

LABEL org.opencontainers.image.title="Gramps Web BCS" \
      org.opencontainers.image.description="Gramps Web with Serbian Latin UI and BCS relationship names" \
      org.opencontainers.image.source="https://github.com/dejanrepic-lab/grampsweb-bcs" \
      org.opencontainers.image.url="https://github.com/dejanrepic-lab/grampsweb-bcs" \
      org.opencontainers.image.licenses="GPL-3.0-or-later" \
      org.opencontainers.image.revision="${VCS_REF}" \
      io.github.dejanrepic-lab.grampsweb-bcs.upstream-digest="${UPSTREAM_DIGEST}"

COPY patch_rel_hr.py patch_sr_latin.py verify_image.py /tmp/grampsweb-bcs/
RUN python3 /tmp/grampsweb-bcs/patch_rel_hr.py \
    && python3 /tmp/grampsweb-bcs/patch_sr_latin.py \
    && python3 /tmp/grampsweb-bcs/verify_image.py \
    && install -D -m 0644 /tmp/grampsweb-bcs/verify_image.py /usr/local/lib/grampsweb-bcs/verify_image.py \
    && rm -rf /tmp/grampsweb-bcs
