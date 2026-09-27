FROM debian:trixie-slim
LABEL maintainer="Victor Laskurain <blaskurain@binovo.es>"
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Generate tracebacks for segfaults on C code
ENV PYTHONFAULTHANDLER=1
RUN export DEBIAN_FRONTEND=noninteractive

# install OCB dependencies and wget
RUN apt update && \
    apt install -y --no-install-recommends \
    adduser \
    fonts-dejavu-core \
    fonts-font-awesome \
    fonts-inconsolata \
    fonts-roboto-unhinted \
    gsfonts \
    lsb-base \
    postgresql-client \
    python3-asn1crypto \
    python3-babel \
    python3-cbor2 \
    python3-chardet \
    python3-cryptography \
    python3-dateutil \
    python3-decorator \
    python3-docutils \
    python3-freezegun \
    python3-geoip2 \
    python3-gevent \
    python3-greenlet \
    python3-h11 \
    python3-idna \
    python3-pil \
    python3-jinja2 \
    python3-ldap \
    python3-libsass \
    python3-lxml \
    python3-lxml-html-clean \
    python3-magic \
    python3-markupsafe \
    python3-num2words \
    python3-ofxparse \
    python3-openssl \
    python3-openpyxl \
    python3-passlib \
    python3-polib \
    python3-psutil \
    python3-psycopg2 \
    python3-openssl \
    python3-pypdf \
    python3-rjsmin \
    python3-qrcode \
    python3-renderpm \
    python3-reportlab \
    python3-requests \
    python3-stdnum \
    python3-urllib3 \
    python3-vobject \
    python3-werkzeug \
    python3-xlsxwriter \
    python3-xlrd \
    python3-zeep \
    wget

# install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb -qO /tmp/wkhtmltox.deb && \
    apt install -y xfonts-75dpi xfonts-base libxext6 fontconfig && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" > /etc/apt/sources.list.d/buster.list && \
    apt update && \
    apt install libssl1.1 && \
    rm /etc/apt/sources.list.d/buster.list && \
    apt update && \
    dpkg -i /tmp/wkhtmltox.deb && \
    rm /tmp/wkhtmltox.deb

# install black and prettier
RUN apt install -y --no-install-recommends black npm
RUN npm install -g prettier

RUN ln -s /opt/src/submodules/ocb/odoo-bin /usr/local/bin/odoo

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

# Set default user when running the container
RUN groupadd odoo -g 1000
RUN useradd  odoo -u 1000 -g odoo -d /var/lib/odoo
RUN mkdir -p /var/lib/odoo
RUN chown odoo.odoo /var/lib/odoo
USER odoo
