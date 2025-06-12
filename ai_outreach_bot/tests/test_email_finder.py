# ruff: noqa: E402
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_outreach_bot.src import email_finder


def test_guess_pattern():
    email = email_finder.guess_pattern("John Doe", "example.com")
    assert email == "john.doe@example.com"


def test_from_page():
    html = "<html>Contact john.doe@example.com</html>"
    email = email_finder.from_page(html, "example.com")
    assert email == "john.doe@example.com"
