# from abc import ABC, abstractmethod
# from pathlib import Path
# from typing import Final
# import os
# import pandas as pd
# import click
# import sys
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv

# load_dotenv()
# env = os.getenv("ENVIRONMENT")
# load_dotenv(dotenv_path=f".env_{env}", override=True) 
# print(f"Environment: {env}")

# class IO(ABC):
#     @abstractmethod
#     def load_data(self) -> pd.DataFrame:
#         pass

# class CSVReader(IO):
#     def __init__(self, path: Path, sep: str = ","):
#         self.path = path
#         self.sep = sep

#     def load_data(self) -> pd.DataFrame:
#         return pd.read_csv(self.path, sep=self.sep)

# def get_database(file_path: str, params=None, args: tuple = ()) -> pd.DataFrame:
#     with open(file_path, "r") as f:
#         query = f.read().format(*args)

#     conn_str = (
#         f"mssql+pyodbc://{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
#         f"?driver={os.getenv('DB_DRIVER').replace('{', '').replace('}', '')}"
#         f"&trusted_connection={os.getenv('DB_TRUSTED_CONN', 'yes')}"
#     )
#     engine = create_engine(conn_str)
#     with engine.connect() as conn:
#         df = pd.read_sql(text(query), conn, params=params)
#     return df


# SQL_FILE_MAP: Final[dict[str, str]] = {   
#     "NOTIONAL_INPUT": "sql/notional_input.sql",
#     "FLOW": "sql/flow.sql",
#     "ADJUSTMENTS": "sql/adjustments.sql",
#     "TRADES": "sql/trades.sql",
#     "PNL": "sql/pnl.sql",
#     "REF_DATA": "sql/ref_data.sql",
# }

# def get_io_source(source_key: str, sep: str = ",") -> IO:
#     match env:
#         case "prod":
#             sql_path = SQL_FILE_MAP.get(source_key)
#             class SQLReader(IO):
#                 def load_data(self) -> pd.DataFrame:
#                     return get_database(sql_path)
#             return SQLReader()

#         case "test":
#             CSV_FILE_MAP: Final[dict[str, str]] = {
#                 "NOTIONAL_INPUT": os.getenv("CSV_NOTIONAL_INPUT"),
#                 "FLOW": os.getenv("CSV_FLOW"),
#                 "ADJUSTMENTS": os.getenv("CSV_ADJUSTMENTS"),
#                 "TRADES": os.getenv("CSV_TRADES"),
#                 "PNL": os.getenv("CSV_PNL"),
#                 "REF_DATA": os.getenv("CSV_REF_DATA"),
#             }
#             csv_path = CSV_FILE_MAP.get(source_key)
#             if not csv_path:
#                 click.echo(f"CSV path for {source_key} not set", err=True)
#                 sys.exit(1)
#             return CSVReader(Path(csv_path), sep=sep)

#         case _:
#             click.echo(f"Unknown ENVIRONMENT: {env}", err=True)
#             sys.exit(1)




from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final
import os
import pandas as pd
import click
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
env = os.getenv("ENVIRONMENT")
load_dotenv(dotenv_path=f".env_{env}", override=True) 
print(f"Environment: {env}")

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
    
# def get_database(file_path: str, client=None, strategy=None, date_start=None, date_end=None) -> pd.DataFrame:
#     print(f"\n--- Executing SQL from file: {file_path}")

#     # Read the SQL query and format with parameters
#     with open(file_path, "r") as f:
#         query = f.read()
    
#     query = query.format(
#         client=f"'{client}'",
#         strategy=f"'{strategy}'",
#         date_start=f"'{date_start}'",
#         date_end=f"'{date_end}'"
#     )

#     conn_str = (
#         f"mssql+pyodbc://{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
#         f"?driver={os.getenv('DB_DRIVER').replace('{', '').replace('}', '')}"
#         f"&trusted_connection={os.getenv('DB_TRUSTED_CONN', 'yes')}"
#     )

#     engine = create_engine(conn_str)

#     with engine.connect() as conn:
#         df = pd.read_sql(query, conn)
#     return df
    

def get_database(file_path: str,client=None, strategy=None, date_start=None, date_end=None) -> pd.DataFrame:
    with open(file_path, "r") as f:
        query = f.read()
    query = query.format(
        client=f"'{client}'",
        strategy=f"'{strategy}'",
        date_start=f"'{date_start}'",
        date_end=f"'{date_end}'"
    )  
    conn_str = (
        f"mssql+pyodbc://{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}"
        f"?driver={os.getenv('DB_DRIVER').replace('{', '').replace('}', '')}"
        f"&trusted_connection={os.getenv('DB_TRUSTED_CONN', 'yes')}"
    )
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df    


SQL_FILE_MAP: Final[dict[str, str]] = {   
    "NOTIONAL_INPUT": "sql/notional_input.sql",
    "FLOW": "sql/flow.sql",
    "ADJUSTMENTS": "sql/adjustments.sql",
    "TRADES": "sql/trades.sql", 
    "PNL": "sql/pnl.sql",
    "REF_DATA": "sql/ref_data.sql",
}

def get_io_source(source_key: str, client=None, strategy=None, date_start=None, date_end=None, sep: str = ",") -> IO:
    match env:
        case "prod":
            sql_path = SQL_FILE_MAP.get(source_key)
            class SQLReader(IO):
                def load_data(self) -> pd.DataFrame:
                    return get_database(
                            sql_path,
                            client=client,
                            strategy=strategy,
                            date_start=date_start,
                            date_end=date_end
                        )
            return SQLReader()

        case "test":
            CSV_FILE_MAP: Final[dict[str, str]] = {
                "NOTIONAL_INPUT": os.getenv("CSV_NOTIONAL_INPUT"),
                "FLOW": os.getenv("CSV_FLOW"),
                "ADJUSTMENTS": os.getenv("CSV_ADJUSTMENTS"),
                "TRADES": os.getenv("CSV_TRADES"),
                "PNL": os.getenv("CSV_PNL"),
                "REF_DATA": os.getenv("CSV_REF_DATA"),
            }
            csv_path = CSV_FILE_MAP.get(source_key)
            if not csv_path:
                click.echo(f"CSV path for {source_key} not set", err=True)
                sys.exit(1)
            return CSVReader(Path(csv_path), sep=sep)

        case _:
            click.echo(f"Unknown ENVIRONMENT: {env}", err=True)
            sys.exit(1)
