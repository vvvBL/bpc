import streamlit as st
import requests

# Function to make API call
def make_api_call(query):
    url = "https://discoveryengine.googleapis.com/v1alpha/projects/418296190033/locations/global/collections/default_collection/dataStores/sop-files_1718096167786/servingConfigs/default_search:search"
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",  # Replace with your access token logic
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
            if api_response.get("answers"):
                for answer in api_response["answers"]:
                    reference_file = answer["referenceFile"]
                    answer_text = answer["extractiveContent"]["extractiveAnswer"][0]["text"]
                    st.write(f"Reference File: {reference_file}")
                    st.write(f"Answer: {answer_text}")
            else:
                st.write("No answers found.")
        else:
            st.write("Please enter a query.")

if __name__ == "__main__":
    main()