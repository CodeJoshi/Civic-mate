import io
import fitz  # PyMuPDF
from typing import List, Optional
from pydantic import BaseModel, Field
from gtts import gTTS
from google import genai
from google.genai import types
from backend.app.config import get_settings

# ---------------------------------------------------------
# Pydantic Output Schema for Gemini Structured Output
# ---------------------------------------------------------
class PolicyAnalysisResponse(BaseModel):
    scheme_name: str = Field(description="Name of the government scheme or circular title")
    eligibility_criteria: List[str] = Field(description="Clear eligibility conditions required to apply")
    benefits: List[str] = Field(description="Monetary, subsidy, or welfare benefits provided")
    required_documents: List[str] = Field(description="List of mandatory documents (e.g. Aadhaar, Income Certificate)")
    regional_summary: str = Field(description="Clear, 3-4 sentence plain conversational summary translated into the requested target language")

# Language code mapping for Google Text-to-Speech (gTTS)
LANG_CODE_MAP = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "Hindi": "hi",
    "தமிழ் (Tamil)": "ta",
    "Tamil": "ta",
    "తెలుగు (Telugu)": "te",
    "Telugu": "te",
    "मराठी (Marathi)": "mr",
    "Marathi": "mr",
    "বাংলা (Bengali)": "bn",
    "Bengali": "bn",
    "ಕನ್ನಡ (Kannada)": "kn",
    "Kannada": "kn"
}

class AIService:
    def __init__(self):
        settings = get_settings()
        api_key = settings.get("gemini_api_key")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_name = settings.get("gemini_model", "gemini-2.5-flash")

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extracts selectable text from an uploaded PDF stream."""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_content = []
        for page in doc:
            text_content.append(page.get_text())
        extracted = "\n".join(text_content).strip()
        if not extracted:
            raise ValueError("No selectable text found in PDF. Scanned images require OCR.")
        return extracted

    def parse_policy(self, text_content: str, target_language: str = "English") -> PolicyAnalysisResponse:
        """
        Uses Gemini 2.5 Flash Structured Outputs to extract structured eligibility
        data and generate a conversational regional summary.
        """
        if not self.client:
            # Deterministic fallback when API key is missing
            return PolicyAnalysisResponse(
                scheme_name="Civic Mate Service Notice",
                eligibility_criteria=["System running in offline mode. Please configure GEMINI_API_KEY."],
                benefits=["Informational preview only."],
                required_documents=["Government photo identity proof"],
                regional_summary=f"This is an offline system response. Please provide a Gemini API key to generate a full {target_language} translation."
            )

        prompt = f"""
        You are Civic Mate's expert welfare policy analyst.
        Analyze the following government notification/policy document:
        
        ---
        {text_content[:15000]}
        ---
        
        Tasks:
        1. Extract clear, verified eligibility criteria.
        2. Extract direct citizen benefits.
        3. List all mandatory verification documents.
        4. Write a warm, plain-language summary in {target_language} explaining how this policy directly impacts everyday citizens.
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PolicyAnalysisResponse,
                temperature=0.2
            )
        )

        return PolicyAnalysisResponse.model_validate_json(response.text)

    def generate_regional_audio(self, text: str, target_language: str = "English") -> bytes:
        """
        Converts regional summary text into an in-memory MP3 audio stream using gTTS.
        """
        lang_code = LANG_CODE_MAP.get(target_language, "en")
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()


ai_service = AIService()