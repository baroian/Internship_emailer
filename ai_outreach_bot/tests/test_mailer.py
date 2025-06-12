# ruff: noqa: E402
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from unittest import mock

mock_openai = mock.MagicMock()
sys.modules["openai"] = mock.MagicMock(OpenAI=mock.MagicMock(return_value=mock_openai))

from ai_outreach_bot.src import mailer


def test_send_email(mocker):
    mocker.patch("ai_outreach_bot.src.mailer.generate_body", return_value="hi")
    smtp = mocker.patch("smtplib.SMTP")
    mailer.send_email(
        "John", "john@example.com", {"lab": "Lab", "paper_title": "Title"}
    )
    smtp.assert_called()
