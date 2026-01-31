import streamlit as st
import time

# --- ROBUST IMPORT SECTION ---
try:
    from duckduckgo_search import DDGS
except ImportError:
    st.error("Library Error: Please update requirements.txt to include 'ddgs>=2.0.0'")
    st.stop()

# --- FIXED SEARCH FUNCTION ---
def search_live_web(query_text):
    """
    Safely searches the web using the new DDGS library.
    Handles empty results and timeouts gracefully.
    """
    results = []
    try:
        # The new DDGS library usage
        with DDGS() as ddgs:
            # We request 5 results
            search_gen = ddgs.text(query_text, max_results=5)
            
            # Safely convert generator to list
            if search_gen:
                results = list(search_gen)
                
    except Exception as e:
        # If the search fails (e.g. timeout), we log it but don't crash
        print(f"Search API Error: {e}")
        st.warning(f"⚠️ Search API encountered an issue: {e}")
        return None

    # Check if results are empty (Common with Cloud IP blocking)
    if not results:
        st.warning("⚠️ The search returned 0 results. DuckDuckGo might be blocking the server IP.")
        return None
        
    return results

# --- YOUR MAIN APP LOGIC ---
# (Paste this where your button logic usually goes)

if st.button("Find Live Solution"):
    st.markdown("### 1. 🌐 Searching live internet...")
    
    # 1. RUN THE SEARCH
    web_results = search_live_web(query) # Assuming 'query' is your input variable name
    
    # 2. CHECK RESULTS BEFORE PROCEEDING
    if not web_results:
        st.error("❌ Process Stopped: No search results found to analyze.")
        st.stop() # This prevents the crash!
    
    # 3. IF SUCCESSFUL, DISPLAY AND CONTINUE
    st.success(f"✅ Found {len(web_results)} relevant sources.")
    with st.expander("View Source Data"):
        st.write(web_results)

    # 4. CONTINUE TO CLASSIFICATION
    # st.markdown("### 2. 🧠 Analyzing vendor authority...")
    # call_your_next_function(web_results)
