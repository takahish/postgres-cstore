# PostreSQL version is 12.11.
FROM postgres:12.11

LABEL maintainer "Hiro Ishikawa <takahiro.ishikawa@cons.jp>"

# cstore_fdw version is 1.6.2 (latest at 2019/06/17).
# See also, lib/cstore_fdw

# Updating packages and installing for cstore_fdw,
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    libprotobuf-c-dev \
    make \
    postgresql-server-dev-12 \
    protobuf-c-compiler \
    gcc

# Cloning cstore_fdw into /tmp.
RUN mkdir /tmp/cstore_fdw
COPY lib/cstore_fdw/ /tmp/cstore_fdw

# Building cstore_fdw.
RUN cd /tmp/cstore_fdw && PATH=/usr/local/pgsql/bin/:$PATH make && PATH=/usr/local/pgsql/bin/:$PATH make install

# Writing configure of cstore_fdw for a shared library.
RUN cp /usr/share/postgresql/postgresql.conf.sample /etc/postgresql/postgresql.conf
RUN sed -i "s/#shared_preload_libraries = ''/shared_preload_libraries = 'cstore_fdw'/g" /etc/postgresql/postgresql.conf
