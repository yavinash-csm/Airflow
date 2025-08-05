from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final
import os
import pandas as pd
import click
import sys
from sqlalchemy import create_engine, text

class IO(ABC):
    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        pass

class CSVReader(IO):
    def __init__(self, path: Path, sep: str = ","):
        self.path = path
        self.sep = sep

    def load_data(self) -> pd.DataFrame:
        return pd.read_csv(self.path, sep=self.sep)

#Database
SQL_FILE_MAP: Final[dict[str, str]] = {
    "NEG_CHECKER_TABLE": "sql/neg_checker.sql",
    "DUP_REQ_TABLE": "sql/dup_req.sql",
    "SHORT_STRATS_TABLE": "sql/short_strats.sql",
    "CONTRACT_REQ_TABLE": "sql/contract_req.sql",
}

def get_database(file_path: str, params=None, args: tuple = ()) -> pd.DataFrame:
    with open(file_path, 'r') as f:
        query = f.read().format(*args)
    conn_str = (
        f"mssql+pyodbc://{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
        f"?driver={os.getenv('DB_DRIVER').replace('{', '').replace('}', '')}"
        f"&trusted_connection={os.getenv('DB_TRUSTED_CONN', 'yes')}"
    )
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    return df    

def get_io_source(source_key: str, sep: str = ",") -> IO:
    env = os.getenv("ENVIRONMENT", "prod")
    #print(f"Using ENVIRONMENT: {env}")
    match env:
        case "prod":
            sql_path = SQL_FILE_MAP.get(source_key)
            class SQLReader(IO):
                def load_data(self) -> pd.DataFrame:
                    return get_database(sql_path)
            return SQLReader()

        case "test":
            CSV_FILE_MAP: Final[dict[str, str]] = {
                    "NEG_CHECKER_TABLE": os.getenv("CSV_PATH"),
                    "DUP_REQ_TABLE": os.getenv("CSV_PATH_DUP"),
                    "CONTRACT_REQ_TABLE": os.getenv("CSV_PATH_CON"),
                    "SHORT_STRATS_TABLE": os.getenv("CSV_PATH"),
                }
            csv_path = CSV_FILE_MAP.get(source_key)
            if not csv_path:
                click.echo(f"CSV path for {source_key} not set", err=True)
                sys.exit(1)
            return CSVReader(Path(csv_path), sep=sep)

        case _:
            click.echo(f"Unknown ENVIRONMENT: {env}", err=True)
            sys.exit(1)
