import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return None


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print("sqlite:", e)


def fetchOne(*args, **kwargs):
    c = conn.cursor()
    c.execute(*args, **kwargs)
    result = c.fetchone()
    return result


def fetchAll(*args, **kwargs):
    c = conn.cursor()
    c.execute(*args, **kwargs)
    result = c.fetchall()
    return result


def insert(*args, **kwargs):
    c = conn.cursor()
    c.execute(*args, **kwargs)
    if kwargs.get('commit', True): conn.commit()
    return c.lastrowid


def update(*args, **kwargs):
    c = conn.cursor()
    c.execute(*args, **kwargs)
    if kwargs.get('commit', True): conn.commit()
    return c.rowcount


conn = create_connection("data.sqlite")


def ddmmyyyyToyyyymmdd(ddmmyyyy):
    # converts DD/MM/YYYY to YYYY-MM-DD
    return "-".join(ddmmyyyy.split("/")[::-1])


conn.create_function("DMYtoYMD", 1, ddmmyyyyToyyyymmdd)
