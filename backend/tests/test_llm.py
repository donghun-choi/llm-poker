import pytest

from backend.llm.response_parser import parse_json_response, validate_action
from backend.engine.betting import Action


def test_parse_json_with_extra_text():
    raw = "Sure! {\"action\": \"call\", \"amount\": null, \"reasoning\": \"call\"} thanks"
    parsed = parse_json_response(raw)
    assert parsed["action"] == "call"


def test_validate_action_clamps_raise_and_call():
    parsed = {"action": "raise", "amount": 5, "reasoning": "test"}
    action = validate_action(parsed, ["call", "raise", "fold"], call_amount=20, min_raise=10, stack=25)
    assert action.action == "raise"
    assert action.amount == 25  # all-in because stack is 25 and min raise makes 30

    parsed_call = {"action": "call", "amount": 100}
    call_action = validate_action(parsed_call, ["call", "raise", "fold"], call_amount=15, min_raise=5, stack=10)
    assert call_action.amount == 10  # capped to stack


def test_invalid_action_falls_back_to_fold():
    parsed = {"action": "dance"}
    action = validate_action(parsed, ["call", "raise"], call_amount=0, min_raise=0, stack=10)
    assert action.action == "fold"
