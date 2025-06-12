# ruff: noqa: E402
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_outreach_bot.src import gpt_filter


def test_filter_candidates(mocker):
    mock_client = mocker.patch("ai_outreach_bot.src.gpt_filter.OpenAI")
    instance = mock_client.return_value
    instance.chat.completions.create.return_value.choices = [
        mocker.MagicMock(
            message=mocker.MagicMock(
                content='[{"name": "A", "reason": "LLM", "confidence": 0.9}]'
            )
        )
    ]
    result = gpt_filter.filter_candidates("Lab", [])
    assert result == [{"name": "A", "reason": "LLM", "confidence": 0.9}]
