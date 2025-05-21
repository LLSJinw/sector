import streamlit as st
import cohere

# Initialize Cohere client with user's trial key
co = cohere.Client("sNIAP0wwbfOagyZr75up0a6tVejuZ6ONH0ODCsOa")

# Fixed sector labels for Thai cybersecurity advisory context
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

# Sample examples for Cohere classifier to learn from
EXAMPLES = [
    {"text": "Electricity Generating Authority of Thailand", "label": "Critical Infrastructure (CII)"},
    {"text": "PEA", "label": "Critical Infrastructure (CII)"},
    {"text": "Bangkok Bank", "label": "Banking / Finance / Insurance (BFSI)"},
    {"text": "Krungthai Bank", "label": "Banking / Finance / Insurance (BFSI)"},
    {"text": "Siriraj Hospital", "label": "Healthcare"},
    {"text": "Bumrungrad Hospital", "label": "Healthcare"},
    {"text": "Ministry of Digital Economy and Society", "label": "Government / SOE"},
    {"text": "Office of the National Cyber Security Agency", "label": "Government / SOE"},
    {"text": "SCB Tech X", "label": "Software / Tech / SaaS"},
    {"text": "Bitkub", "label": "Software / Tech / SaaS"},
    {"text": "AIS", "label": "Telco / ISP"},
    {"text": "True Corporation", "label": "Telco / ISP"},
    {"text": "Lazada", "label": "Retail / SME / Logistics"},
    {"text": "Makro", "label": "Retail / SME / Logistics"},
    {"text": "PTT Global Chemical", "label": "Manufacturing / OT-heavy"},
    {"text": "IRPC", "label": "Manufacturing / OT-heavy"}
]

# Function to classify company sector using Cohere API
def classify_sector_with_cohere(company_name):
    try:
        response = co.classify(
            model='embed-english-v3.0',
            inputs=[company_name],
            examples=[cohere.ClassifyExample(text=e["text"], label=e["label"]) for e in EXAMPLES]
        )
        result = response.classifications[0]
        return result.prediction, result.confidence
    except Exception as e:
        return None, str(e)

# Streamlit UI
st.set_page_config(page_title="AI Sector Classifier", page_icon="🧠")
st.title("🧠 AI-Powered Company Sector Classifier (Cohere)")

st.markdown("""
Enter a Thai or English **company name** and let the Cohere AI model classify it into one of the defined cybersecurity-related sectors.  
This helps match your customer with the right **advisory services** based on industry.
""")

company_input = st.text_input("🔍 Enter company or organization name:")

if company_input:
    with st.spinner("Classifying sector using AI..."):
        sector, confidence = classify_sector_with_cohere(company_input)

    if sector:
        st.success(f"✅ Predicted Sector: **{sector}**")
        st.markdown(f"**Confidence Score:** `{confidence:.2%}`")

        # Optional: map sector to example service set
        services_map = {
            "Critical Infrastructure (CII)": "Cyber Risk Assessment (IT/OT), TTX, IRP & Playbook",
            "Banking / Finance / Insurance (BFSI)": "PDPA Consult, Pentest, Source Code Scan",
            "Healthcare": "PDPA Consult, Awareness Training, Backup Review",
            "Government / SOE": "Cyber Risk Assessment, อว3/อช3 Consult, TTX",
            "Software / Tech / SaaS": "Secure SDLC Advisory, Code Review, Pentest",
            "Telco / ISP": "Zero Trust Assessment, Managed CSOC, IRP",
            "Retail / SME / Logistics": "Phishing Simulation, Awareness Training, PDPA",
            "Manufacturing / OT-heavy": "Cyber Risk Assessment (OT), IRP, Backup/Restore Drill"
        }
        st.markdown(f"**Suggested Cybersecurity Services:** {services_map.get(sector, '-')}")
    else:
        st.error(f"❌ Classification failed: {confidence}")

