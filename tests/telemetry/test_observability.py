import pytest
from src.telemetry.retries import with_db_retry, NonRetryableException
from requests.exceptions import Timeout
from unittest.mock import MagicMock

# Mocking a basic Celery task structure
class MockTask:
    def __init__(self, name="mock_task"):
        self.name = name
        self.request = MagicMock()
        self.request.id = "123"
        self.request.retries = 0
        self.retry = MagicMock(side_effect=Exception("TaskRetriedDelay"))
        self.update_state = MagicMock()

def test_non_retryable_exception():
    @with_db_retry(max_retries=3)
    def failing_task(self):
        raise NonRetryableException("This is completely malformed.")
        
    task = MockTask()
    with pytest.raises(NonRetryableException):
        failing_task(task)
        
    # Validates it updated state directly to FAILURE vs letting celery queue
    assert task.update_state.called
    args, kwargs = task.update_state.call_args
    assert kwargs["state"] == "FAILURE"

def test_retryable_HTTP_timeout():
    @with_db_retry(max_retries=3)
    def crashing_task(self):
        raise Timeout("Network went to sleep.")
        
    task = MockTask()
    with pytest.raises(Exception, match="TaskRetriedDelay"):
        crashing_task(task)
        
    # Validates it pushed back to the broker properly bypassing the hard drop
    assert task.retry.called
    args, kwargs = task.retry.call_args
    assert isinstance(kwargs["exc"], Timeout)

def test_unexpected_exception():
    @with_db_retry(max_retries=3)
    def unpredictable_task(self):
        raise ValueError("Division by zero etc.")
        
    task = MockTask()
    with pytest.raises(Exception, match="TaskRetriedDelay"):
        unpredictable_task(task)
        
    assert task.retry.called
    args, kwargs = task.retry.call_args
    # Confirms it is only allowing one safe retry instead of max exponentially
    assert kwargs["max_retries"] == 1
