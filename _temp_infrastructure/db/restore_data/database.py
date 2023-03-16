import pandas as pd
import psycopg2


def fillDB():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="admin")

        cur = conn.cursor()
        cur.execute('SET search_path TO data_pipe_cache;')

        with open('reWorkTest.csv', 'r') as f:
            next(f)  # Skip the header row.
            cur.copy_from(f, 'abc_logs', sep=';', columns=['userId', 'query', 'pronounceText', 'intent', 'scenario'])

        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


df = pd.read_csv('output.csv', sep=';')
print(len(df))

for column in df.columns:
    if df[column].dtype.name == 'object':
        df[column] = df[column].apply(lambda a: a.replace('\n', '\\n') if isinstance(a, str) else a)
        df[column] = df[column].apply(lambda a: a.replace(';', '.') if isinstance(a, str) else a)

ndf = df[['userId', 'query', 'pronounceText', 'intent', 'scenario']]
ndf = ndf[ndf['pronounceText'] != 'None']
print(len(ndf))

ndf.sort_values(['userId']).to_csv("reWorkTest.csv", index=False, sep=';')
fillDB()
