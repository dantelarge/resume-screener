# Resume Screener AI — Claude Notes

## Project Summary
AI-powered resume screener built with **Python + Streamlit + Anthropic Claude**.

## Stack
- **Language**: Python
- **UI**: Streamlit
- **AI**: Claude (`claude-haiku-4-5-20251001`) via `anthropic` SDK
- **File parsing**: PyPDF2 (PDF), python-docx (DOCX)
- **Config**: `.env` with `ANTHROPIC_API_KEY`

## Files
- `app.py` — main Streamlit app (all logic in one file)
- `requirements.txt` — dependencies
- `.env` — API key (gitignored)

## What It Does
1. User pastes a **job description**
2. User uploads a resume (PDF/DOCX/TXT) **or** pastes resume text
3. Claude analyzes the match and returns structured JSON:
   - Match score (0-100)
   - Recommendation (strong yes / yes / maybe / no)
   - Top strengths, gaps, interview questions, summary
4. Results displayed as cards with color-coded score

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment - Streamlit Community Cloud
- Repo: https://github.com/dantelarge/resume-screener
- Platform: share.streamlit.io
- Set secret in Streamlit Cloud dashboard: `ANTHROPIC_API_KEY = "sk-ant-..."`

## Notes
- Keep all logic in `app.py` - no need to split into multiple files
- The JSON parsing strips markdown fences in case Claude wraps output
- API key loaded from env var first; sidebar input is fallback for local use
