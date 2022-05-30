-- load extension first time after install
CREATE EXTENSION IF NOT EXISTS cstore_fdw;

-- create server object
CREATE SERVER cstore_server FOREIGN DATA WRAPPER cstore_fdw;
