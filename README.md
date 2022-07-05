# postgres-cstore

A docker image and container of PostgreSQL with the columnar store. The data used in a machine learning model or AI is extensive, so Postgres is extended to the columnar store implemented by [Citus Data](#https://github.com/citusdata/cstore_fdw).

## Table of content

- [Bulding steps](#Building-steps)
    - [Build image from docker-compose](#Build-image-from-docker-compose)
    - [Run container](#Run-container)
    - [Load data](#Load-data)
    - [Export volume](#Export-volume)
- [Python client](#Python-client)
    - [Manipulate container](#Manipulate-container)
    - [Manipulate postgres_cstore](#Manipulate-postgres_cstore)
- [EtLT process](#EtLT-process)
    
## Building steps

### Build image from docker-compose

You don't need to build the image if you use the image from the docker hub. But you can build the image manually. Here are the build steps.

```shell
# Clone this repository.
$ git clone https://github.com/takahish/postgres-cstore.git

# Update submodules.
$ git submodule update --init --recursive

# Build postgres-cstore image.
$ docker-compose -f docker-compose-for-build.yml build
```

### Run container

```shell
# Detach posgres-cstore.
# Here is the commands if you build image manually.
$ docker-compose -f docker-compose-for-build.yml up -d

# ... or you can run the container directly from the image from the docker hub.
# After this step, I will describe the topics using the image from the docker hub.
$ docker-compose up -d

# Here is psql connection settings.
$ export PGUSER=dwhuser
$ export PGPASSWORD=dwhuser

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
$ psql -h localhost -d dwhuser -f src/ddl/cstore_fdw.sql 
CREATE EXTENSION
CREATE SERVER

# Difine tables.
$ psql -h localhost -d dwhuser -f src/ddl/test_customer_reviews.sql
CREATE SCHEMA
CREATE FOREIGN TABLE

# Load sample data.
# Use \copy meta-command.
$ psql -h localhost -d dwhuser
psql (13.1, server 12.11 (Debian 12.11-1.pgdg110+1))
Type "help" for help.

dwhuser=# \copy test.customer_reviews from 'data/customer_reviews_1998.csv' with csv

COPY 589859
dwhuser=# \copy test.customer_reviews from 'data/customer_reviews_1999.csv' with csv
COPY 1172645
dwhuser=# ANALYZE test.customer_reviews;
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
$ tar -jcvf warehouse.tar.bz2 warehouse
```

```shell
# Restore volume.
$ tar -jxvf warehouse.tar.bz2 

# Run container.
$ docker-compose up -d

# Here is psql connection settings.
$ export PGUSER=dwhuser
$ export PGPASSWORD=dwhuser

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
>>> from postgres_cstore import Config, Container

# The default configuration is the same as conf/system.ini
>>> c = Container(config=Config())

# Start containers of composing (default docker-compose.yml).
>>> print(c.compose_up())
Creating network "postgres-cstore_default" with the default driver
Creating postgres-cstore_postgres-cstore_1 ... 
Creating postgres-cstore_postgres-cstore_1 ... done

# Stop containers.
>>> print(c.compose_down())
Stopping postgres-cstore_postgres-cstore_1 ... 
Stopping postgres-cstore_postgres-cstore_1 ... done
Removing postgres-cstore_postgres-cstore_1 ... 
Removing postgres-cstore_postgres-cstore_1 ... done
Removing network postgres-cstore_default
```

### Manipulate postgres with columnar store

The First is an execution of SQL. The exec method returns an output as a string.

```pycon
>>> from postgres_cstore import Config, Client

# The default configuration is the same as conf/system.ini
>>> ps = Client(config=Config()) 

# Execute sql.
>>> print(ps.execute(sql="SELECT customer_id, review_date from test.customer_reviews LIMIT 10;"))
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

# Execute sql that is written in a file.
>>> print(ps.execute_from_file(sql_file="src/dml/find_customer_reviews.sql"))
customer_id   | review_date | review_rating | product_id 
----------------+-------------+---------------+------------
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0399128964
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 044100590X
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0441172717
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 0881036366
 A27T7HVDXA3K2A | 1998-04-10  |             5 | 1559949570
(5 rows)

# Execute sql that is written in a template with keyword arguments.
>>> print(ps.execute_from_template(sql_template="src/dml/find_customer_reviews_template.sql", placeholder={'customer_id': 'A27T7HVDXA3K2A'}))
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
# Extract data.
>>> first_query = ps.make_query_id()
>>> df = ps.extract(sql="SELECT customer_id, review_date from test.customer_reviews LIMIT 10;", query_id=first_query)
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

# Extract data using sql that is written in a file.
>>> second_query = ps.make_query_id()
>>> df = ps.extract_from_file(sql_file="src/dml/find_customer_reviews.sql", query_id=second_query)
>>> df
      customer_id review_date  review_rating  product_id
0  A27T7HVDXA3K2A  1998-04-10              5  0399128964
1  A27T7HVDXA3K2A  1998-04-10              5  044100590X
2  A27T7HVDXA3K2A  1998-04-10              5  0441172717
3  A27T7HVDXA3K2A  1998-04-10              5  0881036366
4  A27T7HVDXA3K2A  1998-04-10              5  1559949570

# Extract data using sql that is written in a template with keyword arguments.
>>> third_query = ps.make_query_id()
>>> df = ps.extract_from_template(sql_template="src/dml/find_customer_reviews_template.sql", placeholder={'customer_id': 'A27T7HVDXA3K2A'}, query_id=third_query)
>>> df
      customer_id review_date  review_rating  product_id
0  A27T7HVDXA3K2A  1998-04-10              5  0399128964
1  A27T7HVDXA3K2A  1998-04-10              5  044100590X
2  A27T7HVDXA3K2A  1998-04-10              5  0441172717
3  A27T7HVDXA3K2A  1998-04-10              5  0881036366
4  A27T7HVDXA3K2A  1998-04-10              5  1559949570
```

The methods exports a temporary file to ./data/query/*. The query_id.csv.gz is a data file and the query_id.json is a meta file.

```shell
$ ls data/query/
2360e089ecbab90b820487ad5eb44ebb.csv.gz
2360e089ecbab90b820487ad5eb44ebb.json
2dab25635e049fe04a2fcdf0caff9573.csv.gz
2dab25635e049fe04a2fcdf0caff9573.json
a25d09fd8d5fcbebf271e00d49c0ab09.csv.gz
a25d09fd8d5fcbebf271e00d49c0ab09.json
```

## EtLT process

Here is an EtLT process (the subpattern of ELT process) for the customer_reviews. 

```shell
$ python etlt_customer_reviews.py
```

Here is the code of the etlt_customer_reviews.py.

```pycon
# Import related to the ETL process.
from collections import OrderedDict
from postgres_cstore import Config, Container, FileIO, Client

# Make an instance of FileIO and Client.
config = Config()
ct = Container(config)
io = FileIO(config)
ps = Client(config)

# Start containers of composing to store the data processed as ETL/ELT/EtLT.
_ = ct.compose_up()

# Define data types of the raw data. dtype is OrderedDict of a pair of column name and data type.
dtype = OrderedDict([
    ('customer_id', 'object'),
    ('review_date', 'object'),
    ('review_rating', 'int64'),
    ('review_votes', 'int64'),
    ('review_helpful_votes', 'int64'),
    ('product_id', 'object'),
    ('product_title', 'object'),
    ('product_sales_rank', 'int64'),
    ('product_group', 'object'),
    ('product_category', 'object'),
    ('product_subcategory', 'object'),
    ('similar_product_ids', 'object')
])

# Extract the raw data from data directory.
# FileIO.data_load walks through in the directory to find files with a pattern.
# The method returns the pd.Dataframe and the list of a processed files.
df, processed_file_list = io.data_load(
    pattern='customer_reviews_*.csv',
    header=None,
    names=list(dtype.keys()),
    dtype=dtype,
    parse_dates=['review_date'],
    delimiter=','
)

# processed_file_list has two file names which are loaded from the data directory.
# print(processed_file_list)
# ['data/customer_reviews_1999.csv', 'data/customer_reviews_1998.csv']

# You can cleanse pr preprocess the data using python libraries.
subset = ['customer_id', 'review_date', 'product_id']
df = df.dropna(subset=subset)
df = df.drop_duplicates(subset=subset, keep='first')

# Dump the data to the temporary directory as CSV.
# The io.data_dump method returns the output message from process. In this case, it is ignored.
_ = io.data_dump(data_frame=df, temporary_file_name='customer_reviews.csv', index=False, header=False)

# Recreate the table on the postgres-cstore.
# The ps.execute method returns the output message from process. In this case, it is ignored.
_ = ps.execute(sql="DROP FOREIGN TABLE test.customer_reviews;")
_ = ps.execute(sql="CREATE SCHEMA IF NOT EXISTS test;")
_ = ps.execute(sql="""
CREATE FOREIGN TABLE IF NOT EXISTS test.customer_reviews
(
    customer_id TEXT,
    review_date DATE,
    review_rating INTEGER,
    review_votes INTEGER,
    review_helpful_votes INTEGER,
    product_id CHAR(10),
    product_title TEXT,
    product_sales_rank BIGINT,
    product_group TEXT,
    product_category TEXT,
    product_subcategory TEXT,
    similar_product_ids CHAR(10)[]
)
SERVER cstore_server
OPTIONS(compression 'pglz');
""")

# Load the CSV file which is cleaned and preprocessed in the temporary directory.
# The ps.load method returns the output message from process. In this case, it is ignored.
_ = ps.load(csv_file="customer_reviews.csv", schema_name="test", table_name="customer_reviews")
```
