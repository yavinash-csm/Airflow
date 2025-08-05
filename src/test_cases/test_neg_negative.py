import os
from click.testing import CliRunner
from dotenv import load_dotenv
    
load_dotenv(dotenv_path=".env_test", override=True)

from app import cli
def test_neg_checker_with_negative_data():
    os.environ["CSV_PATH"] = "csv/jam_positions.csv" 
    runner = CliRunner()
    result = runner.invoke(cli, ["neg_checker"])
    print("-------->", result.output) 
    assert result.output == "False\n"