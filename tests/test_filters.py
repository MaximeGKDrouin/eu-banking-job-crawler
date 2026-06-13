import pytest
from datetime import datetime
from pipeline.filters import JobFilterEngine

@pytest.fixture
def filter_engine():
    return JobFilterEngine()

def test_location_filtering(filter_engine):
    assert filter_engine.match_location("London, Greater London") == "London"
    assert filter_engine.match_location("Paris, France") == "Paris"
    assert filter_engine.match_location("New York, NY") is None

def test_division_filtering(filter_engine):
    assert filter_engine.match_division("M&A Summer Analyst") == "Investment Banking"
    assert filter_engine.match_division("Equity Research Intern") == "Financial Markets"
    assert filter_engine.match_division("Operations Associate") is None

def test_temporal_window_validation(filter_engine):
    valid_start = datetime(2027, 4, 15)
    invalid_start = datetime(2026, 6, 1)
    
    assert filter_engine.verify_temporal_window(valid_start, None) is True
    assert filter_engine.verify_temporal_window(invalid_start, None) is False