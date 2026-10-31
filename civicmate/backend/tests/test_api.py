from fastapi.testclient import TestClient
from backend.app.main import app
client=TestClient(app)

def test_health():
    r=client.get('/api/health')
    assert r.status_code==200 and r.json()['status']=='ok'

def test_sample_schemes():
    r=client.get('/api/schemes/sample')
    assert r.status_code==200 and len(r.json())>=2

def test_invalid_profile_rejected():
    r=client.post('/api/summarize',data={'profile':'{"name":"A","annual_income":0,"state":"Tamil Nadu"}','scheme_id':'PMAY'})
    assert r.status_code==422

def test_execution_waits_for_approval_and_never_marks_submitted(monkeypatch):
    from backend.app import main
    async def fake_prepare(profile, sid):
        from backend.app.models import AgentStep
        return [AgentStep(step_number=1, action='Mock form populated', status='ok')], '/tmp/preview.png'
    async def fake_finalize(profile, sid, receipt_reference):
        return [], '/tmp/receipt.png'
    monkeypatch.setattr(main, 'prepare_execution', fake_prepare)
    monkeypatch.setattr(main, 'finalize_demo_receipt', fake_finalize)
    payload={'profile':{'name':'Arun','annual_income':200000,'state':'Tamil Nadu','category':'General','preferred_language':'Tamil'},'scheme_name':'PMAY','eligible':True}
    started=client.post('/api/execute-form',json=payload)
    assert started.status_code==200
    session=started.json()
    assert session['status']=='awaiting_approval'
    assert session['submitted'] is False
    sid=session['session_id']
    approved=client.post(f'/api/execute-form/{sid}/confirm',data={'approve':'true'})
    assert approved.status_code==200
    assert approved.json()['session']['status']=='completed'
    assert approved.json()['session']['submitted'] is False
    duplicate=client.post(f'/api/execute-form/{sid}/confirm',data={'approve':'true'})
    assert duplicate.status_code==409
    client.delete(f'/api/sessions/{sid}')

def test_ineligible_profile_cannot_launch_agent():
    payload={'profile':{'name':'Arun','annual_income':5000000,'state':'Tamil Nadu'},'scheme_name':'PMAY','eligible':False}
    assert client.post('/api/execute-form',json=payload).status_code==403
