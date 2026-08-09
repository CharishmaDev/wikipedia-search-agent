import streamlit as st
from google import genai
from google.genai import types
import wikipediaapi
import os


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WikiAgent",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS — AI SaaS THEME
# ============================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(124, 58, 237, 0.18),
            transparent 35%
        ),
        #08080d;
    color: #f5f5f7;
}

.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 5rem;
}


/* ---------- HEADER ---------- */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0 25px 0;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;

    background:
        linear-gradient(
            135deg,
            #8b5cf6,
            #6366f1
        );

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 18px;
    font-weight: 700;

    box-shadow:
        0 0 25px rgba(139, 92, 246, 0.35);
}

.brand-name {
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -0.4px;
}

.brand-badge {
    font-size: 10px;
    padding: 4px 7px;
    border-radius: 20px;

    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.25);

    color: #b9a2ff;
}


/* ---------- HERO ---------- */

.hero {
    text-align: center;
    padding: 90px 20px 45px 20px;
}

.hero-badge {
    display: inline-block;

    padding: 7px 13px;
    border-radius: 30px;

    background: rgba(139, 92, 246, 0.10);
    border: 1px solid rgba(139, 92, 246, 0.25);

    color: #bca7ff;

    font-size: 12px;
    font-weight: 600;

    margin-bottom: 22px;
}

.hero h1 {
    font-size: clamp(42px, 6vw, 72px);

    line-height: 1.02;

    letter-spacing: -3px;

    margin: 0;

    font-weight: 800;

    background:
        linear-gradient(
            135deg,
            #ffffff 20%,
            #c4b5fd 55%,
            #818cf8 100%
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 620px;

    margin: 20px auto 0 auto;

    color: #9999a7;

    font-size: 17px;

    line-height: 1.6;
}


/* ---------- FEATURE CARDS ---------- */

.feature-card {
    height: 100%;

    padding: 22px;

    border-radius: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.045),
            rgba(255,255,255,0.018)
        );

    border: 1px solid rgba(255,255,255,0.08);

    transition: 0.2s ease;
}

.feature-icon {
    font-size: 22px;
    margin-bottom: 12px;
}

.feature-title {
    font-weight: 700;
    margin-bottom: 6px;
}

.feature-text {
    color: #888895;
    font-size: 13px;
    line-height: 1.5;
}


/* ---------- SUGGESTIONS ---------- */

.section-label {
    color: #777784;

    font-size: 12px;

    text-transform: uppercase;

    letter-spacing: 1.5px;

    font-weight: 700;

    margin: 35px 0 14px 0;
}


/* ---------- CHAT ---------- */

.user-message {
    display: flex;
    justify-content: flex-end;

    margin: 25px 0;
}

.user-bubble {
    max-width: 75%;

    padding: 14px 18px;

    border-radius: 18px 18px 5px 18px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #6366f1
        );

    color: white;

    box-shadow:
        0 8px 30px rgba(99,102,241,0.18);
}

.ai-label {
    display: flex;
    align-items: center;

    gap: 9px;

    color: #b7a1ff;

    font-size: 13px;

    font-weight: 700;

    margin-bottom: 12px;
}

.ai-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #a78bfa;

    box-shadow:
        0 0 12px #8b5cf6;
}

.answer-text {
    color: #e5e5eb;

    font-size: 16px;

    line-height: 1.75;
}


/* ---------- SOURCE ---------- */

.source-card {
    margin-top: 22px;

    padding: 18px;

    border-radius: 15px;

    background:
        rgba(255,255,255,0.025);

    border: 1px solid rgba(255,255,255,0.08);
}

.source-label {
    font-size: 10px;

    letter-spacing: 1.3px;

    color: #777784;

    text-transform: uppercase;

    margin-bottom: 8px;
}

.source-title {
    font-weight: 700;

    color: #eeeeef;

    margin-bottom: 5px;
}

.source-link {
    color: #a78bfa;

    text-decoration: none;

    font-size: 13px;
}


/* ---------- STATUS ---------- */

.status-card {
    padding: 14px 18px;

    border-radius: 12px;

    background: rgba(139,92,246,0.07);

    border: 1px solid rgba(139,92,246,0.15);

    color: #aaa3bb;

    font-size: 13px;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #0c0c12;
    border-right: 1px solid rgba(255,255,255,0.07);
}


/* ---------- CHAT INPUT ---------- */

.stChatInput {
    border-color: rgba(139,92,246,0.3) !important;
}


/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 12px;

    border: 1px solid rgba(255,255,255,0.08);

    background: rgba(255,255,255,0.035);

    color: #dcdce5;

    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: rgba(139,92,246,0.5);

    background: rgba(139,92,246,0.10);

    color: white;
}


/* ---------- MOBILE ---------- */

@media (max-width: 768px) {

    .hero {
        padding-top: 50px;
    }

    .hero h1 {
        letter-spacing: -2px;
    }

    .user-bubble {
        max-width: 90%;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key is not configured.")
    st.stop()

client = genai.Client(
    api_key=GEMINI_API_KEY
)

wiki = wikipediaapi.Wikipedia(
    user_agent="WikiAgent/1.0",
    language="en"
)


# ============================================================
# WIKIPEDIA SEARCH
# ============================================================

def wikipedia_search_candidates(query, limit=5):

    search_results = wiki.search(
        query,
        limit=limit
    )

    if not search_results.pages:
        return []

    candidates = []

    for title in search_results.pages:

        page = wiki.page(title)

        if page.exists():

            candidates.append({
                "title": page.title,
                "summary": page.summary[:700],
                "url": page.fullurl
            })

    return candidates


# ============================================================
# SELECT BEST ARTICLE
# ============================================================

def choose_best_wikipedia_article(
    question,
    candidates
):

    if not candidates:
        return None

    candidate_text = ""

    for i, article in enumerate(candidates):

        candidate_text += f"""
Candidate {i + 1}

Title:
{article['title']}

Summary:
{article['summary']}

URL:
{article['url']}

"""

    prompt = f"""
You are selecting the best Wikipedia article
for the user's question.

User question:
{question}

Available Wikipedia articles:

{candidate_text}

Choose the single most relevant article.

Return ONLY the candidate number.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    try:

        number = int(
            response.text.strip()
        )

        if 1 <= number <= len(candidates):

            return candidates[number - 1]

    except:

        pass

    return candidates[0]


# ============================================================
# WIKIPEDIA TOOL
# ============================================================

def smart_wikipedia_search(query):

    try:

        candidates = wikipedia_search_candidates(
            query,
            limit=5
        )

        if not candidates:

            return {
                "status": "error",
                "message":
                "No relevant Wikipedia article found."
            }

        selected = choose_best_wikipedia_article(
            query,
            candidates
        )

        if selected is None:

            return {
                "status": "error",
                "message":
                "Could not select a relevant article."
            }

        return {
            "status": "success",
            "title": selected["title"],
            "summary": selected["summary"],
            "url": selected["url"]
        }

    except Exception as e:

        return {
            "status": "error",
            "message":
            "Wikipedia search failed.",
            "details": str(e)
        }


# ============================================================
# TOOL DEFINITION
# ============================================================

wikipedia_tool = {

    "name":
    "smart_wikipedia_search",

    "description":
    """
    Searches Wikipedia for information relevant
    to the user's question and selects the most
    appropriate article.
    """,

    "parameters": {

        "type": "object",

        "properties": {

            "query": {

                "type": "string",

                "description":
                "The topic or question to search on Wikipedia."

            }

        },

        "required":
        ["query"]
    }
}


tools = types.Tool(
    function_declarations=[
        wikipedia_tool
    ]
)

config = types.GenerateContentConfig(
    tools=[tools]
)


# ============================================================
# CONVERSATION CONTEXT
# ============================================================

def build_conversation_context(messages):

    context = ""

    for message in messages:

        context += (
            f"{message['role'].capitalize()}: "
            f"{message['content']}\n\n"
        )

    return context


# ============================================================
# AI AGENT
# ============================================================

def wikipedia_agent(
    question,
    messages
):

    conversation_context = \
        build_conversation_context(messages)

    prompt = f"""
You are WikiAgent, an AI-powered Wikipedia
research assistant.

Use the conversation history to understand
follow-up questions.

If factual Wikipedia information is needed,
use the Wikipedia search tool.

Do not invent facts.

Conversation history:

{conversation_context}

Current question:

{question}
"""

    response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=prompt,

        config=config
    )


    if not response.function_calls:

        return {
            "answer": response.text,
            "source": None
        }


    call = response.function_calls[0]

    query = call.args["query"]


    result = smart_wikipedia_search(query)


    if result["status"] == "error":

        return {
            "answer": result["message"],
            "source": None
        }


    function_response = \
        types.Part.from_function_response(

            name=call.name,

            response=result

        )


    final_prompt = f"""
You are WikiAgent.

Answer the user's question using
the retrieved Wikipedia information.

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
- If information is insufficient, say so.
"""


    final_response = client.models.generate_content(

        model="gemini-3.1-flash-lite",

        contents=[

            types.Content(

                role="user",

                parts=[

                    types.Part.from_text(
                        text=final_prompt
                    )

                ]

            ),

            response.candidates[0].content,

            types.Content(

                role="user",

                parts=[

                    function_response

                ]

            )

        ],

        config=config
    )


    return {

        "answer":
        final_response.text,

        "source": {

            "title":
            result["title"],

            "url":
            result["url"]

        }

    }


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# TOP BAR
# ============================================================

st.markdown("""
<div class="topbar">

    <div class="brand">

        <div class="brand-icon">
            ✦
        </div>

        <div class="brand-name">
            WikiAgent
        </div>

        <div class="brand-badge">
            AI RESEARCH
        </div>

    </div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ✦ WikiAgent")

    st.caption(
        "AI-powered Wikipedia research assistant"
    )

    st.divider()

    st.markdown("### Capabilities")

    st.markdown("""
    🔎 **Smart Wikipedia Search**

    🧠 **AI Article Selection**

    💬 **Conversation Memory**

    📚 **Source Attribution**

    🤖 **Gemini Tool Calling**
    """)

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# EMPTY STATE / HERO
# ============================================================

if not st.session_state.messages:

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            ✦ AI-POWERED KNOWLEDGE SEARCH
        </div>

        <h1>
            Explore knowledge.<br>
            Understand anything.
        </h1>

        <p>
            Ask a question in natural language.
            WikiAgent searches Wikipedia, evaluates
            relevant information, and gives you a
            clear answer with its source.
        </p>

    </div>
    """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # FEATURE CARDS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="feature-card">

            <div class="feature-icon">
                🔎
            </div>

            <div class="feature-title">
                Search
            </div>

            <div class="feature-text">
                Search across relevant Wikipedia
                articles using natural language.
            </div>

        </div>
        """, unsafe_allow_html=True)


    with col2:

        st.markdown("""
        <div class="feature-card">

            <div class="feature-icon">
                🧠
            </div>

            <div class="feature-title">
                Understand
            </div>

            <div class="feature-text">
                AI evaluates search results and
                selects the most relevant article.
            </div>

        </div>
        """, unsafe_allow_html=True)


    with col3:

        st.markdown("""
        <div class="feature-card">

            <div class="feature-icon">
                📚
            </div>

            <div class="feature-title">
                Cite
            </div>

            <div class="feature-text">
                Every research answer includes
                its Wikipedia source.
            </div>

        </div>
        """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # EXAMPLES
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">Try asking</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🧠  Who was Alan Turing?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "Who was Alan Turing?"

            st.rerun()


    with col2:

        if st.button(
            "🤖  What is artificial intelligence?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "What is artificial intelligence?"

            st.rerun()


    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📞  Who invented the telephone?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "Who invented the telephone?"

            st.rerun()


    with col2:

        if st.button(
            "🌌  Explain the theory of relativity",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "Explain the theory of relativity"

            st.rerun()


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            '<div class="user-message">'
            f'<div class="user-bubble">'
            f'{message["content"]}'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown("""
        <div class="ai-label">

            <div class="ai-dot"></div>

            WikiAgent

        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div class="answer-text">'
            f'{message["content"]}'
            f'</div>',
            unsafe_allow_html=True
        )

        if message.get("source"):

            source = message["source"]

            st.markdown(
                f"""
                <div class="source-card">

                    <div class="source-label">
                        Primary source
                    </div>

                    <div class="source-title">
                        📚 {source["title"]}
                    </div>

                    <div>
                        <span
                        style="color:#777784;
                        font-size:12px;">
                        Wikipedia
                        </span>
                    </div>

                    <br>

                    <a
                    class="source-link"
                    href="{source["url"]}"
                    target="_blank">

                    Open Wikipedia article ↗

                    </a>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# INPUT
# ============================================================

example_question = \
    st.session_state.pop(
        "example_question",
        None
    )


question = st.chat_input(
    "Ask WikiAgent anything..."
)


if example_question:

    question = example_question


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # User message

    st.markdown(
        '<div class="user-message">'
        f'<div class="user-bubble">'
        f'{question}'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    # Save temporarily for context

    current_messages = \
        st.session_state.messages.copy()


    # Agent status

    with st.status(
        "✦ WikiAgent is working...",
        expanded=True
    ):

        st.write(
            "🤔 Understanding your question..."
        )

        st.write(
            "🔎 Searching Wikipedia..."
        )

        st.write(
            "🧠 Evaluating relevant information..."
        )

        result = wikipedia_agent(
            question,
            current_messages
        )

        st.write(
            "✍️ Preparing your answer..."
        )


    # Display answer

    st.markdown("""
    <div class="ai-label">

        <div class="ai-dot"></div>

        WikiAgent

    </div>
    """, unsafe_allow_html=True)


    st.markdown(
        f'<div class="answer-text">'
        f'{result["answer"]}'
        f'</div>',
        unsafe_allow_html=True
    )


    # Source

    if result["source"]:

        source = result["source"]

        st.markdown(
            f"""
            <div class="source-card">

                <div class="source-label">
                    Primary source
                </div>

                <div class="source-title">
                    📚 {source["title"]}
                </div>

                <div style="color:#777784;
                font-size:12px;">
                    Wikipedia
                </div>

                <br>

                <a
                class="source-link"
                href="{source["url"]}"
                target="_blank">

                Open Wikipedia article ↗

                </a>

            </div>
            """,
            unsafe_allow_html=True
        )


    # Save conversation

    st.session_state.messages.append({

        "role":
        "user",

        "content":
        question

    })


    st.session_state.messages.append({

        "role":
        "assistant",

        "content":
        result["answer"],

        "source":
        result["source"]

    })

    st.rerun()
