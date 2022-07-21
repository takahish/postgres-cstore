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

# Create a foreign server of cstore_fdw.
_ = ps.execute(sql="CREATE EXTENSION IF NOT EXISTS cstore_fdw;")
_ = ps.execute(sql="CREATE SERVER IF NOT EXISTS cstore_server FOREIGN DATA WRAPPER cstore_fdw;")

# Recreate the table on the postgres-cstore.
# The ps.execute method returns the output message from process. In this case, it is ignored.
_ = ps.execute(sql="CREATE SCHEMA IF NOT EXISTS test;")
_ = ps.execute(sql="DROP FOREIGN TABLE IF EXISTS test.customer_reviews;")
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
