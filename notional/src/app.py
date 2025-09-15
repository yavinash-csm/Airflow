import os
import click
import pandas as pd
from functools import reduce
from iointerface import get_io_source

@click.group()
def cli():
    """Notionals CLI"""
    pass

environment = os.getenv("ENVIRONMENT")
@cli.command("compare_notionals")
@click.argument("client")
@click.argument("strategy")
@click.argument("date_start")
@click.argument("date_end")
def compare_notionals(client, strategy, date_start, date_end):
    def formating_date(reader, date_col="asofdate"):
        df = reader.load_data()
        df.columns = df.columns.str.strip().str.replace("\xa0", "", regex=True)
        df = df.rename(columns={date_col: "asofdate"})
        df["asofdate"] = pd.to_datetime(
            df["asofdate"], errors="coerce", dayfirst=(environment == "test")
        ).dt.strftime("%Y-%m-%d")
        return df

    files_with_dates = [
        ("NOTIONAL_INPUT", "asofdate"),
        ("FLOW", "date"),
        ("ADJUSTMENTS", "asofdate"),
        ("TRADES", "asofdate"),
        ("PNL", "asofdate"),
    ]

    df_list = list(
        map(
            lambda f: formating_date(
                get_io_source(f[0], client=client, strategy=strategy, date_start=date_start, date_end=date_end), 
                f[1]
            ),
            files_with_dates
        )
    )

    ref_data = get_io_source("REF_DATA", client=client).load_data()
    commission_variable = ref_data["cmmsnInclude"].iloc[0]
    interest_variable = ref_data["interestInclude"].iloc[0]

    merged_df = reduce(lambda l, r: pd.merge(l, r, on="asofdate", how="left"), df_list)
    merged_df = merged_df.sort_values(by="asofdate").reset_index(drop=True)
    merged_df = merged_df.drop_duplicates(subset=['asofdate'], keep='last')
    merged_df["notional_end"] = merged_df["notional_end"].shift(1)
    merged_df = merged_df[1:]
    merged_df.set_index("asofdate", inplace=True)
    merged_df = merged_df.fillna(0)

    cols_to_convert = ["notional_end", "flow", "int_adj", "pnl", "com_adj", "commsn"]
    merged_df[cols_to_convert] = (
        merged_df[cols_to_convert]
        .replace({r',': '', r'\((.*?)\)': r'-\1'}, regex=True)
        .apply(pd.to_numeric, errors='coerce')
    )

    merged_df["notional_output"] = (
        merged_df["notional_end"]  
        + merged_df["flow"]              
        + merged_df["com_adj"] * commission_variable  
        + merged_df["int_adj"] * interest_variable  
        - merged_df["commsn"] * commission_variable  
        + merged_df["pnl"]
    )

    merged_df = merged_df[merged_df.index.notna()]
    #print(merged_df["notional_output"])
    print(merged_df["notional_output"].to_json())


if __name__ == "__main__":
    cli()



#old
# @cli.command("compare_notionals")
# def compare_notionals():
#     def formating_date(reader,date_col="asofdate"):
#         df = reader.load_data()
#         df.columns = df.columns.str.strip().str.replace("\xa0", "", regex=True) 
#         df = df.rename(columns={date_col: "asofdate"})
#         df["asofdate"] = pd.to_datetime(df["asofdate"], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
#         return df

#     files_with_dates = [
#     ("NOTIONAL_INPUT", "asofdate"),
#         ("FLOW", "resetdate"),
#         ("ADJUSTMENTS", "asofdate"),
#         ("TRADES", "asofdate"),
#         ("PNL", "asofdate"),
# ]
#     df_list = list(map(lambda f: formating_date(get_io_source(f[0]), f[1]),files_with_dates))
#     ref_data = get_io_source("REF_DATA").load_data()
#     commission_variable = ref_data["com_include"].iloc[0]
#     interest_variable = ref_data["int_include"].iloc[0]
#     merged_df = reduce(lambda l, r: pd.merge(l, r, on="asofdate", how="left"), df_list)
#     merged_df["notional"] = merged_df["notional"].shift(1)
#     merged_df = merged_df[1:] 
#     merged_df.set_index("asofdate", inplace=True)
#     merged_df = merged_df.fillna(0)
#     cols_to_convert = ["notional", "flow", "int_adj", "pnl", "com_adj", "com_trade"]
#     merged_df[cols_to_convert] = (
#         merged_df[cols_to_convert]
#         .replace({r',': '', r'\((.*?)\)': r'-\1'}, regex=True)
#         .apply(pd.to_numeric, errors='coerce')
#     )
    
#     merged_df["notional_output"] = (
#     merged_df["notional"]  
#     + merged_df["flow"]              
#     + merged_df["com_adj"] * commission_variable  
#     + merged_df["int_adj"] * interest_variable  
#     - merged_df["com_trade"] * commission_variable  
#     + merged_df["pnl"]         
# )
#     merged_df = merged_df[merged_df.index.notna()]
#     print(merged_df["notional_output"].to_json())




#prod
# def compare_notionals(client, strategy, date_start, date_end):
#     def formating_date(reader, date_col="asofdate"):
#         df = reader.load_data()
#         df.columns = df.columns.str.strip().str.replace("\xa0", "", regex=True)
#         df = df.rename(columns={date_col: "asofdate"})
#         df["asofdate"] = pd.to_datetime(df["asofdate"], errors="coerce").dt.strftime("%Y-%m-%d")
#         return df

#     files_with_dates = [
#         ("NOTIONAL_INPUT", "asofdate"),
#         ("FLOW", "date"),
#         ("ADJUSTMENTS", "asofdate"),
#         ("TRADES", "asofdate"),
#         ("PNL", "asofdate"),
#     ]
#     df_list = list(
#         map(
#             lambda f: formating_date(
#                 get_io_source(f[0], client=client, strategy=strategy, date_start=date_start, date_end=date_end), 
#                 f[1]
#             ),
#             files_with_dates
#         )
#     )
#     ref_data = get_io_source("REF_DATA", client=client).load_data()
#     commission_variable = ref_data["cmmsnInclude"].iloc[0]
#     interest_variable = ref_data["interestInclude"].iloc[0]
#     merged_df = reduce(lambda l, r: pd.merge(l, r, on="asofdate", how="outer"), df_list)
#     merged_df = merged_df.sort_values(by="asofdate").reset_index(drop=True)
#     merged_df = merged_df.drop_duplicates(subset=['asofdate'], keep='last')
#     merged_df["notional_end"] = merged_df["notional_end"].shift(1)
#     merged_df = merged_df[1:]
#     merged_df.set_index("asofdate", inplace=True)
#     merged_df = merged_df.fillna(0)
#     cols_to_convert = ["notional_end", "flow", "int_adj", "pnl", "com_adj", "commsn"]
#     merged_df[cols_to_convert] = (
#         merged_df[cols_to_convert]
#         .replace({r',': '', r'\((.*?)\)': r'-\1'}, regex=True)
#         .apply(pd.to_numeric, errors='coerce')
#     )
#     merged_df["notional_output"] = (
#         merged_df["notional_end"]  
#         + merged_df["flow"]              
#         + merged_df["com_adj"] * commission_variable  
#         + merged_df["int_adj"] * interest_variable  
#         - merged_df["commsn"] * commission_variable  
#         + merged_df["pnl"]
#     )
#     merged_df = merged_df[merged_df.index.notna()]
#     print(merged_df["notional_output"])
#     print("\nJSON Output of 'notional_output':")
#     print(merged_df["notional_output"].to_json())



#test
# def compare_notionals(client, strategy, date_start, date_end):
#     def formating_date(reader,date_col="asofdate"):
#         df = reader.load_data()
#         print(df)
#         df.columns = df.columns.str.strip().str.replace("\xa0", "", regex=True) 
#         df = df.rename(columns={date_col: "asofdate"})
#         df["asofdate"] = pd.to_datetime(df["asofdate"], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
#         return df

#     files_with_dates = [
#     ("NOTIONAL_INPUT", "asofdate"),
#         ("FLOW", "date"),
#         ("ADJUSTMENTS", "asofdate"),
#         ("TRADES", "asofdate"),
#         ("PNL", "asofdate"),
# ]
#     df_list = list(map(lambda f: formating_date(get_io_source(f[0],client=client,strategy=strategy,date_start=date_start,date_end=date_end), f[1]),files_with_dates))
#     ref_data = get_io_source("REF_DATA",client=client,).load_data()
#     commission_variable = ref_data["cmmsnInclude"].iloc[0]
#     interest_variable = ref_data["interestInclude"].iloc[0]
#     merged_df = reduce(lambda l, r: pd.merge(l, r, on="asofdate", how="outer"), df_list)
#     merged_df = merged_df.drop_duplicates(subset=['asofdate'], keep='last')
#     merged_df["notional_end"] = merged_df["notional_end"].shift(1)
#     merged_df = merged_df[1:] 
#     merged_df.set_index("asofdate", inplace=True)
#     merged_df = merged_df.fillna(0)
#     cols_to_convert = ["notional_end", "flow", "int_adj", "pnl", "com_adj", "commsn"]
#     merged_df[cols_to_convert] = (
#         merged_df[cols_to_convert]
#         .replace({r',': '', r'\((.*?)\)': r'-\1'}, regex=True)
#         .apply(pd.to_numeric, errors='coerce')
#     )
    
#     merged_df["notional_output"] = (
#     merged_df["notional_end"]  
#     + merged_df["flow"]              
#     + merged_df["com_adj"] * commission_variable  
#     + merged_df["int_adj"] * interest_variable  
#     - merged_df["commsn"] * commission_variable  
#     + merged_df["pnl"]         
# )
#     print(merged_df)
#     merged_df = merged_df[merged_df.index.notna()]
#     print(merged_df["notional_output"].to_json())