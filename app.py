# -*- coding: utf-8 -*-
import os
import io
import json
import streamlit as st
import anthropic
import PyPDF2
import docx
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Resume Screener AI", page_icon="🎯", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { box-sizing: border-box; }
.stApp { font-family: 'Inter', sans-serif; background: #080e1a; color: #e2e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 3rem 2rem !important; max-width: 1280px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }

/* ── Navbar ── */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 2rem 0; border-bottom: 1px solid #1e293b;
    margin-bottom: 2.5rem;
}
.nav-logo { display: flex; align-items: center; gap: 10px; }
.nav-logo-icon {
    width: 38px; height: 38px; border-radius: 10px;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.nav-logo-text { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; }
.nav-badge {
    font-size: 0.72rem; font-weight: 600; color: #06b6d4;
    background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.25);
    padding: 4px 12px; border-radius: 999px; letter-spacing: 0.3px;
}

/* ── Page title block ── */
.page-title { margin-bottom: 2rem; }
.page-title h1 {
    font-size: 2.4rem; font-weight: 800; color: #f8fafc;
    letter-spacing: -1px; margin: 0 0 6px 0; line-height: 1.2;
}
.page-title h1 span { background: linear-gradient(90deg, #6366f1, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.page-title p { font-size: 1rem; color: #64748b; margin: 0; }

/* ── Input cards ── */
.input-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 16px; padding: 24px;
}
.input-card-label {
    font-size: 0.8rem; font-weight: 700; letter-spacing: 0.8px;
    text-transform: uppercase; color: #64748b; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}
.input-card-label span { color: #94a3b8; font-size: 1rem; }

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: #080e1a !important; border: 1px solid #1e293b !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    font-size: 0.9rem !important; font-family: 'Inter', sans-serif !important;
}
.stTextArea textarea:focus { border-color: #6366f1 !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important; }
.stFileUploader {
    background: #080e1a !important; border: 1px dashed #1e293b !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"] { background: #080e1a !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: #6366f1 !important; }

/* ── Analyze button ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-size: 1rem !important;
    font-weight: 700 !important; padding: 0.75rem 2rem !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 28px rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Divider ── */
.divider { border: none; border-top: 1px solid #1e293b; margin: 2rem 0; }

/* ── Results header ── */
.results-title {
    font-size: 1.5rem; font-weight: 800; color: #f8fafc;
    letter-spacing: -0.5px; margin-bottom: 0.25rem;
}
.results-sub { font-size: 0.88rem; color: #475569; }

/* ── Score card ── */
.score-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 20px; padding: 32px 24px;
    display: flex; flex-direction: column; align-items: center; gap: 16px;
}
.score-ring-wrap { position: relative; width: 160px; height: 160px; }
.score-ring-wrap svg { transform: rotate(-90deg); }
.score-center {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%); text-align: center; line-height: 1;
}
.score-num { font-size: 2.6rem; font-weight: 800; }
.score-denom { font-size: 0.7rem; color: #475569; margin-top: 3px; font-weight: 500; }
.score-bar-wrap { width: 100%; }
.score-bar-label { display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-bottom: 6px; }
.score-bar-track { background: #1e293b; border-radius: 999px; height: 6px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 999px; }

/* ── Verdict card ── */
.verdict-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 20px; padding: 28px 24px;
    display: flex; flex-direction: column; gap: 16px;
}
.verdict-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: #475569; }
.verdict-pill {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 22px; border-radius: 999px; font-weight: 700; font-size: 1rem;
}
.v-strong { background: rgba(34,197,94,0.12); color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
.v-yes    { background: rgba(99,102,241,0.12); color: #818cf8; border: 1px solid rgba(99,102,241,0.25); }
.v-maybe  { background: rgba(234,179,8,0.12);  color: #facc15; border: 1px solid rgba(234,179,8,0.25); }
.v-no     { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
.match-level { font-size: 0.88rem; font-weight: 600; }

/* ── Summary card ── */
.summary-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 20px; padding: 28px 24px; height: 100%;
}
.summary-card p { font-size: 0.95rem; color: #94a3b8; line-height: 1.8; margin: 0; }
.card-heading {
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.8px;
    text-transform: uppercase; color: #475569; margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
}
.card-heading-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

/* ── List cards ── */
.list-card {
    background: #0f172a; border: 1px solid #1e293b;
    border-radius: 20px; padding: 24px;
}
.list-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 14px; border-radius: 10px; margin-bottom: 8px;
    font-size: 0.88rem; line-height: 1.6;
}
.list-item:last-child { margin-bottom: 0; }
.li-green { background: rgba(34,197,94,0.07); border: 1px solid rgba(34,197,94,0.15); color: #86efac; }
.li-red   { background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.15); color: #fca5a5; }
.li-blue  { background: rgba(99,102,241,0.07); border: 1px solid rgba(99,102,241,0.15); color: #a5b4fc; }
.li-icon  { flex-shrink: 0; font-size: 0.8rem; font-weight: 800; min-width: 22px; margin-top: 1px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0a1020 !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li { color: #94a3b8 !important; font-size: 0.88rem !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: #0f172a !important; border: 1px solid #1e293b !important; color: #e2e8f0 !important;
    border-radius: 8px !important;
}
.sidebar-logo {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0 20px 0; border-bottom: 1px solid #1e293b; margin-bottom: 20px;
}
.sidebar-logo-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    display: flex; align-items: center; justify-content: center; font-size: 0.9rem;
}
.sidebar-logo-text { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; }
.step-row { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 14px; }
.step-num {
    min-width: 22px; height: 22px; border-radius: 6px;
    background: rgba(99,102,241,0.2); color: #818cf8;
    font-size: 0.72rem; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}
.step-text { font-size: 0.85rem; color: #94a3b8; line-height: 1.5; padding-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎯</div>
        <div class="sidebar-logo-text">ResumeAI</div>
    </div>
    """, unsafe_allow_html=True)

    env_key = os.getenv("ANTHROPIC_API_KEY", "")
    if env_key:
        api_key = env_key
        st.success("✅ API key loaded")
    else:
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        st.caption("Or add `ANTHROPIC_API_KEY` to `.env`")

    st.markdown("---")
    st.markdown("**How to use**")
    st.markdown("""
    <div class="step-row"><div class="step-num">1</div><div class="step-text">Paste the job description</div></div>
    <div class="step-row"><div class="step-num">2</div><div class="step-text">Upload a resume or paste text</div></div>
    <div class="step-row"><div class="step-num">3</div><div class="step-text">Hit Analyze Resume</div></div>
    <div class="step-row"><div class="step-num">4</div><div class="step-text">Review the AI report</div></div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Powered by Claude · Built with Streamlit")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="nav-logo">
        <div class="nav-logo-icon">🎯</div>
        <div class="nav-logo-text">Resume Screener AI</div>
    </div>
    <div class="nav-badge">✦ Powered by Claude</div>
</div>
<div class="page-title">
    <h1>Screen resumes with <span>AI precision</span></h1>
    <p>Upload a resume and job description — get a deep match analysis in seconds</p>
</div>
""", unsafe_allow_html=True)

# ── Input Section ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="input-card-label"><span>📋</span> Job Description</div>
    """, unsafe_allow_html=True)
    job_description = st.text_area(
        label="jd", label_visibility="collapsed",
        placeholder="Paste the full job description here...\n\nExample:\nSenior Python Developer\n• 5+ years Python\n• FastAPI or Django\n• PostgreSQL & AWS",
        height=300,
    )

with col2:
    st.markdown("""
    <div class="input-card-label"><span>📄</span> Candidate Resume</div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    resume_text_input = st.text_area(
        label="Or paste resume text",
        placeholder="Paste resume text here if not uploading a file...",
        height=190,
    )

st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([2, 1, 2])
with btn_col:
    screen = st.button("🔍 Analyze Resume", use_container_width=True, type="primary")

# ── Helpers ────────────────────────────────────────────────────────────────────
def extract_text(f) -> str:
    name = f.name.lower()
    data = io.BytesIO(f.read())
    if name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(data)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        d = docx.Document(data)
        return "\n".join(p.text for p in d.paragraphs)
    elif name.endswith(".txt"):
        return data.read().decode("utf-8")
    return ""


def screen_resume(api_key, job_description, resume) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""You are a senior hiring expert. Evaluate this resume against the job description rigorously and honestly.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}

Respond with valid JSON only — no markdown fences, no text outside the JSON:
{{
  "score": <integer 0-100>,
  "recommendation": "<exactly one of: strong yes | yes | maybe | no>",
  "top_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>"],
  "summary": "<2-3 sentence plain-English summary for a hiring manager>",
  "interview_questions": ["<question 1>", "<question 2>", "<question 3>"]
}}"""
    with st.spinner("🤖 Claude is analyzing the resume..."):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def score_ring(score: int) -> str:
    if score >= 80:   color = "#22c55e"
    elif score >= 60: color = "#f59e0b"
    else:             color = "#ef4444"
    r = 66
    circumference = 2 * 3.14159 * r
    offset = circumference * (1 - score / 100)
    bar_pct = score
    return f"""
    <div class="score-card">
        <div class="score-ring-wrap">
            <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="{r}" fill="none" stroke="#1e293b" stroke-width="10"/>
                <circle cx="80" cy="80" r="{r}" fill="none" stroke="{color}" stroke-width="10"
                    stroke-linecap="round"
                    stroke-dasharray="{circumference:.1f}"
                    stroke-dashoffset="{offset:.1f}"/>
            </svg>
            <div class="score-center">
                <div class="score-num" style="color:{color}">{score}</div>
                <div class="score-denom">/ 100</div>
            </div>
        </div>
        <div class="score-bar-wrap">
            <div class="score-bar-label"><span>Match Score</span><span style="color:{color};font-weight:700">{score}%</span></div>
            <div class="score-bar-track">
                <div class="score-bar-fill" style="width:{bar_pct}%;background:{color}"></div>
            </div>
        </div>
    </div>"""


def verdict_card(recommendation: str, score: int) -> str:
    mapping = {
        "strong yes": ("v-strong", "✅ Strong Hire"),
        "yes":        ("v-yes",    "👍 Hire"),
        "maybe":      ("v-maybe",  "🤔 Consider"),
        "no":         ("v-no",     "❌ Pass"),
    }
    cls, label = mapping.get(recommendation.lower(), ("v-yes", recommendation.title()))
    if score >= 80:   level, lcolor = "Excellent Match", "#4ade80"
    elif score >= 60: level, lcolor = "Good Match", "#facc15"
    else:             level, lcolor = "Weak Match", "#f87171"
    return f"""
    <div class="verdict-card">
        <div>
            <div class="verdict-label">Hiring Decision</div>
            <span class="verdict-pill {cls}">{label}</span>
        </div>
        <div>
            <div class="verdict-label">Match Level</div>
            <div class="match-level" style="color:{lcolor}">{level}</div>
        </div>
    </div>"""


# ── Results ────────────────────────────────────────────────────────────────────
if screen:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    else:
        resume = ""
        if uploaded_file:
            resume = extract_text(uploaded_file)
            if not resume.strip():
                st.error("Could not extract text from the file. Try pasting the resume instead.")
                st.stop()
        elif resume_text_input.strip():
            resume = resume_text_input.strip()
        else:
            st.error("Please upload a resume or paste resume text.")
            st.stop()

        try:
            result = screen_resume(api_key, job_description, resume)
            score = result["score"]

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-bottom:1.5rem">
                <div class="results-title">📊 Analysis Report</div>
                <div class="results-sub">AI-generated assessment · Match score: {score}/100</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Row 1: score | verdict | summary ──────────────────────────────
            r1, r2, r3 = st.columns([1, 1, 2], gap="large")

            with r1:
                st.markdown(score_ring(score), unsafe_allow_html=True)

            with r2:
                st.markdown(verdict_card(result["recommendation"], score), unsafe_allow_html=True)

            with r3:
                st.markdown(f"""
                <div class="summary-card">
                    <div class="card-heading">
                        <div class="card-heading-dot" style="background:#6366f1"></div>
                        AI Summary
                    </div>
                    <p>{result["summary"]}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Row 2: strengths | gaps | questions ───────────────────────────
            b1, b2, b3 = st.columns(3, gap="large")

            with b1:
                st.markdown("""
                <div class="list-card">
                    <div class="card-heading">
                        <div class="card-heading-dot" style="background:#22c55e"></div>
                        Top Strengths
                    </div>
                """, unsafe_allow_html=True)
                for s in result.get("top_strengths", []):
                    st.markdown(f'<div class="list-item li-green"><span class="li-icon">✓</span><span>{s}</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with b2:
                st.markdown("""
                <div class="list-card">
                    <div class="card-heading">
                        <div class="card-heading-dot" style="background:#ef4444"></div>
                        Skill Gaps
                    </div>
                """, unsafe_allow_html=True)
                gaps = result.get("gaps", [])
                if gaps:
                    for g in gaps:
                        st.markdown(f'<div class="list-item li-red"><span class="li-icon">✗</span><span>{g}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="list-item li-green"><span class="li-icon">✓</span><span>No significant gaps found</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with b3:
                st.markdown("""
                <div class="list-card">
                    <div class="card-heading">
                        <div class="card-heading-dot" style="background:#6366f1"></div>
                        Interview Questions
                    </div>
                """, unsafe_allow_html=True)
                for i, q in enumerate(result.get("interview_questions", []), 1):
                    st.markdown(f'<div class="list-item li-blue"><span class="li-icon">Q{i}</span><span>{q}</span></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🔧 Raw JSON"):
                st.json(result)

        except json.JSONDecodeError:
            st.error("Claude returned an unexpected format. Please try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
