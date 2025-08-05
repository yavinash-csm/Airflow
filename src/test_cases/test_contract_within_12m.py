import os
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env_test", override=True)

from app import cli
def test_contracts_within_12_months():
    os.environ["CSV_PATH_CON"] = "csv/TradeReqs.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["contract_req"])
    assert result.output == "True\n"
