import asyncio, uuid, hashlib, time
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import UserProfile, Language, SchemeSummary, ExecutionSession, AgentStep, ExecuteRequest
from .ai_service import extract_text, summarize_policy, apply_income_gate
from .agent_service import prepare_execution, finalize_demo_receipt
from .config import SAMPLE_DIR, MAX_UPLOAD_BYTES

app=FastAPI(title='CivicMate API', version='1.0.0', description='Local civic scheme explainer and mock-portal demo')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:8501','http://127.0.0.1:8501'], allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['*'])
SESSIONS: dict[str, ExecutionSession] = {}
ANALYSES: dict[str, SchemeSummary] = {}

@app.get('/api/health')
def health():
    try:
        import playwright
        pw=True
    except Exception: pw=False
    from .config import GEMINI_API_KEY
    return {'status':'ok','playwright_ready':pw,'gemini_configured':bool(GEMINI_API_KEY and GEMINI_API_KEY!='replace_me'), 'mode':'gemini' if GEMINI_API_KEY and GEMINI_API_KEY!='replace_me' else 'offline_fallback'}

@app.get('/api/schemes/sample')
def sample_schemes():
    import json
    data=json.loads((SAMPLE_DIR/'schemes.json').read_text(encoding='utf-8'))
    return [{'id':k,'name':v['name'],'income_cap':v.get('income_cap'),'description':v['description']} for k,v in data.items()]

@app.post('/api/summarize')
async def summarize(profile: str = Form(...), scheme_id: str = Form('PMAY'), file: UploadFile | None = File(default=None), policy_text: str | None = Form(default=None)):
    try: user=UserProfile.model_validate_json(profile)
    except Exception as e: raise HTTPException(422, detail=str(e))
    text=policy_text or ''
    if file:
        if Path(file.filename or '').suffix.lower() not in {'.pdf','.txt'}:
            raise HTTPException(400, detail='Invalid file format. Please upload a PDF or TXT file.')
        content=await file.read()
        if len(content)>MAX_UPLOAD_BYTES: raise HTTPException(413, detail='Please upload a document under 10 MB.')
        try: text=extract_text(file.filename, content)
        except ValueError as e: raise HTTPException(400, detail=str(e))
        except Exception as e: raise HTTPException(400, detail=f'Could not read document: {e}')
    summary, offline=summarize_policy(scheme_id, user.preferred_language, text)
    summary=apply_income_gate(summary, user.annual_income)
    analysis_id=str(uuid.uuid4())
    ANALYSES[analysis_id]=summary
    return {'analysis_id':analysis_id,'summary':summary.model_dump(),'mode':'offline_fallback' if offline else 'gemini'}

@app.post('/api/execute-form')
async def execute_form(payload: ExecuteRequest):
    if not payload.eligible: raise HTTPException(403, detail='Applicant is ineligible; automation is blocked.')
    sid=str(uuid.uuid4())
    session=ExecutionSession(session_id=sid,user_profile=payload.profile,scheme_name=payload.scheme_name,status='filling')
    SESSIONS[sid]=session
    try:
        steps,shot=await prepare_execution(payload.profile,sid)
        session.trace_log=steps
        session.screenshot_path=shot
        session.status='awaiting_approval'
        session.trace_log.append(AgentStep(step_number=len(session.trace_log)+1,action='Human approval gate reached; awaiting citizen decision',status='awaiting_approval'))
        return session.model_dump()
    except Exception as e:
        session.status='failed'
        session.trace_log.append(AgentStep(step_number=len(session.trace_log)+1,action=f'Automation stopped safely: {e}',status='failed'))
        raise HTTPException(504, detail=str(e))

@app.post('/api/execute-form/{session_id}/confirm')
async def confirm_execution(session_id: str, approve: bool = Form(...)):
    session=SESSIONS.get(session_id)
    if not session: raise HTTPException(404, detail='Session not found or expired.')
    if session.status=='completed': raise HTTPException(409, detail='Form submission already processed for this session.')
    if session.status!='awaiting_approval': raise HTTPException(409, detail='Session is not waiting for approval.')
    if not approve:
        session.status='failed'
        session.trace_log.append(AgentStep(step_number=len(session.trace_log)+1,action='Citizen cancelled the local demo execution',status='cancelled'))
        return {'session':session.model_dump(),'message':'Execution cancelled. No submission was made.'}
    try:
        receipt_ref=hashlib.sha256(f'{session_id}:{time.time_ns()}'.encode()).hexdigest()[:16].upper()
        steps,shot=await finalize_demo_receipt(session.user_profile,session_id,receipt_ref)
        session.trace_log.extend(steps)
        session.screenshot_path=shot
        session.status='completed'
        session.submitted=False  # Deliberately never represents a government submission.
        session.receipt_reference=receipt_ref
        session.trace_log.append(AgentStep(step_number=len(session.trace_log)+1,action='Local visual receipt generated after explicit approval; no government form submitted',status='completed'))
        return {'session':session.model_dump(),'receipt_url':f'/api/receipts/{session_id}','receipt_reference':session.receipt_reference,'message':'Local demo receipt generated. No government application was submitted.'}
    except Exception as e:
        session.status='failed'
        raise HTTPException(500, detail=f'Receipt generation failed: {e}')

@app.get('/api/sessions/{session_id}')
def get_session(session_id: str):
    s=SESSIONS.get(session_id)
    if not s: raise HTTPException(404, detail='Session not found or expired.')
    return s.model_dump()

@app.get('/api/receipts/{session_id}')
def get_receipt(session_id: str):
    s=SESSIONS.get(session_id)
    if not s or s.status!='completed' or not s.screenshot_path: raise HTTPException(404, detail='Receipt not available.')
    p=Path(s.screenshot_path)
    if not p.exists(): raise HTTPException(404, detail='Receipt file not found.')
    return FileResponse(p, media_type='image/png', filename=f'receipt_{session_id}.png')

@app.delete('/api/sessions/{session_id}')
def delete_session(session_id: str):
    s=SESSIONS.pop(session_id,None)
    if not s: raise HTTPException(404, detail='Session not found.')
    for p in [s.screenshot_path, str(SAMPLE_DIR.parent/'receipts'/f'preview_{session_id}.png'), str(SAMPLE_DIR.parent/'receipts'/f'receipt_{session_id}.png')]:
        if p:
            try: Path(p).unlink(missing_ok=True)
            except Exception: pass
    return {'deleted':True}
