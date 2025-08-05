import os
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env_test", override=True)


from app import cli 
def test_neg_checker_with_positive_data():
    os.environ["CSV_PATH"] = "csv/jam_positions_positive.csv"  
    print("Testing with positive data from:", os.environ["CSV_PATH"])
    runner = CliRunner()
    result = runner.invoke(cli, ["neg_checker"])
    #print("-------->", result.output)
    assert result.output == "True\n"
