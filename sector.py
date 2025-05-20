import streamlit as st
import requests

st.markdown("### 🌐 Company Name → Domain Resolver")
company = st.text_input("Enter company name to find domain:")
if st.button("Find Domain"):
    domain, official_name = resolve_company_to_domain(company, "yrMP8nnBRROs77XL9XFj8xAFQr3LpP8r8pVOTiag")
    if domain:
        st.success(f"✅ Domain: {domain}")
        st.markdown(f"**Official Name:** {official_name}")
    else:
        st.error("❌ No match found.")
