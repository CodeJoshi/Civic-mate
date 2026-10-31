import os, requests, streamlit as st
from pathlib import Path
API=os.getenv('CIVICMATE_API','http://127.0.0.1:8000')
STATES=['Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal']
LANGUAGES=['Tamil','English','Hindi','Telugu','Marathi']
def api(method,path,**kwargs):
    try:
        r=requests.request(method,API+path,timeout=60,**kwargs)
        if not r.ok:
            try: detail=r.json().get('detail',r.text)
            except Exception: detail=r.text
            st.error(str(detail)); return None
        return r
    except requests.RequestException as e:
        st.error(f'Cannot reach CivicMate backend at {API}. Start FastAPI first. Details: {e}')
        return None

st.set_page_config(page_title='CivicMate | Scheme Assistant',page_icon='🏛️',layout='wide')
st.markdown('''<style>.block-container{padding-top:2rem}.hero{padding:1.4rem 1.6rem;border-radius:16px;background:linear-gradient(120deg,#102b4e,#1c527a);color:white;margin-bottom:1rem}.hero h1{margin:0;color:white}.hero p{margin:.35rem 0 0;color:#dbeafe}.small-muted{color:#64748b;font-size:.88rem}</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏛️ CivicMate</h1><p>மக்களுக்கான அரசுத் திட்டங்கள் · Understand schemes. Prepare with confidence.</p></div>',unsafe_allow_html=True)
health=api('GET','/api/health')
if health:
    h=health.json()
    if h['mode']=='offline_fallback': st.warning('🟠 Offline Fallback Mode active · Static regional summaries and local mock portal are enabled.')
    else: st.success('🟢 Gemini configured · Playwright service available')
    if not h.get('playwright_ready'): st.error('Playwright package unavailable. Install dependencies and Chromium browser.')

with st.sidebar:
    st.header('Preferences')
    language=st.selectbox('Regional language',LANGUAGES,index=0)
    st.caption('Automation mode is controlled by backend HEADLESS_MODE. Only the bundled local mock portal is supported.')
    schemes_resp=api('GET','/api/schemes/sample')
    schemes=schemes_resp.json() if schemes_resp else [{'id':'PMAY','name':'PMAY sample'}]
    scheme_names={x['name']:x['id'] for x in schemes}
    selected=st.selectbox('Choose a sample scheme',list(scheme_names))
    uploaded=st.file_uploader('Or upload scheme PDF / TXT (max 10 MB)',type=['pdf','txt'])

st.subheader('1 · Citizen profile')
with st.form('profile_form'):
    c1,c2=st.columns(2)
    name=c1.text_input('Full name',placeholder='Enter applicant name')
    income=c2.number_input('Annual household income (₹)',min_value=1.0,value=200000.0,step=1000.0)
    state=c1.selectbox('State',STATES,index=STATES.index('Tamil Nadu'))
    category=c2.selectbox('Social category',['General','OBC','SC','ST'])
    analyze=st.form_submit_button('✨ Analyze scheme eligibility',type='primary',use_container_width=True)
if analyze:
    if len(name.strip())<2: st.error('Please enter a name with at least 2 characters.')
    else:
        profile={'name':name.strip(),'annual_income':income,'state':state,'category':category,'preferred_language':language}
        files={'file':(uploaded.name,uploaded.getvalue(),uploaded.type or 'application/octet-stream')} if uploaded else None
        data={'profile':__import__('json').dumps(profile),'scheme_id':scheme_names[selected]}
        r=api('POST','/api/summarize',data=data,files=files)
        if r:
            st.session_state.analysis=r.json(); st.session_state.profile=profile; st.session_state.scheme_name=selected; st.session_state.session=None

analysis=st.session_state.get('analysis')
if analysis:
    summary=analysis['summary']
    st.divider(); st.subheader('2 · Scheme eligibility summary')
    if summary['eligible']: st.success('ELIGIBLE · Income criterion passed')
    else: st.error('NOT ELIGIBLE · Automation disabled')
    st.markdown(f'**{summary["scheme_name"]}**')
    for bullet in summary['eligibility_bullets']: st.markdown(f'- {bullet}')
    if summary.get('income_cap') is not None: st.info(f'Maximum annual income cap: ₹{summary["income_cap"]:,.0f}')
    for note in summary.get('notes',[]): st.caption('Note: '+note)
    st.caption('Summary mode: '+analysis['mode']+' · Demo summaries are informational and are not an official eligibility determination.')
    st.divider(); st.subheader('3 · Local portal preparation')
    st.warning('This demo only fills a local mock form. It does not access or submit to a real government portal.')
    if st.button('🚀 Launch local application preparation',disabled=not summary['eligible'],type='primary'):
        r=api('POST','/api/execute-form',json={'profile':st.session_state.profile,'scheme_name':st.session_state.scheme_name,'eligible':summary['eligible']})
        if r: st.session_state.session=r.json()

session=st.session_state.get('session')
if session:
    st.divider(); st.subheader('4 · Live agent trace')
    st.write('Session status: **'+session['status']+'**')
    for step in session.get('trace_log',[]):
        icon='🟢' if step['status']=='ok' else '🟡' if step['status']=='awaiting_approval' else '🔴'
        st.markdown(f'{icon} **{step["step_number"]}. {step["action"]}**')
        if step.get('selector_used'): st.caption('Selector: '+step['selector_used'])
    if session.get('screenshot_path'):
        p=Path(session['screenshot_path'])
        if p.exists(): st.image(str(p),caption='Filled local mock portal — review before approval',use_container_width=True)
    if session['status']=='awaiting_approval':
        st.warning('Human approval required. Inspect the screenshot before continuing.')
        left,right=st.columns(2)
        with left:
            if st.button('✅ Approve & generate local receipt',type='primary',use_container_width=True):
                r=api('POST',f'/api/execute-form/{session["session_id"]}/confirm',data={'approve':'true'})
                if r: st.session_state.session=r.json()['session']; st.session_state.receipt=r.json(); st.rerun()
        with right:
            if st.button('✖ Abort execution',use_container_width=True):
                r=api('POST',f'/api/execute-form/{session["session_id"]}/confirm',data={'approve':'false'})
                if r: st.session_state.session=r.json()['session']; st.rerun()
    if session['status']=='completed':
        receipt=st.session_state.get('receipt',{})
        st.success('Local demo receipt generated · No government application was submitted.')
        st.code('Receipt reference: '+str(receipt.get('receipt_reference','—')))
        if receipt.get('receipt_url'):
            rr=api('GET',receipt['receipt_url'].replace('/api','/api'))
            if rr: st.download_button('⬇ Download visual receipt (PNG)',rr.content,file_name=f'receipt_{session["session_id"]}.png',mime='image/png')
    if st.button('Clear this demo session'):
        api('DELETE',f'/api/sessions/{session["session_id"]}')
        for key in ['analysis','profile','scheme_name','session','receipt']: st.session_state.pop(key,None)
        st.rerun()
st.divider()
st.caption('CivicMate is a demonstration assistant. Scheme rules can change; always verify requirements with the relevant official department. Profile/session data is held in backend memory and cleared when you clear the session or restart the backend.')
