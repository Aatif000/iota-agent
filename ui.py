# Streamlit chat UI for the agent. Shows a tool bubble when a tool was used.

import streamlit as st
from agent import send_message

st.title("Iota Agent")

# Streamlit reruns this script on every interaction, so chat history must live in session_state to survive.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display all earlier messages on every rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

try:
    if prompt := st.chat_input("Ask something..."):

        # Returns the answer + tool details (if any)
        tool_response = send_message(prompt)

        # Show and store the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Tool bubble: only when the agent actually used a tool
        if tool_response["tool_used"]:
            tool_text = (
                f"Tool used -> {tool_response['tool_used']}\n\n"
                f"Input -> {tool_response['tool_input']}\n\n"
                f"Result -> {tool_response['tool_result']}"
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": tool_text})
            with st.chat_message("assistant"):
                st.write(tool_text)

        # Answer bubble: always shown, with or without a tool
        st.session_state.messages.append(
            {"role": "assistant", "content": tool_response["answer"]})
        with st.chat_message("assistant"):
            st.write(tool_response["answer"])

except Exception as e:
    st.write("Something went wrong.", e)
