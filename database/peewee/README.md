# Connection to DCS using `peewee`

## Folder Structure

This folder contains utility class for pythonic access to DCS database using
`peewee`. The database must be imported before using the class.

### Connecting to DB
- Copy `config.sample.py` to `config.py`
- Details of the database login can be added to `config.py` file.
- `peewee` is used to make the database connection. (`pip install peewee`)
   `peewee` is a simple and small ORM. (http://docs.peewee-orm.com/en/latest/index.html)
- In particular, Connection URL is used for making the database connection.
  For MySQL, connection url would look like `mysql://user:pass@host:port/db?<optional-connection-params>`
  For convenience, after filling the credentials in `config.py`, `config.mysql_url` can be used as connection URL.
- For MySQL connection `pymysql` is also needed. (`pip install pymysql`)

### Models

- Models (Objects to represent SQL tables) are contained in `models.py`
- These can be generated from the existing schema using:

`$ python -m pwiz -e mysql -u dcs_user -P dcs_dbname >> models.py`

- Database configuration is to be imported for database object creation.
- `connection` function is a decorator to connect to the database before a function call and close it afterwards
  (If the code is to be used in a flask-like framework, the framework can manage connection before and after the requests)
  (Check, http://docs.peewee-orm.com/en/latest/peewee/database.html#framework-integration)

### Utility Functions
- All utility functions are contained in `dcs.py` inside class `DigitalCorpusSanskrit`
- Functions for fetching a corpus, sentence, analysis
- Similar utility functions for relatively complex tasks
