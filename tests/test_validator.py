"""Tests for run_validators."""

import pytest
from resumeforge.validator import run_validators


class TestRunValidators:
    """Tests for the shared validation runner."""

    def test_all_checks_pass(self):
        """POSITIVE: no exception when all validators pass"""
        validators = [
            {"check": lambda x: x > 0, "message": "must be positive"},
            {"check": lambda x: x < 100, "message": "must be less than 100"},
        ]
        run_validators(validators, 50)  # should not raise

    def test_empty_validators_list(self):
        """POSITIVE: no exception with empty validator list"""
        run_validators([], "anything")

    def test_multiple_args_passed_to_check(self):
        """POSITIVE: multiple args are forwarded to check callable"""
        validators = [
            {"check": lambda a, b: a + b == 3, "message": "sum must be 3"},
        ]
        run_validators(validators, 1, 2)

    def test_first_failure_raises_valueerror(self):
        """NEGATIVE: first failing validator raises ValueError with its message"""
        validators = [
            {"check": lambda x: x > 0, "message": "must be positive"},
        ]
        with pytest.raises(ValueError, match="must be positive"):
            run_validators(validators, -1)

    def test_stops_at_first_failure(self):
        """NEGATIVE: second validator is not evaluated after first fails"""
        called = []
        validators = [
            {"check": lambda x: False, "message": "first fails"},
            {"check": lambda x: called.append(1) or True, "message": "second"},
        ]
        with pytest.raises(ValueError, match="first fails"):
            run_validators(validators, 1)
        assert called == []

    def test_second_validator_fails(self):
        """NEGATIVE: passes first check but fails second"""
        validators = [
            {"check": lambda x: x > 0, "message": "must be positive"},
            {"check": lambda x: x % 2 == 0, "message": "must be even"},
        ]
        with pytest.raises(ValueError, match="must be even"):
            run_validators(validators, 3)
