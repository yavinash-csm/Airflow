import os
import pandas as pd
import json
from click.testing import CliRunner
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env_test", override=True)
from app import cli

def test_compare_notionals_diff_with_test_case():
    notional_input = os.getenv("CSV_NOTIONAL_INPUT")
    notional_input = pd.read_csv(notional_input)
    notional_input['notional_end'] = notional_input['notional_end'].astype(str).str.replace(',', '').str.strip().astype(float)
    notional_input['asofdate'] = pd.to_datetime(notional_input['asofdate'], dayfirst=True).dt.strftime('%Y-%m-%d')
    test_case = os.getenv("CSV_TEST_CASE")
    test_case = pd.read_csv(test_case)
    runner = CliRunner()
    result = runner.invoke(cli, ["compare_notionals","BOEING", "OYDLS", "2025-06-01", "2025-06-30"])
    output_json = json.loads(result.output)
    print("Output:", result.output)
    output_json = pd.DataFrame({"asofdate": list(output_json.keys()),"notional_output": list(output_json.values())})
    output_json['notional_output'] = output_json['notional_output'].astype(str).str.replace(',', '').str.strip().astype(float)
    merged_df = pd.merge(output_json, notional_input, on='asofdate')
    # print(merged_df)
    merged_df['difference'] = merged_df['notional_output'] - merged_df['notional_end']
    pd.testing.assert_series_equal(
        merged_df['difference'].reset_index(drop=True),
        test_case['difference'].reset_index(drop=True),
    )