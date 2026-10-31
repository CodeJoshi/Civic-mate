import pytest
from pydantic import ValidationError
from backend.app.models import UserProfile, Language, SchemeSummary
from backend.app.ai_service import apply_income_gate, _offline_summary

def test_income_must_be_positive():
    with pytest.raises(ValidationError):
        UserProfile(name='Arun',annual_income=0,state='Tamil Nadu')
    with pytest.raises(ValidationError):
        UserProfile(name='Arun',annual_income=-1,state='Tamil Nadu')

def test_income_gate_blocks_over_cap():
    summary=SchemeSummary(scheme_name='PMAY',eligibility_bullets=['a','b','c'],income_cap=300000,eligible=True)
    assert apply_income_gate(summary,5000000).eligible is False

def test_income_gate_allows_under_cap():
    summary=SchemeSummary(scheme_name='PMAY',eligibility_bullets=['a','b','c'],income_cap=300000,eligible=True)
    assert apply_income_gate(summary,200000).eligible is True

def test_offline_tamil_has_three_bullets():
    summary=_offline_summary('PMAY',Language.TAMIL)
    assert len(summary.eligibility_bullets)==3
    assert summary.income_cap==300000
