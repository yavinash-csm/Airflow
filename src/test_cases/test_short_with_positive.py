import os
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env_test", override=True)

from app import cli
def test_short_strats_with_positive_positions():
    os.environ["CSV_PATH"] = "csv/test_short_positive.csv"  
    runner = CliRunner()
    result = runner.invoke(cli, ["short_strats"])
    assert result.output == "False\n"
