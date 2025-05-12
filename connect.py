import pymysql
from configparser import ConfigParser

def read_db_config(filename='database.ini', section='mysql'):
    parser = ConfigParser()
    parser.read(filename)

    if parser.has_section(section):
        return {param[0]: param[1] for param in parser.items(section)}
    else:
        raise Exception(f"Section {section} not found in {filename}")

def connect_database():
    db_config = read_db_config()
    connection = pymysql.connect(
        host=db_config['host'],
        port=int(db_config.get('port', 3306)),
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    return connection.cursor(), connection

def execute_sql_script(filename='inventory_system.sql'):
    connection = pymysql.connect(
        host='localhost',
        user='varisshaa',
        password='varisha.2005'  # Replace with your real password
    )
    cursor = connection.cursor()

    with open(filename, 'r') as f:
        sql_script = f.read()

    # Split queries by semicolon, ignoring empty lines
    queries = [q.strip() for q in sql_script.split(';') if q.strip()]
    
    for query in queries:
        try:
            cursor.execute(query)
        except Exception as e:
            print(f"Error executing query: {query}\n{e}")

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == '__main__':
    execute_sql_script()
