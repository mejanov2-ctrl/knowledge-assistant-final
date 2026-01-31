import streamlit as st
import time

# --- ROBUST IMPORT SECTION ---
# This handles the library renaming issue automatically
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        st.error("Library Error: Please update requirements.txt to include 'ddgs>=2.0.0'")
        st.stop()

# --- SEARCH FUNCTION ---
def search_live_web(query_text):
    """
    Safely searches the web. Handles empty results and cloud blocking.
    """
    results = []
    try:
        with DDGS() as ddgs:
            # Request 5 results
            search_gen = ddgs.text(query_text, max_results=5)
            # Safely convert generator to list
            if search_gen:
                results = list(search_gen)
                
    except Exception as e:
        print(f"Search API Error: {e}")
        st.warning(f"⚠️ Search API issue: {e}")
        return None

    if not results:
        st.warning("⚠️ Search returned 0 results. DuckDuckGo might be blocking the server IP.")
        return None
        
    return results
