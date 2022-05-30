# postgres-cstore

A docker image and container of PostgreSQL with the columnar store. The data used in a machine learning model or AI is extensive, so Postgres is extended to the columnar store implemented by [Citus Data](#https://github.com/citusdata/cstore_fdw).

## Table of content

- [Bulding steps](#Building-steps)
    - [Pull image from docker hub](#Build-image)
    - [Run container](#Run-container)
    - [Load data](#Load-data)
    - [Export volume](#Export volume)
    
## Building steps

### Pull image from docker hub

```sh
# Pull image from docker hub
$ docker pull takahish/postgres-cstore:12.11  # latest version is 12.11
```

#### ... or manually build image

```sh
# Clone this repository.
$ git clone https://github.com/takahish/postgres-cstore.git

# Update submodules.
$ git submodule update --init --recursive

# Build persistent-postgres image.
$ docker build -t postgres-cstore-base:12.11 lib/postgres/12/bullseye

# Build postgres-persistnece-cstore image (This image has columner store).
$ docker build -t postgres-cstore:12.11 .
```

### Run container

```sh
# Detach posgres-cstore.
# If you build image manually, You change the image name to postgres-cstore:12.11. 
$ docker run --name postgres-cstore -p 5432:5432 -e POSTGRES_USER=dwhuser -e POSTGRES_PASSWORD=dwhuser -v warehouse:/var/lib/postgresql/data -d takahish/postgres-cstore:12.11
baec3761b49aaf73abbd34cc8b21f903af72c30c8c71f2ea9f89feff0ccae78f

# Here is psql connection settings.
export PGUSER=dwhuser
export PGPASSWORD=dwhuser

# Connect persistent-postgres-cstore.
# Prerequisite is to install postgresql for using psql.
$ psql -h localhost -d dwhuser
psql (13.1, server 12.11 (Debian 12.11-1.pgdg110+1))
Type "help" for help.

dwhuser=# \dt
Did not find any relations.
dwhuser=# \q
```

### Load data

```sh
# Download sample data.
$ data/download_customer_reviews.sh

# Create foreign server.
$ psql -h localhost -d dwhuser -f src/ddl/create_cstore_fdw.sql 
CREATE EXTENSION
CREATE SERVER

# Difine tables.
$ psql -h localhost -d dwhuser -f src/ddl/create_customer_reviews.sql
CREATE FOREIGN TABLE

# Load sample data.
# Use \copy meta-command.
$ psql -h localhost -d dwhuser
psql (13.1, server 12.11 (Debian 12.11-1.pgdg110+1))
Type "help" for help.

dwhuser=# \copy customer_reviews from 'data/customer_reviews_1998.csv' with csv
COPY 589859
dwhuser=# \copy customer_reviews from 'data/customer_reviews_1999.csv' with csv
COPY 1172645
dwhuser=# ANALYZE customer_reviews;
ANALYZE
dwhuser=# \q

$ psql -h localhost -U dwhuser -d dwhuser -f src/dml/find_customer_reviews.sql
  customer_id   | review_date | review_rating | product_id 
----------------+-------------+---------------+------------
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0399128964
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 044100590X
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0441172717
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0881036366
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 1559949570
(5 rows)

$ psql -h localhost -d dwhuser -f src/dml/take_correlation_customer_reviews.sql
 title_length_bucket | review_average | count  
---------------------+----------------+--------
                   1 |           4.26 | 139034
                   2 |           4.24 | 411318
                   3 |           4.34 | 245671
                   4 |           4.32 | 167361
                   5 |           4.30 | 118422
                   6 |           4.40 | 116412
(6 rows)
```

### Export volume

```sh
# Export volume to persist data.
$ docker run --rm --volumes-from postgres-cstore -v $(pwd):/backup debian:latest tar zcvf /backup/warehouse.tar.gz /var/lib/postgresql/data
```

```sh
# Pull image from docker hub
$ docker pull takahish/postgres-cstore:12.11  # latest version is 12.11

# Run container.
# If you build image manually, You change the image name to postgres-cstore:12.11. 
$ docker run --name postgres-cstore -p 5432:5432 -e POSTGRES_USER=dwhuser -e POSTGRES_PASSWORD=dwhuser -v warehouse:/var/lib/postgresql/data -d takahish/postgres-cstore:12

# Create foreign server.
$ psql -h localhost -d dwhuser -f src/ddl/create_cstore_fdw.sql 
CREATE EXTENSION
CREATE SERVER

# Difine tables.
$ psql -h localhost -d dwhuser -f src/ddl/create_customer_reviews.sql
CREATE FOREIGN TABLE

# Restore volume.
$ docker run --volumes-from postgres-cstore -v $(pwd):/backup debian:latest tar zxvf /backup/warehouse.tar.gz -C /

$ psql -h localhost -U dwhuser -d dwhuser -f src/dml/find_customer_reviews.sql
  customer_id   | review_date | review_rating | product_id 
----------------+-------------+---------------+------------
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0399128964
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 044100590X
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0441172717
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0881036366
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 1559949570
(5 rows)

$ psql -h localhost -d dwhuser -f src/dml/take_correlation_customer_reviews.sql
 title_length_bucket | review_average | count  
---------------------+----------------+--------
                   1 |           4.26 | 139034
                   2 |           4.24 | 411318
                   3 |           4.34 | 245671
                   4 |           4.32 | 167361
                   5 |           4.30 | 118422
                   6 |           4.40 | 116412
(6 rows)
```
