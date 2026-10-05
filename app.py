import streamlit as st
from llm import ask

st.set_page_config(page_title="TeachBack", page_icon="🎓")
st.title("🎓 TeachBack")
st.caption("Learn by teaching: explain a concept to a curious classmate.")

SYSTEM = """You are Sam, a curious classmate who knows NOTHING about "{topic}".
A student is teaching it to you.
Rules:
- Ask exactly ONE short follow-up question at a time.
- Ask about things that were vague, skipped, or that seem to be missing a link between ideas.
- Never explain the topic yourself and never give the answer.
- If something the student says sounds wrong, don't correct it. Just say you're confused and ask them to explain again.
- Keep replies under 3 sentences. Be friendly and casual."""

topic = st.text_input("What topic will you teach?", placeholder="e.g. photosynthesis")

if "messages" not in st.session_state:
    st.session_state.messages = [] # chat history

if st.button("Start over"): # clear history
    st.session_state.messages = []
    st.rerun()

if topic:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): # draw avatar
            st.markdown(m["content"]) # redraw conversation after reruns

    if prompt := st.chat_input("Explain it to Sam..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Sam is thinking..."):
                history = [{"role": "system", "content": SYSTEM.format(topic=topic)}]
                history += st.session_state.messages
                reply = ask(history)
            st.markdown(reply) # display response
        st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("Enter a topic above to begin.")