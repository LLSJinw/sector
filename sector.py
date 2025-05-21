import streamlit as st
import cohere

# Initialize Cohere Chat model
co = cohere.Client("sNIAP0wwbfOagyZr75up0a6tVejuZ6ONH0ODCsOa")

SECTOR_LABELS = [
    "Critical Infrastructure (CII)",
    "Banking / Finance / Insurance (BFSI)",
    "Healthcare",
    "Government / SOE",
    "Software / Tech / SaaS",
    "Telco / ISP",
    "Retail / SME / Logistics",
    "Manufacturing / OT-heavy"
]

PROMPT_INSTRUCTION = f"""
You're a sector classification assistant trained to categorize companies into one of the following sectors:

{', '.join(SECTOR_LABELS)}

Given a company name, return the sector only, and a brief reason in JSON format.

Example output:
{{"sector": "Healthcare", "reason": "The company operates a major hospital network in Thailand."}}
"""

def classify_sector_with_chat(company_name):
    try:
        response = co.chat(
            model="command-r-plus",  # or "command-a-03-2025"
            message=f"{PROMPT_INSTRUCTION}\nCompany: {company_name}",
            temperature=0.3
        )
        return response.text
    except Exception as e:
        return None, str(e)

# --- Streamlit UI ---
st.set_page_config(page_title="Cohere Chat Sector Classifier", page_icon="🧠")
st.title("🧠 AI Sector Classifier (via Cohere Chat API)")

company_input = st.text_input("🔍 Enter company or organization name:")

if company_input:
    with st.spinner("Asking Cohere AI for sector classification..."):
        result = classify_sector_with_chat(company_input)

    if result:
        st.success("✅ Sector Prediction Received")
        st.code(result, language="json")
    else:
        st.error("❌ Failed to get a response. Check API key or request limits.")
