import streamlit as st
import requests
import sseclient
import json
import logging

def serve_chatbot():
    # Configure logging
    # logging.basicConfig(level=logging.DEBUG, filename='chatbot.log', filemode='w', format='%(asctime)s - %(message)s')

    st.title("Rag Intro Chat")

    # Function to send user query to the /query endpoint and handle streaming response
    def get_chat_response(query):
        url = "http://localhost:5000/query"  # Replace with your actual endpoint URL
        headers = {"Content-Type": "application/json"}
        data = {"query": query}

        # Initialize the request to the server
        response = requests.post(url, headers=headers, json=data, stream=True)

        # Check if the response is successful
        if response.status_code != 200:
            st.error("Error: Unable to get a valid response from the server.")
            return

        # Parse the server-sent events (SSE)
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                logging.debug(f"Raw line: {decoded_line}")  # Log the raw line
                if decoded_line.startswith("data: "):
                    data = json.loads(decoded_line[len("data: "):])
                    response_chunk = data.get("response", "")
                    logging.debug(f"Response chunk: {response_chunk}")  # Log the response chunk
                    yield response_chunk

    def escape_markdown(text):
        # List of characters to escape in Markdown
        escape_chars = ['$']
        # Replace each character with its escaped version
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(escape_markdown(message["content"]))

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(escape_markdown(prompt))
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response_container = st.empty()
            complete_response = ""
            for chunk in get_chat_response(prompt):
                complete_response = chunk
                logging.debug(f"Complete response: {complete_response}")  # Log the complete response so far
                response_container.markdown(escape_markdown(complete_response))
        
        st.session_state.messages.append({"role": "assistant", "content": complete_response})