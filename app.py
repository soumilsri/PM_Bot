import streamlit as st
import os
from aha_api import AhaAPI
from main import groom_features, generate_product_summary, generate_openai_summary
from rich.table import Table

st.set_page_config(page_title="Product Management Bot", layout="wide")
st.title("🛠️ Product Management Bot")

# User inputs
def get_user_inputs():
    base_url = st.text_input("Aha! base URL", "https://yourcompany.aha.io")
    product_id = st.text_input("Aha! Product ID")
    openai_api_key = st.text_input("OpenAI API Key (optional)", type="password")
    return base_url, product_id, openai_api_key

base_url, product_id, openai_api_key = get_user_inputs()

if st.button("Fetch Stories"):
    if not base_url or not product_id:
        st.error("Please enter both Aha! base URL and Product ID.")
    else:
        # Set OpenAI key if provided
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        try:
            api = AhaAPI(base_url)
            data = api.fetch_features(product_id)
            features = data.get('features', [])
            if not features:
                st.warning("No features found for this product.")
            else:
                groomed = groom_features(features)
                # Display table
                st.subheader("Groomed Aha! Features")
                st.dataframe(groomed)
                # Show summary
                ai_summary = generate_openai_summary(features)
                if ai_summary:
                    st.markdown(f"**AI Product Summary:**\n{ai_summary}")
                else:
                    summary = generate_product_summary(features)
                    st.markdown(f"**Product Summary (Top Keywords):** {summary}")
        except Exception as e:
            st.error(f"Error: {e}") 