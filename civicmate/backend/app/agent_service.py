import asyncio, hashlib, os, sys
from datetime import datetime, timezone
from pathlib import Path
from .config import SAMPLE_DIR, RECEIPT_DIR, HEADLESS_MODE, MAX_DOM_ACTIONS, SELECTOR_TIMEOUT_MS
from .models import UserProfile, AgentStep

async def _browser_run(profile: UserProfile, session_id: str, headed: bool = False):
    """Populate only the bundled local mock portal; never navigate to a user-supplied URL."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError('Playwright is not installed. Run: playwright install chromium') from exc
    steps=[]; shot=None
    def log(action, selector=None, status='ok'):
        steps.append(AgentStep(step_number=len(steps)+1, action=action, selector_used=selector, status=status))
        if len(steps) > MAX_DOM_ACTIONS:
            raise RuntimeError('Automation exceeded the 10-action safety limit.')
    portal = (SAMPLE_DIR / 'mock_portal.html').resolve()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=(HEADLESS_MODE and not headed))
        page = await browser.new_page(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        await page.goto(portal.as_uri(), wait_until='domcontentloaded', timeout=SELECTOR_TIMEOUT_MS)
        log('Opened the local CivicMate demo portal', 'file://mock_portal.html')
        await page.locator('#applicant_name').fill(profile.name, timeout=SELECTOR_TIMEOUT_MS)
        log('Populated applicant name', '#applicant_name')
        await page.locator('#annual_income').fill(str(profile.annual_income), timeout=SELECTOR_TIMEOUT_MS)
        log('Populated annual income', '#annual_income')
        await page.locator('#state').select_option(label=profile.state, timeout=SELECTOR_TIMEOUT_MS)
        log('Selected state', '#state')
        await page.locator('#category').select_option(label=profile.category, timeout=SELECTOR_TIMEOUT_MS)
        log('Selected social category', '#category')
        await page.locator('#review_status').wait_for(state='visible', timeout=SELECTOR_TIMEOUT_MS)
        await page.locator('#review_status').fill('Ready for citizen review — not submitted')
        log('Prepared local form for review', '#review_status')
        await page.screenshot(path=str(RECEIPT_DIR / f'preview_{session_id}.png'), full_page=True)
        log('Captured pre-approval review screenshot', None)
        await browser.close()
    return steps, str(RECEIPT_DIR / f'preview_{session_id}.png')

async def prepare_execution(profile: UserProfile, session_id: str):
    return await _browser_run(profile, session_id, headed=False)

async def finalize_demo_receipt(profile: UserProfile, session_id: str, receipt_reference: str):
    """Explicit approval completes the local demo only; no external portal is contacted."""
    steps, _ = await _browser_run(profile, session_id, headed=False)
    # Add a visible receipt marker to the screenshot through the local page's final state.
    from playwright.async_api import async_playwright
    portal=(SAMPLE_DIR / 'mock_portal.html').resolve()
    receipt=RECEIPT_DIR / f'receipt_{session_id}.png'
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        page=await browser.new_page(viewport={"width":1280,"height":900})
        await page.goto(portal.as_uri(), wait_until='domcontentloaded', timeout=SELECTOR_TIMEOUT_MS)
        await page.locator('#applicant_name').fill(profile.name)
        await page.locator('#annual_income').fill(str(profile.annual_income))
        await page.locator('#state').select_option(label=profile.state)
        await page.locator('#category').select_option(label=profile.category)
        await page.locator('#review_status').fill('Citizen approved local demo receipt — no government submission')
        await page.locator('#receipt_banner').evaluate("el => el.style.display = 'block'")
        stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')
        await page.locator('#receipt_banner').evaluate("(el, data) => { el.innerHTML += `<br><strong>Receipt:</strong> ${data.ref}<br><strong>Generated:</strong> ${data.stamp}`; }", {"ref": receipt_reference, "stamp": stamp})
        await page.screenshot(path=str(receipt), full_page=True)
        await browser.close()
    return steps, str(receipt)
