import os
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env_test", override=True)

from app import cli
def test_short_strats_without_positive_positions():
    os.environ["CSV_PATH"] = "csv/jam_positions.csv"  
    runner = CliRunner()
    result = runner.invoke(cli, ["short_strats"])
    assert result.output == "True\n"
