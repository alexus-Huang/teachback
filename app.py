import streamlit as st
from llm import ask
from concepts import get_key_concepts
from scoring import score_coverage

st.set_page_config(page_title="TeachBack", page_icon="🎓")
st.title("🎓 TeachBack")
st.caption("Learn by teaching: explain a concept to a curious classmate.")

SYSTEM = """You are Sam, a curious classmate who knows NOTHING about "{topic}".
A student is teaching it to you.
Rules:
- Ask exactly ONE short follow-up question at a time.
- Ask about things that were vague, skipped, or missing a link between ideas.
- Never explain the topic yourself and never give the answer.
- If something sounds wrong, don't correct it. Say you're confused and ask them to explain again.
- Keep replies under 3 sentences. Be friendly and casual.

These ideas have NOT been explained yet. Steer your next question toward ONE of them,
without revealing or hinting at the answer:
{missing}"""

for key, default in [("messages", []), ("concepts", []), ("concepts_topic", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

threshold = st.sidebar.slider("Match strictness", 0.30, 0.80, 0.45, 0.05)
reveal = st.sidebar.checkbox("Reveal missing ideas")

topic = st.text_input("What topic will you teach?", placeholder="e.g. photosynthesis")

if topic and topic != st.session_state.concepts_topic:
    with st.spinner("Preparing the key ideas..."):
        st.session_state.concepts = get_key_concepts(topic)
    st.session_state.concepts_topic = topic
    st.session_state.messages = []

if st.button("Start over"):
    st.session_state.messages = []
    st.rerun()


def student_text():
    return " ".join(m["content"] for m in st.session_state.messages if m["role"] == "user")


concepts = st.session_state.concepts

if topic and not concepts:
    st.error("Couldn't generate key ideas. Try rephrasing the topic.")
elif topic:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Explain it to Sam..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        results = score_coverage(student_text(), concepts, threshold)
        missing = [r["concept"] for r in results if not r["covered"]]
        missing_text = "\n".join(f"- {c}" for c in missing) or "- (all covered; ask them to connect two ideas)"

        with st.chat_message("assistant"):
            with st.spinner("Sam is thinking..."):
                system = SYSTEM.format(topic=topic, missing=missing_text)
                history = [{"role": "system", "content": system}] + st.session_state.messages
                reply = ask(history)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    results = score_coverage(student_text(), concepts, threshold)
    covered = sum(r["covered"] for r in results)
    with st.sidebar:
        st.header("Concept coverage")
        st.progress(covered / len(results))
        st.write(f"{covered} of {len(results)} key ideas explained")
        for r in results:
            if r["covered"]:
                st.write(f"✅ {r['concept']}")
            elif reveal:
                st.write(f"⬜ {r['concept']}")
            else:
                st.write("⬜ ???")
else:
    st.info("Enter a topic above to begin.")