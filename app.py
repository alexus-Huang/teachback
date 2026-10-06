import streamlit as st
from llm import ask
from concepts import get_key_concepts, get_concept_links
from grader import evaluate
from mapviz import build_dot

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

for key, default in [("messages", []), ("concepts", []), ("links", []), ("concepts_topic", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

reveal = st.sidebar.checkbox(
    "Reveal missing ideas",
    help="Show the key ideas you haven't explained yet. Off by default so you have to recall them yourself.",
)

with st.sidebar.expander("Advanced settings"):
    threshold = st.slider(
        "Idea matching strictness",
        0.15, 0.80, 0.35, 0.05,
        help="Backup grading only. If the AI check is unavailable, an idea counts as explained when your wording is at least this similar in meaning. Higher = stricter, lower = more forgiving.",
    )
    link_threshold = st.slider(
        "Link matching strictness",
        0.25, 0.80, 0.40, 0.05,
        help="Same as above, but for the connections in the concept map.",
    )
    debug = st.checkbox(
        "Show scores",
        help="Display each idea's similarity score and the grader's verdict. Useful for testing.",
    )

level = st.selectbox(
    "Learner level",
    ["Elementary school", "Middle school", "High school", "College"],
    index=1,
)
topic = st.text_input("What topic will you teach?", placeholder="e.g. photosynthesis")

state_key = f"{topic}|{level}"
if topic and state_key != st.session_state.concepts_topic:
    with st.spinner("Preparing the key ideas..."):
        st.session_state.concepts = get_key_concepts(topic, level=level)
        st.session_state.links = get_concept_links(topic)
    st.session_state.concepts_topic = state_key
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

        results = evaluate(student_text(), concepts, threshold)
        missing = [r["concept"] for r in results if not r["covered"]]
        missing_text = "\n".join(f"- {c}" for c in missing) or "- (all covered; ask them to connect two ideas)"

        with st.chat_message("assistant"):
            with st.spinner("Sam is thinking..."):
                system = SYSTEM.format(topic=topic, missing=missing_text)
                history = [{"role": "system", "content": system}] + st.session_state.messages
                reply = ask(history)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    results = evaluate(student_text(), concepts, threshold)
    covered = sum(r["covered"] for r in results)
    with st.sidebar:
        st.header("Concept coverage")
        st.progress(covered / len(results))
        st.write(f"{covered} of {len(results)} key ideas explained")
        ICONS = {"explained": "✅", "mentioned": "🟡", "incorrect": "❌", "missing": "⬜"}
        for r in results:
            score = f" ({r['score']:.2f})" if debug else ""
            if r["status"] == "missing" and not reveal:
                st.write(f"⬜ ???{score}")
            else:
                st.write(f"{ICONS[r['status']]} {r['concept']}{score}")
                if r["reason"]:
                    st.caption(r["reason"])

    links = st.session_state.links
    if links:
        link_sentences = [f"{l['from']} {l['relation']} {l['to']}" for l in links]
        link_results = evaluate(student_text(), link_sentences, link_threshold)
        linked = sum(r["covered"] for r in link_results)
        with st.expander("🗺️ Concept map", expanded=True):
            st.caption(f"{linked} of {len(links)} connections explained. Green = explained, orange = named only, red = not quite right, dashed grey = missing.")
            st.graphviz_chart(build_dot(links, link_results, reveal))
            if debug:
                for sentence, r in zip(link_sentences, link_results):
                    st.write(f"{r['score']:.2f} {r['status']}: {sentence}")
else:
    st.info("Enter a topic above to begin.")