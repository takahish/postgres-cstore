# postgres-cstore

A docker image and container of PostgreSQL with the columnar store. The data used in a machine learning model or AI is extensive, so Postgres is extended to the columnar store implemented by [Citus Data](#https://github.com/citusdata/cstore_fdw).

## Table of content

- [Bulding steps](#Building-steps)
    - [Pull image from docker hub](#Build-image)
    - [Run container](#Run-container)
    - [Load data](#Load-data)
    - [Export volume](#Export-volume)
- [Python client](#Python-client)
    - [Manipulate container](#Manipulate-container)
    - [Manipulate postgres_cstore](#Manipulate-postgres_cstore)
    
## Building steps

### Pull image from docker hub

```shell
# Pull image from docker hub
$ docker pull takahish/postgres-cstore:12.11  # latest version is 12.11
```

#### ... or manually build image

```shell
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

```shell
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

```shell
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

```shell
# Export volume to persist data.
$ docker run --rm --volumes-from postgres-cstore -v $(pwd):/backup debian:latest tar zcvf /backup/warehouse.tar.gz /var/lib/postgresql/data
```

```shell
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

## Python client

### Manipulate container

```pycon
>>> from postgres_cstore.config import Config
>>> from postgres_cstore.container import Container
>>> c = Container(config=Config())  # The default configuration is the same as conf/system.ini
>>> c.run()  # Run container from image and start container.
>>> c.run()  # An error occurs if the container already exists. 
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/takahiro/work/postgres-cstore/postgres_cstore/container.py", line 56, in run
    volume=self.volume
  File "/Users/takahiro/work/postgres-cstore/postgres_cstore/process.py", line 17, in run
    raise Exception(output)
Exception: docker: Error response from daemon: Conflict. The container name "/postgres-cstore" is already in use by container "56f3bdc5855a0e6a467854d656dd051ae46e9fc2c39de12ab09c097752a80f03". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.
>>> c.stop()  # Stop container.
'postgres-cstore'
>>> c.start()  # Start container if the container already exists.
'postgres-cstore'
>>> c.stop()  # Stop container.
'postgres-cstore'
>>>
```

### Manipulate postgres_cstore

The First is an execution of SQL. The exec method returns an output as a string.

```pycon
>>> from postgres_cstore.config import Config
>>> from postgres_cstore.postgres_cstore import PostgresCstore
>>> ps = PostgresCstore(config=Config())  # The default configuration is the same as conf/system.ini
>>> print(ps.exec(sql="SELECT customer_id, review_date from customer_reviews LIMIT 10;"))  # Execute sql.
customer_id   | review_date 
----------------+-------------
 AE22YDHSBFYIP  | 1970-12-30
 AE22YDHSBFYIP  | 1970-12-30
 ATVPDKIKX0DER  | 1995-06-19
 AH7OKBE1Z35YA  | 1995-06-23
 ATVPDKIKX0DER  | 1995-07-14
 A102UKC71I5DU8 | 1995-07-18
 A1HPIDTM9SRBLP | 1995-07-18
 A1HPIDTM9SRBLP | 1995-07-18
 ATVPDKIKX0DER  | 1995-07-18
 ATVPDKIKX0DER  | 1995-07-18
(10 rows)
>>> print(ps.exec_from_file(sql_file="src/dml/find_customer_reviews.sql"))  # Execute sql that is written in a file.
customer_id   | review_date | review_rating | product_id 
----------------+-------------+---------------+------------
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0399128964
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 044100590X
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0441172717
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0881036366
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 1559949570
(5 rows)
```

The second is an extraction of data from the output. The output is pandas.DataFrame object. The method doesn’t need a Postgres client library such as pycong2 (It only needs pandas).

```pycon
>>> first_query = ps.make_hash_id() # The hash_id identifies a query.
>>> df = ps.ext(sql="SELECT customer_id, review_date from customer_reviews LIMIT 10;", query_id=first_query)
>>> df
      customer_id review_date
0   AE22YDHSBFYIP  1970-12-30
1   AE22YDHSBFYIP  1970-12-30
2   ATVPDKIKX0DER  1995-06-19
3   AH7OKBE1Z35YA  1995-06-23
4   ATVPDKIKX0DER  1995-07-14
5  A102UKC71I5DU8  1995-07-18
6  A1HPIDTM9SRBLP  1995-07-18
7  A1HPIDTM9SRBLP  1995-07-18
8   ATVPDKIKX0DER  1995-07-18
9   ATVPDKIKX0DER  1995-07-18
>>> second_query = ps.make_hash_id()
>>> df = ps.ext_from_file(sql_file="src/dml/find_customer_reviews.sql", query_id=second_query)
>>> df
      customer_id review_date  review_rating  product_id
0  A27T7HVDXA3K2A  1998-04-10              5  0399128964
1  A27T7HVDXA3K2A  1998-04-10              5  044100590X
2  A27T7HVDXA3K2A  1998-04-10              5  0441172717
3  A27T7HVDXA3K2A  1998-04-10              5  0881036366
4  A27T7HVDXA3K2A  1998-04-10              5  1559949570
```

The methods exports a temporary file to ./out/query/*.

```shell
$ ls ./out/query/
c843461198336e0137cc62cf60414391.csv.gz
ce6c98b1ba8147a3cbde3abc128b01bd.csv.gz
```

When loading data to a table, it has to create a foreign table in advance. Then load method loads data to the table.

```pycon
>>> ps.exec_from_file(sql_file="src/ddl/create_customer_reviews.sql")
'CREATE FOREIGN TABLE'
>>> ps.load(csv_file="data/customer_reviews_1998.csv", target_table="customer_reviews")
'COPY 589859'
>>> ps.load(csv_file="data/customer_reviews_1999.csv", target_table="customer_reviews")
'COPY 1172645'
>>>
```
