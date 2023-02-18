FROM debian:bullseye-slim
LABEL maintainer="Victor Laskurain <blaskurain@binovo.es>"
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Generate tracebacks for segfaults on C code
ENV PYTHONFAULTHANDLER=1
RUN export DEBIAN_FRONTEND=noninteractive

# install OCB dependencies and wget
RUN apt update
RUN apt install -y \
    adduser \
    fonts-dejavu-core \
    fonts-font-awesome \
    fonts-inconsolata \
    fonts-roboto-unhinted \
    gsfonts \
    libjs-underscore \
    lsb-base \
    postgresql-client \
    python3-babel \
    python3-chardet \
    python3-dateutil \
    python3-decorator \
    python3-docutils \
    python3-freezegun \
    python3-jinja2 \
    python3-ldap \
    python3-libsass \
    python3-lxml \
    python3-num2words \
    python3-ofxparse \
    python3-openssl \
    python3-passlib \
    python3-pil \
    python3-polib \
    python3-psutil \
    python3-psycopg2 \
    python3-pydot \
    python3-pypdf2 \
    python3-qrcode \
    python3-renderpm \
    python3-reportlab \
    python3-requests \
    python3-stdnum \
    python3-tz \
    python3-vobject \
    python3-werkzeug \
    python3-xlrd \
    python3-xlsxwriter \
    python3-zeep \
    wget

# install wkhtmltopdf
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.buster_amd64.deb -qO /tmp/wkhtmltox_0.12.5-1.buster_amd64.deb
RUN apt install -y xfonts-75dpi xfonts-base
RUN dpkg -i /tmp/wkhtmltox_0.12.5-1.buster_amd64.deb

# install black and prettier
RUN apt install -y black npm
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
