import json, re
from pathlib import Path
from pypdf import PdfReader
from .config import GEMINI_API_KEY, GEMINI_MODEL, SAMPLE_DIR
from .models import Language, SchemeSummary

LANGUAGE_BULLETS = {
 "PMAY": {
  "English": ["Families with annual income up to ₹3,00,000 may meet this sample scheme's income criterion.", "The applicant's family should not own a pucca house anywhere in India.", "The sample guideline specifies a woman applicant or joint ownership where applicable."],
  "Tamil": ["ஆண்டு வருமானம் ₹3,00,000 வரை உள்ள குடும்பங்கள் இந்த மாதிரி திட்டத்தின் வருமானத் தகுதியைப் பூர்த்தி செய்யலாம்.", "விண்ணப்பதாரரின் குடும்பத்துக்கு இந்தியாவில் எங்கும் நிரந்தர வீடு இருக்கக்கூடாது.", "பொருந்தும் இடங்களில் பெண் உறுப்பினர் பெயரில் அல்லது கூட்டுப் பெயரில் விண்ணப்பிக்க வேண்டும்."],
  "Hindi": ["₹3,00,000 तक वार्षिक आय वाले परिवार इस नमूना योजना की आय संबंधी शर्त पूरी कर सकते हैं।", "आवेदक के परिवार के पास भारत में कहीं भी पक्का मकान नहीं होना चाहिए।", "जहाँ लागू हो, आवेदन महिला सदस्य के नाम पर या संयुक्त नाम से होना चाहिए।"],
  "Telugu": ["వార్షిక ఆదాయం ₹3,00,000 వరకు ఉన్న కుటుంబాలు ఈ నమూనా పథకం ఆదాయ అర్హతను చేరుకోవచ్చు.", "దరఖాస్తుదారు కుటుంబానికి భారతదేశంలో ఎక్కడా పక్కా ఇల్లు ఉండకూడదు.", "వర్తించే చోట మహిళ పేరు మీద లేదా ఉమ్మడి పేరుతో దరఖాస్తు చేయాలి."],
  "Marathi": ["वार्षिक उत्पन्न ₹3,00,000 पर्यंत असलेली कुटुंबे या नमुना योजनेची उत्पन्न अट पूर्ण करू शकतात.", "अर्जदाराच्या कुटुंबाच्या नावावर भारतात कुठेही पक्के घर नसावे.", "लागू असल्यास महिलेच्या नावाने किंवा संयुक्त नावाने अर्ज करावा."]
 },
 "PMKISAN": {
  "English": ["Eligible landholding farmer families may receive income support under the scheme rules.", "Benefits and exclusions depend on the current official eligibility guidelines.", "Land and identity records may need verification by the relevant authorities."],
  "Tamil": ["தகுதியுள்ள நிலம் வைத்துள்ள விவசாயக் குடும்பங்கள் திட்ட விதிகளின்படி வருமான உதவி பெறலாம்.", "பலன்களும் விலக்குகளும் தற்போதைய அதிகாரப்பூர்வ தகுதி விதிகளைப் பொறுத்தது.", "நிலம் மற்றும் அடையாளப் பதிவுகளை சம்பந்தப்பட்ட அதிகாரிகள் சரிபார்க்க வேண்டியிருக்கலாம்."],
  "Hindi": ["पात्र भूमिधारक किसान परिवार योजना के नियमों के अनुसार आय सहायता प्राप्त कर सकते हैं।", "लाभ और अपवाद वर्तमान आधिकारिक पात्रता दिशानिर्देशों पर निर्भर करते हैं।", "संबंधित अधिकारियों द्वारा भूमि और पहचान अभिलेखों का सत्यापन आवश्यक हो सकता है।"],
  "Telugu": ["అర్హత గల భూమి కలిగిన రైతు కుటుంబాలు పథకం నిబంధనల ప్రకారం ఆదాయ సహాయం పొందవచ్చు.", "ప్రయోజనాలు, మినహాయింపులు ప్రస్తుత అధికారిక అర్హత మార్గదర్శకాలపై ఆధారపడి ఉంటాయి.", "సంబంధిత అధికారులు భూమి, గుర్తింపు రికార్డులను ధృవీకరించాల్సి రావచ్చు."],
  "Marathi": ["पात्र जमीनधारक शेतकरी कुटुंबांना योजनेच्या नियमांनुसार उत्पन्न सहाय्य मिळू शकते.", "लाभ आणि अपवाद सध्याच्या अधिकृत पात्रता मार्गदर्शक तत्त्वांवर अवलंबून असतात.", "संबंधित अधिकाऱ्यांकडून जमीन आणि ओळख नोंदींची पडताळणी आवश्यक असू शकते."]
 }
}

def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == '.txt':
        return content.decode('utf-8-sig', errors='replace')
    if suffix == '.pdf':
        import io
        reader = PdfReader(io.BytesIO(content))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    raise ValueError('Invalid file format. Please upload a PDF or TXT file.')

def _offline_summary(scheme_id: str, language: Language, text: str = '') -> SchemeSummary:
    key = 'PMKISAN' if 'kisan' in scheme_id.lower() else 'PMAY'
    data = json.loads((SAMPLE_DIR / 'schemes.json').read_text(encoding='utf-8'))
    scheme = data[key]
    bullets = LANGUAGE_BULLETS[key].get(language.value, LANGUAGE_BULLETS[key]['English'])
    # If a custom text explicitly contains a recognizable income cap, use it; otherwise sample metadata is retained.
    cap = scheme.get('income_cap')
    match = re.search(r'(?:₹|INR\s*)([0-9,]{4,})', text or '', re.I)
    if match:
        try: cap = float(match.group(1).replace(',', ''))
        except ValueError: pass
    return SchemeSummary(scheme_name=scheme['name'], eligibility_bullets=bullets,
        income_cap=cap, eligible=True,
        notes=["Offline demo summary. Verify all criteria against the latest official scheme notification."])

def summarize_policy(scheme_id: str, language: Language, text: str = '') -> tuple[SchemeSummary, bool]:
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'replace_me':
        return _offline_summary(scheme_id, language, text), True
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f'''Extract policy criteria from the source text and translate the summary into {language.value}. Return JSON only with keys scheme_name, eligibility_bullets (exactly 3 concise strings), income_cap (number in INR or null), notes (array). Do not calculate whether a citizen is eligible. Never invent facts; if absent, say so in notes. Source text:\n{text[:30000]}'''
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        raw = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        obj = json.loads(raw)
        summary = SchemeSummary(scheme_name=obj['scheme_name'], eligibility_bullets=obj['eligibility_bullets'][:3],
            income_cap=obj.get('income_cap'), eligible=True, notes=obj.get('notes', []))
        return summary, False
    except Exception:
        # A service outage should not break the demo. Static data is explicitly labelled offline.
        return _offline_summary(scheme_id, language, text), True

def apply_income_gate(summary: SchemeSummary, annual_income: float) -> SchemeSummary:
    eligible = summary.income_cap is None or annual_income <= summary.income_cap
    notes = list(summary.notes)
    if not eligible:
        notes.append(f"Income exceeds the scheme cap of ₹{summary.income_cap:,.0f}; automation is blocked.")
    return summary.model_copy(update={"eligible": eligible, "notes": notes})
