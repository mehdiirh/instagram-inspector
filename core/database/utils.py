from typing import TypeVar, Callable
import sqlite3
from typing import Callable
from functools import wraps
from pathlib import Path

T = TypeVar("T", bound=Callable)
DATABASE_PATH = Path(__file__).parent.parent.parent / "database.sqlite3"


class Cursor:

    connection = None
    cursor = None

    def __init__(self, close_on_exit=True):
        self.close_on_exit = close_on_exit

    def __enter__(self):
        self.connection = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_on_exit:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None:
                self.connection.close()


def dataclass_constructor(cursor, dataclass: Callable, fetchone=False):
    columns = list(map(lambda x: x[0], cursor.description))
    dataset = cursor.fetchall()
    cursor.close()
    cursor.connection.close()
    dataset = [dataclass(**dict(zip(columns, data))) for data in dataset]
    if fetchone:
        if dataset:
            dataset = dataset[0]
        else:
            dataset = None

    return dataset


def dataclass_wrapper(dataclass: Callable, fetchone=False):
    def inner(fn: T) -> T:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            cursor = fn(*args, **kwargs)
            return dataclass_constructor(cursor, dataclass, fetchone)

        return wrapper

    return inner
