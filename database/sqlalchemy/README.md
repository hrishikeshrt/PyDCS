# Connection to DCS using `SQLAlchemy`

## Folder Structure

This folder contains utility class for pythonic access to DCS database using
`SQLAlchemy`. The database must be imported before using the class.

### Connecting to DB

- Copy `config.sample.py` to `config.py`
- Details of the database login can be added to `config.py` file.
- In particular, Connection URL is used for making the database connection.
  For MySQL, connection url would look like `mysql://user:pass@host:port/db?<optional-connection-params>`
  For convenience, after filling the credentials in `config.py`, `config.mysql_url` can be used as connection URL.
- For MySQL connection `pymysql` is also needed. (`pip install pymysql`)

### Models

- Models (Objects to represent SQL tables) are contained in `models.py`
- These can be generated from the existing schema using `sqlacodegen`
- Database configuration is to be imported for database object creation.

### Utility Functions

- TODO
