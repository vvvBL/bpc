import json
import requests
import streamlit as st
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Function to load credentials and generate access token using Streamlit Secrets
def get_access_token():
    # Read the credentials from Streamlit secrets directly as a dictionary
    gcp_credentials = st.secrets["gcp_service_account"]
    
    # Load the credentials using google.oauth2 service_account
    credentials = service_account.Credentials.from_service_account_info(
        gcp_credentials, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    # Ensure the credentials are valid and refresh if necessary
    credentials.refresh(Request())
    
    # Generate an access token
    access_token = credentials.token
    st.write(f"Access Token: {access_token}")  # Log the access token for debugging (remove in production)
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

    # Log the request data
    st.write(f"Request data: {json.dumps(data, indent=2)}")

    response = requests.post(url, headers=headers, json=data)

    # Log the response
    st.write(f"Response status code: {response.status_code}")
    st.write(f"Response text: {response.text}")

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

            # Check if there's a summary
            if "summary" in api_response and "summaryText" in api_response["summary"]:
                summary_text = api_response["summary"]["summaryText"]
                st.write(f"Summary: {summary_text}")

            if "results" in api_response and api_response["results"]:
                for result in api_response["results"]:
                    doc = result["document"]
                    title = doc["derivedStructData"].get("title", "No title available")
                    link = doc["derivedStructData"].get("link", "No link available")
                    st.write(f"Title: {title}")
                    st.write(f"Link: {link}")
            else:
                st.write("No relevant answers found.")
        else:
            st.write("Please enter a query.")

if __name__ == "__main__":
    main()
