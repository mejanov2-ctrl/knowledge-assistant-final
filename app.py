import streamlit as st
import time
from groq import Groq
from duckduckgo_search import DDGS

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Technical Resolution Assistant", page_icon="🛡️", layout="wide")

# SECURITY: Retrieve API Key from Streamlit Secrets
try:
    GROQ_API_KEY = st.secrets["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"]
except:
    st.error("⚠️ API Key missing! Please set GROQ_API_KEY in Streamlit Secrets.")
    st.stop()

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main .block-container { color: #1e1e1e !important; }
    h1, h2, h3, p, li { color: #1e1e1e; }
    a { color: #0078D4; font-weight: bold; text-decoration: none; }
    section[data-testid="stSidebar"] { background-color: #0F172A; }
    section[data-testid="stSidebar"] * { color: white !important; }
    .green-tier { border-left: 6px solid #10B981; background-color: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #1e1e1e; }
    .red-tier { border-left: 6px solid #EF4444; background-color: #FEF2F2; padding: 15px; border-radius: 8px; margin-bottom: 20px; color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AI FUNCTIONS ---
def get_live_solution(user_query):
    client = Groq(api_key=GROQ_API_KEY)
    search_results = ""
    source_link = "#"
    source_name = "Unknown"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(user_query, max_results=3))
            if results:
                source_name = results[0]['title']
                source_link = results[0]['href']
                for r in results:
                    search_results += f"Title: {r['title']}\nSnippet: {r['body']}\nSource: {r['href']}\n\n"
    except Exception as e:
        return "Error", "Could not search web.", "#", "N/A"

    system_prompt = """
    You are an Enterprise Technical Assistant. 
    Analyze the provided search results to answer the user's technical question.
    CRITICAL STEP: Determine the "Safety Tier":
    - If from Official Vendor Documentation (Microsoft Learn, AWS Docs, etc.), classify as "GREEN".
    - If from Community Forums (Reddit, StackOverflow), classify as "RED".
    Output format strictly:
    TIER: [GREEN or RED]
    SUMMARY: [Concise 3-step guide]
    RISK_ANALYSIS: [Why safe or unsafe?]
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {user_query}\n\nSearch Results:\n{search_results}"}
            ],
            model="llama3-8b-8192",
            temperature=0.1,
        )
        return chat_completion.choices[0].message.content, source_name, source_link
    except Exception as e:
        return "Error", f"AI Error: {str(e)}", "#"

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("🛠️ Tech Assistant")
    st.info("Brain: **Llama3 on Groq**")
    st.info("Eyes: **DuckDuckGo Live**")
    st.caption("Live Mode Active")

# --- 4. MAIN APP ---
st.title("🛡️ Technical Solution Finder (LIVE AI)")
st.markdown("Describe the issue. The AI will search the live web and classify safety.")

issue_input = st.text_area("Describe the Issue / Error Message:", height=100)

if st.button("🔍 Find Live Solution", type="primary"):
    if not issue_input:
        st.error("Please describe the issue first.")
    else:
        with st.status("🧠 Active Reasoning Engine...", expanded=True):
            st.write("1. 🌐 Searching live internet...")
            ai_response, source_title, source_url = get_live_solution(issue_input)
            st.write("2. 🤖 Analyzing vendor authority...")
            time.sleep(0.5) 
            st.write("3. 🛡️ Classifying Safety Tier...")

        st.divider()
        
        if "TIER: GREEN" in ai_response:
            display_text = ai_response.replace("TIER: GREEN", "").replace("SUMMARY:", "").replace("RISK_ANALYSIS:", "\n\n**Risk Analysis:**")
            st.success("✅ **Solution Found:** Verified Vendor Source")
            st.markdown(f"""<div class="green-tier"><h3>🌟 Verified Vendor Solution (Live)</h3><p><b>Source:</b> <a href="{source_url}">{source_title}</a></p><p><b>AI Classification:</b> Trusted Vendor Documentation</p></div>""", unsafe_allow_html=True)
            with st.expander("📖 View Guide", expanded=True):
                st.markdown(display_text)
                st.button("✅ Verify & Add to KB")
        elif "TIER: RED" in ai_response:
            display_text = ai_response.replace("TIER: RED", "").replace("SUMMARY:", "").replace("RISK_ANALYSIS:", "\n\n**Risk Analysis:**")
            st.warning("⚠️ **Solution Found:** Unverified / Community Source")
            st.markdown(f"""<div class="red-tier"><h3>⚠️ Warning: Community Solution (Live)</h3><p><b>Source:</b> <a href="{source_url}">{source_title}</a></p><p><b>Risk Alert:</b> Not official vendor.</p></div>""", unsafe_allow_html=True)
            with st.expander("🛑 Review Unverified Solution", expanded=True):
                st.error("🛡️ **Safety Guardrail Triggered**")
                st.markdown(display_text)
                st.button("🚫 Report as Risky")
        else:
            st.error("Could not classify solution.")
            st.write(ai_response)