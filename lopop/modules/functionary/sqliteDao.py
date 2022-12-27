import os
import sqlite3
from datetime import datetime
from sqlite3 import DatabaseError
from lopop import logger

DB_PATH = os.path.expanduser('~/.functionary/lopop.db')


class SqliteDao(object):
    def __init__(self, table, columns, fields):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._dbpath = DB_PATH
        self._table = table
        self._columns = columns
        self._fields = fields
        self._create_table()

    def _create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(self._table, self._fields)
        with self._connect() as conn:
            conn.execute(sql)

    def _connect(self):
        # detect_types 中的两个参数用于处理datetime
        return sqlite3.connect(self._dbpath, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)


# noinspection PyArgumentList
class Practice(SqliteDao):

    def __init__(self):
        super().__init__(
            table='practice',
            columns='pid, type, total_num, error_num, gain, comments, time',
            fields='''
            pid INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            total_num INT NOT NULL,
            error_num INT NOT NULL,
            gain TEXT,
            comments TEXT,
            time TEXT NOT NULL
            ''')

    @staticmethod
    def row2item(r, has_pid=False, has_time=True):
        msg = ''
        if not has_pid:
            r = r[1:]
        if not has_time:
            r = r[:-1]
        for data in r:
            if data:
                msg += str(data) + ' '
        return msg + '''
'''

    def add(self, practice):
        with self._connect() as conn:
            try:
                return conn.execute(f'''INSERT INTO {self._table} ({self._columns}) VALUES(NULL, ?, ?, ?, ?, ?, ?)''',
                                    (practice['type'], practice['total_num'], practice['error_num'],
                                     practice['gain'], practice['comments'], practice['time'])).lastrowid
            except sqlite3.DatabaseError as e:
                logger.error(f'[{self._table} add {e}')
                raise DatabaseError('添加失败')

    def find_all(self, page=-1):
        with self._connect() as conn:
            try:
                ret = conn.execute(f'''SELECT {self._columns} FROM {self._table}''', ).fetchall()
                if page == -1:
                    ret = ret[-10:]
                else:
                    # 0-10 10-20
                    fs = (page - 1) * 10 if page >= 1 else 0
                    ed = len(ret) if page * 10 > len(ret) else page * 10
                    ret = ret[fs:ed]
                return ''.join([self.row2item(r, has_pid=True) for r in ret])
            except sqlite3.DatabaseError as e:
                logger.error(f'[{self._table} find_all {e}')
            raise DatabaseError('查询失败')
        return None

    def delete(self, pid):
        with self._connect() as conn:
            try:
                conn.execute(f'''DELETE FROM {self._table} WHERE pid=?''', (pid,))
                return "删除成功"
            except sqlite3.DatabaseError as e:
                logger.error(f'[{self._table} delete {e}')
                return '删除失败'

    def get_today_practice_num(self):
        with self._connect() as conn:
            try:
                today = datetime.now().strftime("%Y-%m-%d")
                ret = conn.execute(
                    f'''SELECT total_num, error_num FROM {self._table} WHERE time=?''',
                    (today,)).fetchall()
                total_num = 0
                error_num = 0
                for r in ret:
                    total_num += r[0]
                    error_num += r[1]
                return total_num, error_num
            except sqlite3.DatabaseError as e:
                logger.error(f'[{self._table} get_today_practice_num {e}')
                raise DatabaseError('查询失败')
        return None

    def find_practice_by(self, param, val, has_time=True):
        with self._connect() as conn:
            try:
                ret = conn.execute(f'''SELECT {self._columns} FROM {self._table} WHERE {param}=?''',
                                   (val,)).fetchall()
                return ''.join([self.row2item(r, has_time=has_time) for r in ret])
            except sqlite3.DatabaseError as e:
                logger.error(f'[{self._table} find_{param} {e}')
                raise DatabaseError('查询失败')
        return None

    def find_practice(self, pid):
        return self.find_practice_by('pid', pid)

    def find_day(self, day):
        return self.find_practice_by('time', day, has_time=False)
