import os

import streamlit as st
import wikipediaapi
from google import genai
from google.genai import types


st.set_page_config(
    page_title="WikiAgent — Wikipedia research",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --bg:#050607; --surface:#0a0c10; --border:#2a2f37; --muted:#9299a5; --text:#f4f6f8; --blue:#74a9ff; }
    .stApp { background:var(--bg); color:var(--text); }
    .stApp:before { content:""; position:fixed; z-index:-1; inset:94px 0 0; pointer-events:none;
      background:radial-gradient(ellipse 42% 42% at 47% 48%, rgba(34,112,223,.31), transparent 72%),
      radial-gradient(ellipse 25% 23% at 61% 69%, rgba(114,94,234,.23), transparent 72%),
      linear-gradient(rgba(255,255,255,.018) 1px, transparent 1px),linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
      background-size:auto,auto,32px 32px,32px 32px; }
    #MainMenu, footer, header { visibility:hidden; }
    .block-container { max-width:1232px; padding:0 2rem 6.5rem; }
    section[data-testid="stSidebar"] { background:#080a0d; border-right:1px solid var(--border); }
    section[data-testid="stSidebar"] > div { padding:1.25rem .85rem; }
    .brand { display:flex; align-items:center; gap:10px; font-size:18px; font-weight:650; letter-spacing:-.035em; }
    .brand-mark { width:24px; height:24px; display:grid; place-items:center; border:1px solid #e7ebf1; border-radius:7px; font-size:12px; }
    .side-label { color:#6f7884; font-size:10px; letter-spacing:.13em; text-transform:uppercase; margin:1.75rem .55rem .55rem; }
    section[data-testid="stSidebar"] .stButton button { justify-content:flex-start; min-height:38px; padding:0 11px; border:1px solid transparent; background:transparent; color:#b2bac5; border-radius:4px; font-size:13px; transition:background .18s,border-color .18s,color .18s; }
    section[data-testid="stSidebar"] .stButton button:hover { border-color:#353c46; background:#10141a; color:#fff; }
    .topnav { height:94px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border); }
    .navlinks { display:flex; gap:30px; margin-left:88px; flex:1; color:#9299a5; font-size:14px; }
    .navlinks span:first-child { color:#fff; }
    .top-status { color:#afb7c2; font-size:12px; display:flex; align-items:center; gap:7px; }
    .top-status:before { content:""; width:6px; height:6px; background:#69d598; border-radius:50%; box-shadow:0 0 9px #69d598; }
    .hero { max-width:850px; margin:0 auto; padding:104px 12px 28px; text-align:center; }
    .eyebrow { color:#a1a9b6; font-size:10px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; }
    .hero h1 { margin:17px 0 0; color:#f8fafc; font-size:clamp(43px,5.3vw,68px); font-weight:520; letter-spacing:-.065em; line-height:1.02; }
    .hero p { max-width:610px; margin:24px auto 0; color:#c5ccd7; font-size:16px; line-height:1.56; }
    div[data-testid="stVerticalBlockBorderWrapper"] { margin-top:30px; border:1px solid #505966; border-radius:0; background:rgba(8,10,14,.92); box-shadow:0 17px 55px rgba(0,0,0,.38); }
    .control-title { padding:5px 9px 11px; color:#aab4c1; font-size:12px; text-align:left; }
    div[data-testid="stFileUploader"] { padding:0; }
    div[data-testid="stFileUploaderDropzone"] { min-height:85px; background:#0b0e13; border:1px dashed #424b58; border-radius:2px; }
    div[data-testid="stFileUploaderDropzone"] span, div[data-testid="stFileUploaderDropzone"] small { color:#acb5c0 !important; }
    div[data-testid="stFileUploaderDropzone"] button { border:1px solid #56616f; border-radius:2px; background:#121720; color:#edf2f8; }
    .upload-note { max-width:610px; margin:10px auto 0; color:#8a94a1; font-size:11px; line-height:1.45; }
    div[data-testid="stMain"] .stButton button { min-height:31px; border:1px solid #343b45; border-radius:3px; background:rgba(9,12,16,.75); color:#aeb7c3; font-size:12px; transition:border-color .18s,background .18s,color .18s; }
    div[data-testid="stMain"] .stButton button:hover { border-color:#668dca; background:#111925; color:#fff; }
    .feature-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; max-width:850px; margin:42px auto 0; }
    .feature { min-height:119px; padding:18px; text-align:left; border:1px solid rgba(118,132,150,.3); background:rgba(9,12,16,.72); }
    .feature-number { color:#7cafff; font:11px monospace; }
    .feature h3 { margin:13px 0 7px; color:#eff3f7; font-size:14px; font-weight:600; }
    .feature p { margin:0; color:#919ba8; font-size:12px; line-height:1.48; }
    .conversation { max-width:880px; margin:42px auto 0; }
    .message-user { display:flex; justify-content:flex-end; margin:20px 0; }
    .user-bubble { max-width:78%; padding:11px 14px; border:1px solid #354150; border-radius:8px 2px 8px 8px; background:#101722; color:#edf3fb; font-size:14px; line-height:1.5; }
    .assistant-meta { margin-top:28px; color:#96a3b3; font-size:10px; letter-spacing:.13em; text-transform:uppercase; }
    .assistant-answer { padding:12px 0 4px; color:#e6ebf2; font-size:15px; line-height:1.7; }
    .source-card { margin-top:15px; padding:14px 16px; border:1px solid #2d3540; border-left:2px solid #6c9eff; background:rgba(10,14,20,.86); }
    .source-label { color:#8491a1; font-size:10px; letter-spacing:.13em; text-transform:uppercase; }
    .source-title { display:block; margin-top:6px; color:#eff5fd; font-size:14px; font-weight:600; text-decoration:none; }
    .source-url { color:#7aaeff; font-size:12px; text-decoration:none; }
    div[data-testid="stChatInput"] { max-width:880px; margin:0 auto; }
    div[data-testid="stChatInput"] textarea { min-height:54px; border:1px solid #4d5867 !important; border-radius:2px !important; background:#080b10 !important; color:#eff4fa !important; }
    div[data-testid="stChatInput"] textarea::placeholder { color:#8d98a6; }
    div[data-testid="stChatInput"] button { border-radius:1px !important; background:#f4f6f8 !important; color:#111820 !important; }
    .stStatus { max-width:880px; margin:18px auto; border:1px solid #303a47; border-radius:2px; background:#0a0e14; }
    @media (max-width:760px) { .block-container { padding:0 1rem 6rem; } .navlinks { display:none; } .hero { padding-top:70px; } .feature-grid { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)
wiki = wikipediaapi.Wikipedia(user_agent="WikiAgent/1.0", language="en")


def wikipedia_search_candidates(query, limit=5):
    search_results = wiki.search(query, limit=limit)
    if not search_results.pages:
        return []
    candidates = []
    for title in search_results.pages:
        page = wiki.page(title)
        if page.exists():
            candidates.append({"title": page.title, "summary": page.summary[:700], "url": page.fullurl})
    return candidates


def choose_best_wikipedia_article(question, candidates):
    if not candidates:
        return None
    candidate_text = ""
    for i, article in enumerate(candidates):
        candidate_text += f"""Candidate {i + 1}\n\nTitle:\n{article['title']}\n\nSummary:\n{article['summary']}\n\nURL:\n{article['url']}\n\n"""
    prompt = f"""You are selecting the best Wikipedia article for the user's question.
User question: {question}
Available Wikipedia articles:
{candidate_text}
Choose the single most relevant article. Return ONLY the candidate number."""
    response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt)
    try:
        number = int(response.text.strip())
        if 1 <= number <= len(candidates):
            return candidates[number - 1]
    except:
        pass
    return candidates[0]


def smart_wikipedia_search(query):
    try:
        candidates = wikipedia_search_candidates(query, limit=5)
        if not candidates:
            return {"status": "error", "message": "No relevant Wikipedia article found."}
        selected = choose_best_wikipedia_article(query, candidates)
        if selected is None:
            return {"status": "error", "message": "Could not select a relevant article."}
        return {"status": "success", "title": selected["title"], "summary": selected["summary"], "url": selected["url"]}
    except Exception as error:
        return {"status": "error", "message": "Wikipedia search failed.", "details": str(error)}


wikipedia_tool = {
    "name": "smart_wikipedia_search",
    "description": "Searches Wikipedia for information relevant to the user's question and selects the most appropriate article.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "The topic or question to search on Wikipedia."}}, "required": ["query"]},
}
tools = types.Tool(function_declarations=[wikipedia_tool])
config = types.GenerateContentConfig(tools=[tools])


def build_conversation_context(messages):
    return "".join(f"{message['role'].capitalize()}: {message['content']}\n\n" for message in messages)


def wikipedia_agent(question, messages):
    conversation_context = build_conversation_context(messages)
    prompt = f"""You are WikiAgent, an AI-powered Wikipedia research assistant.
Use the conversation history to understand follow-up questions. If factual Wikipedia information is needed, use the Wikipedia search tool. Do not invent facts.
Conversation history:
{conversation_context}
Current question:
{question}"""
    response = client.models.generate_content(model="gemini-3.1-flash-lite", contents=prompt, config=config)
    if not response.function_calls:
        return {"answer": response.text, "source": None}
    call = response.function_calls[0]
    result = smart_wikipedia_search(call.args["query"])
    if result["status"] == "error":
        return {"answer": result["message"], "source": None}
    function_response = types.Part.from_function_response(name=call.name, response=result)
    final_prompt = f"""You are WikiAgent. Answer the user's question using the retrieved Wikipedia information.
Conversation:
{conversation_context}
Question:
{question}
Wikipedia article:
{result['title']}
Wikipedia information:
{result['summary']}
Rules:
- Give a clear answer.
- Use conversation context.
- Resolve pronouns such as he/she/they.
- Do not invent facts.
- If information is insufficient, say so."""
    final_response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=final_prompt)]), response.candidates[0].content, types.Content(role="user", parts=[function_response])],
        config=config,
    )
    return {"answer": final_response.text, "source": {"title": result["title"], "url": result["url"]}}


if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">◈</span> WikiAgent</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">Research workspace</div>', unsafe_allow_html=True)
    if st.button("⌕  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown('<div class="side-label">Capabilities</div>', unsafe_allow_html=True)
    st.caption("Wikipedia retrieval")
    st.caption("Gemini article selection")
    st.caption("Grounded citations")
    st.markdown('<div class="side-label">Conversation</div>', unsafe_allow_html=True)
    if st.button("⌫  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


st.markdown("""<div class="topnav"><div class="brand"><span class="brand-mark">◈</span> WikiAgent</div>
<div class="navlinks"><span>Research</span><span>Sources</span><span>Workspace</span></div>
<div class="top-status">Gemini connected</div></div>""", unsafe_allow_html=True)

example_question = None

if not st.session_state.messages:
    st.markdown("""<section class="hero"><div class="eyebrow">Wikipedia research assistant</div>
    <h1>Ask anything from your<br>research workspace.</h1>
    <p>Explore Wikipedia with an AI research assistant that finds relevant sources, evaluates context, and gives you a clear answer.</p></section>""", unsafe_allow_html=True)
    _, workspace_column, _ = st.columns([1, 2.1, 1])
    with workspace_column:
        with st.container(border=True):
            st.markdown('<div class="control-title">Add research documents</div>', unsafe_allow_html=True)
            uploaded_documents = st.file_uploader(
                "Add research documents",
                type=["pdf", "txt", "md", "docx"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                help="Upload controls are available for your workspace. The current RAG pipeline grounds answers in Wikipedia.",
            )
        if uploaded_documents:
            file_names = ", ".join(document.name for document in uploaded_documents)
            st.markdown(f'<div class="upload-note">Selected for this workspace: {file_names}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="upload-note">Upload PDF, TXT, Markdown, or DOCX files for your workspace. WikiAgent currently retrieves answer sources from Wikipedia.</div>', unsafe_allow_html=True)
        example_columns = st.columns(3)
        suggestions = [
            "Who was Alan Turing?",
            "Explain the theory of relativity",
            "What is artificial intelligence?",
        ]
        for column, suggestion in zip(example_columns, suggestions):
            with column:
                if st.button(suggestion, use_container_width=True):
                    example_question = suggestion
    st.markdown("""
    <section class="feature-grid"><article class="feature"><span class="feature-number">01</span><h3>Search</h3><p>Search Wikipedia with a question in your own words.</p></article>
    <article class="feature"><span class="feature-number">02</span><h3>Evaluate</h3><p>AI selects the most relevant article from the results.</p></article>
    <article class="feature"><span class="feature-number">03</span><h3>Ground answers</h3><p>Every retrieved answer includes its primary source.</p></article></section>""", unsafe_allow_html=True)

st.markdown('<main class="conversation">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="message-user"><div class="user-bubble">{message["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="assistant-meta">◈ &nbsp; WikiAgent</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-answer">{message["content"]}</div>', unsafe_allow_html=True)
        if message.get("source"):
            source = message["source"]
            st.markdown(f'<article class="source-card"><div class="source-label">Primary Wikipedia source</div><a class="source-title" href="{source["url"]}" target="_blank">{source["title"]} ↗</a><a class="source-url" href="{source["url"]}" target="_blank">Open article</a></article>', unsafe_allow_html=True)
st.markdown('</main>', unsafe_allow_html=True)

question = st.chat_input("Ask WikiAgent anything…")
if example_question:
    question = example_question
if question:
    st.markdown(f'<div class="conversation"><div class="message-user"><div class="user-bubble">{question}</div></div></div>', unsafe_allow_html=True)
    with st.status("WikiAgent is researching…", expanded=True):
        st.write("Understanding your question")
        st.write("Searching and evaluating Wikipedia")
        result = wikipedia_agent(question, st.session_state.messages.copy())
        st.write("Preparing a grounded answer")
    st.markdown('<div class="conversation"><div class="assistant-meta">◈ &nbsp; WikiAgent</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="conversation"><div class="assistant-answer">{result["answer"]}</div></div>', unsafe_allow_html=True)
    if result["source"]:
        source = result["source"]
        st.markdown(f'<div class="conversation"><article class="source-card"><div class="source-label">Primary Wikipedia source</div><a class="source-title" href="{source["url"]}" target="_blank">{source["title"]} ↗</a><a class="source-url" href="{source["url"]}" target="_blank">Open article</a></article></div>', unsafe_allow_html=True)
    st.session_state.messages.extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": result["answer"], "source": result["source"]},
    ])
    st.rerun()
