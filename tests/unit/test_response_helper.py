"""Tests for the shared response helper."""

from app.utils.response_helper import build_error_response, build_success_response


def test_build_success_response_has_ok_true():
    result = build_success_response({"value": 42})
    assert result["ok"] is True


def test_build_success_response_contains_data():
    result = build_success_response({"value": 42})
    assert result["data"] == {"value": 42}


def test_build_success_response_with_empty_data():
    result = build_success_response({})
    assert result["ok"] is True
    assert result["data"] == {}


def test_build_error_response_has_ok_false():
    result = build_error_response("something went wrong")
    assert result["ok"] is False


def test_build_error_response_contains_message():
    result = build_error_response("something went wrong")
    assert result["error"] == "something went wrong"


def test_build_error_response_with_empty_string():
    result = build_error_response("")
    assert result["ok"] is False
    assert result["error"] == ""
