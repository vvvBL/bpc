import json
import requests
import streamlit as st
from google.oauth2 import service_account

# Function to load credentials and generate access token using Streamlit Secrets
def get_access_token():
    # Convert the AttrDict to a JSON string
    gcp_credentials = st.secrets["gcp_service_account"]
    gcp_credentials_json = json.dumps(gcp_credentials)
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(gcp_credentials_json), scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    access_token_info = credentials.with_claims(audience="https://discoveryengine.googleapis.com/")
    access_token = access_token_info.token
    return access_token

# Function to make API call
def make_api_call(query):
    access_token = get_access_token()
    url = "https://discoveryengine.googleapis.com/v1alpha/projects/418296190033/locations/global/collections/default_collection/dataStores/sop-files_1718096167786/servingConfigs/default_search:search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "pageSize": 10,
        "queryExpansionSpec": {"condition": "AUTO"},
        "spellCorrectionSpec": {"mode": "AUTO"},
        "contentSearchSpec": {
            "summarySpec": {
                "ignoreAdversarialQuery": True,
                "includeCitations": True,
                "summaryResultCount": 5,
                "modelSpec": {"version": "gemini-1.0-pro-002/answer_gen/v1"}
            },
            "snippetSpec": {"returnSnippet": True},
            "extractiveContentSpec": {"maxExtractiveAnswerCount": 1}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Streamlit app
def main():
    st.title("SOP Search")
    query = st.text_input("Enter your query:")
    if st.button("Search"):
        if query:
            st.write(f"Searching for: {query}")
            # Make API call
            api_response = make_api_call(query)
            # Display results
            if "answers" in api_response:
                for answer in api_response["answers"]:
                    reference_file = answer.get("referenceFile", "No reference file available")
                    extractive_content = answer.get("extractiveContent", {}).get("extractiveAnswer", [])
                    answer_text = extractive_content[0]["text"] if extractive_content else "No answer available"
                    st.write(f"Reference File: {reference_file}")
                    st.write(f"Answer: {answer_text}")
            else:
                st.write("No answers found.")
        else:
            st.write("Please enter a query.")

if __name__ == "__main__":
    main()
