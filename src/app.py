from __future__ import annotations
from iointerface import get_io_source
import sys
from typing import Final
import click
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

env = os.getenv("ENVIRONMENT","prod") 
load_dotenv(dotenv_path=f".env_{env}", override=True) 

REQUIRED_COLS: Final[list[str]] = [
    "AsofDate", "client", "strategy", "ticker",
    "monthCode", "yearCode", "pstn",
]
GROUP_COLS: Final[list[str]] = REQUIRED_COLS[:-1]
ALLOWED_STRATS: Final[set[str]] = {"OY", "OYFAR", "FAREQH", "CUSTOM1"}

LOG: Final[dict[str, object]] = {
    "process_name":   "LoadAPGIndex.pl",
    "process_path":   "/apps/jam/etc/batchjobs/LoadAPGIndex.pl",
    "run_by":         "jam",
    "run_date":       "12/06/25 00:00",
    "exit_code":      1,
    "exit_msg":       "Job Started",
    "log_file":       "/logs/jam/logs/LoadAPGIndex.pl.0612",
    "output_file":    "",
    "data":           "",
    "business_day":   "12/06/2025",
    "host_name":      "pd-vsl-app-01.core.corp",
    "job_step":       0,
    "start_time":     "12/06/25 17:14",
    "end_time":       "12/06/25 17:14",
    "records_input":  0,
    "records_loaded": 0,
    "records_error":  0,
}

def select_required(df: pd.DataFrame) -> pd.DataFrame:
    return df[REQUIRED_COLS]

def exclude_strategies(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["strategy"] != "FARRMF"]
    mask = (
        df["strategy"].str.contains("SHORT", case=False, na=False)
        | df["strategy"].isin(ALLOWED_STRATS)
    )
    return df[~mask]

def group_and_sum(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(GROUP_COLS, as_index=False, sort=False)["pstn"].sum()

def keep_negatives(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["pstn"] < 0]

# ─────────────────────── CLI ───────────────────────────── #
@click.group()
def cli():
    """Multi‑script driver.  Run `python app.py --help` to list jobs."""
    pass

@cli.command("neg_checker")
def negative_position_checker():
    try:
        reader = get_io_source("NEG_CHECKER_TABLE")
        df = (
            reader.load_data()
                  .pipe(select_required)
                  .pipe(exclude_strategies)
                  .pipe(group_and_sum)
                  .pipe(keep_negatives)
        )
    except Exception as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)
    click.echo(df.empty)

def dup_checker(df: pd.DataFrame) -> bool:
    dup_cols = [
        "AsofDate", "Client", "Strategy", "Symbol",
        "SecType", "Contract", "Short", "Long", "account"
    ]
    return df[df.duplicated(subset=dup_cols, keep=False)]

@cli.command("dup_req")
def dup_req():
    try:
        reader = get_io_source("DUP_REQ_TABLE")
        has_duplicates = (
            reader.load_data()
                  .pipe(dup_checker)  
        )
    except Exception as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)
    click.echo(has_duplicates.empty)

def filter_today(df: pd.DataFrame) -> pd.DataFrame:
    today = pd.Timestamp.today().strftime("%Y%m%d")
    return df[df["AsofDate"].astype(str) == today]

def filter_trade_type(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["tradeType"].isin(["Futures", "LME"])]

def filter_beta_shorts(df: pd.DataFrame) -> pd.DataFrame:
    beta_shorts = {"FARRMF", "FEQSHORT", "DEQSHORT", "LSFSHORT"}
    return df[df["strategy"].isin(beta_shorts)]

def group_by_strategy_ticker(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["strategy", "ticker"], as_index=False)["pstn"].sum()

def keep_positive(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["pstn"] > 0]

@cli.command("short_strats")
def short_strategies_checker():
    try:
        reader = get_io_source("SHORT_STRATS_TABLE")
        df = (
            reader.load_data()
                  .pipe(filter_today)
                  .pipe(filter_trade_type)
                  .pipe(filter_beta_shorts)
                  .pipe(group_by_strategy_ticker)
                  .pipe(keep_positive)
        )
        click.echo(df.empty)    

    except Exception as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)
    

MONTH_CODE_MAP = {
    'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
    'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12
}

def contract_duration_check(df: pd.DataFrame) -> bool:
    today = datetime.today()
    max_allowed = today + relativedelta(months=12)
    def parse_contract_month(contract_code: str) -> datetime | None:
        try:
            code = contract_code[-3:]
            month_char = code[0].upper()
            year_suffix = int(code[1:])
            month = MONTH_CODE_MAP.get(month_char)
            year = 2000 + year_suffix if year_suffix < 50 else 1900 + year_suffix
            return datetime(year, month, 1)
        except Exception as e:
            raise ValueError(f"Invalid contract code '{contract_code}': {e}")
    contract_dates = df["Contract"].astype(str).apply(parse_contract_month)
    return all(asofdate <= max_allowed for asofdate in contract_dates)

@cli.command("contract_req")
def cContractDurationReq():
    try:
        reader = get_io_source("CONTRACT_REQ_TABLE",sep="\t")
        df = reader.load_data().pipe(contract_duration_check)
        click.echo(df)
    except Exception as exc:
        click.echo(f"ERROR: {exc}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
