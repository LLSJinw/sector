import streamlit as st
import requests

# ✅ Define the API call function first
def resolve_company_to_domain(company_name, api_key):
    url = "https://api.companyurlfinder.com/api/v1/services/name_to_domain"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "company_name": company_name,
        "country_code": "TH"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") and result.get("domain"):
            return result["domain"], result["company_name"]
    return None, None

# ✅ Streamlit app section
st.title("🌐 Company Name → Domain Resolver")

company = st.text_input("Enter company name (e.g., SCG, PTT Chem):")

if st.button("Find Domain"):
    domain, official_name = resolve_company_to_domain(
        company,
        "yrMP8nnBRROs77XL9XFj8xAFQr3LpP8r8pVOTiag"  # ✅ your working API key
    )
    if domain:
        st.success(f"✅ Domain: `{domain}`")
        st.markdown(f"**Official Name:** {official_name}")
    else:
        st.error("❌ No match found or invalid response.")
