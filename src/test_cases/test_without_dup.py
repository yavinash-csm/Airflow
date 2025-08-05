import os
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env_test", override=True)

from app import cli
def test_dup_checker_without_duplicates():
    os.environ["CSV_PATH_DUP"] = "csv/Book1.csv"
    runner = CliRunner()
    result = runner.invoke(cli, ["dup_req"])
    assert result.output == "True\n"
