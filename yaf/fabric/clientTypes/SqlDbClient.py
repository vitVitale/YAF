import pandas as pd
from time import sleep
from tabulate import tabulate
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import Session


class SqlDbCl:
    def __init__(self, config: dict):
        config.pop('name')
        self.config = config.copy()
        self.engine = create_engine(URL.create(**config))
        self.session = None

    def launch_session(self):
        self.session = Session(self.engine)
        self.session.begin()

    def shutdown_session(self):
        self.session.close()
        self.session = None

    def execute(self, query: str):
        if query is None:
            raise Exception('Request not specified!')
        res = self._exec(query)
        self.session.commit()
        return res.rowcount > 0

    def fetch(self, query: str, empty_required: bool):
        if query is None:
            raise Exception('Request not specified!')
        return self._get_empty_or_not_result_by_timeout(query, 10, empty_required)

    def _get_empty_or_not_result_by_timeout(self, query, timeout, empty):
        res = None
        for _ in range(timeout*2):
            res = self._exec(query)
            if (res.rowcount > 0) != empty:
                break
            sleep(0.5)
        if (res.rowcount > 0) != empty:
            return ResultSet(cursor=res.cursor) if not empty else ResultSet()
        raise AssertionError(f'Wrong expected result, number of records: {res.rowcount}')

    def _exec(self, query):
        try:
            return self.session.execute(text(query))
        except OperationalError as ex:
            self.launch_session()
            print(f'Catch error: {ex}')
            return self.session.execute(text(query))
        except Exception as exc:
            self.session.rollback()
            raise exc


class ResultSet:
    def __init__(self, cursor=None):
        if cursor:
            self.rows: list = cursor.fetchall()
            self.headers: list = []
            for i in range(len(cursor.description)):
                self.headers.append(cursor.description[i].name)
            self.text_layout = self._get_layout()
        else:
            self.text_layout = 'EMPTY!'

    def _get_layout(self):
        rows_num = 50 if len(self.rows) > 50 else len(self.rows)
        suffix = '\n|...record(s) truncated...' if len(self.rows) > 50 else ''
        df = pd.DataFrame(data=self.rows[:rows_num], columns=self.headers)
        for index in range(df.shape[1]):
            if df.iloc[:, index].dtype.name == 'object':
                df.iloc[:, index] = df.iloc[:, index].apply(lambda a: a.replace('\n', '\\n') if isinstance(a, str) else a)
                df.iloc[:, index] = df.iloc[:, index].apply(lambda a: f'{a[:47]}...' if isinstance(a, str) and len(a) > 50 else a)

        table = tabulate(tabular_data=df,
                         headers=self.headers,
                         tablefmt='psql',
                         missingval='NULL',
                         showindex=[item for item in range(1, rows_num+1)])
        return f'{table}{suffix}'

    def get_column_values(self, column):
        df = pd.DataFrame(data=self.rows, columns=self.headers)
        return df[column].tolist()

    def get_cell_value(self, column, row=None):
        column_values = self.get_column_values(column)
        if isinstance(row, str):
            if 'ALL' == row.upper():
                return str(column_values)[1:-1]
        row = 1 if row is None else row
        try:
            return column_values[int(row)-1]
        except IndexError as ex:
            raise AssertionError(f'Row {row} does not exist!\n'
                                 f'Results set size {len(column_values)}.')
