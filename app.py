
import streamlit as st
from google import genai
from google.genai import types
import wikipediaapi
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Wikipedia Search Agent",
    page_icon="🤖",
    layout="centered"
)


# ============================================================
# INITIALIZATION
# ============================================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY
)

wiki = wikipediaapi.Wikipedia(
    user_agent="WikipediaSearchAgent/1.0",
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

        page = wiki.page(title);

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

def choose_best_wikipedia_article(question, candidates):

    if not candidates:
        return None

    candidate_text = ""

    for i, article in enumerate(candidates):

        candidate_text += f"""
Candidate {i + 1}
Title: {article['title']}
Summary: {article['summary']}
URL: {article['url']}

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

        number = int(response.text.strip())

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
                "message": "No relevant Wikipedia article found."
            }

        selected = choose_best_wikipedia_article(
            query,
            candidates
        )

        if selected is None:

            return {
                "status": "error",
                "message": "Could not select a relevant article."
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
            "message": "Wikipedia search failed.",
            "details": str(e)
        }


# ============================================================
# GEMINI TOOL
# ============================================================

wikipedia_tool = {
    "name": "smart_wikipedia_search",

    "description": """
    Searches Wikipedia for information relevant to
    the user's question and selects the most
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

        "required": ["query"]
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

    if not messages:
        return ""

    context = ""

    for message in messages:

        role = message["role"].capitalize()

        context += f"{role}: {message['content']}\n\n"

    return context


# ============================================================
# AI AGENT
# ============================================================

def wikipedia_agent(question, messages):

    conversation_context = build_conversation_context(messages)

    prompt = f"""
You are a Wikipedia Search Agent.

Your job is to answer the user's question using
relevant Wikipedia information.

IMPORTANT:
- Use the conversation history to understand follow-up questions.
- If the user says "he", "she", "it", "they", "his", "her", etc.,
  determine what they refer to from the conversation.
- Use the Wikipedia search tool when factual Wikipedia information
  is needed.
- Do not invent facts.
- Base factual answers on the retrieved Wikipedia information.

Conversation history:

{conversation_context}

Current user question:

{question}
"""

    # First Gemini call
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=config
    )

    # Gemini doesn't need Wikipedia
    if not response.function_calls:

        return {
            "answer": response.text,
            "source": None
        }

    # Gemini wants to use Wikipedia
    call = response.function_calls[0]

    query = call.args["query"]

    # Execute Wikipedia tool
    result = smart_wikipedia_search(query)

    if result["status"] == "error":

        return {
            "answer": result["message"],
            "source": None
        }

    # Send Wikipedia result back to Gemini
    function_response = types.Part.from_function_response(
        name=call.name,
        response=result
    )

    final_prompt = f"""
You are a Wikipedia Search Agent.

Conversation history:

{conversation_context}

Current question:

{question}

Wikipedia information retrieved:

Title:
{result["title"]}

Summary:
{result["summary"]}

Source:
{result["url"]}

Answer the user's question using the Wikipedia
information above.

Rules:
- Give a clear and natural answer.
- Use the conversation context.
- Resolve pronouns such as "he", "she", "it", or "they".
- Do not invent facts.
- If the information is insufficient, say so.
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
                parts=[function_response]
            )
        ],

        config=config
    )

    return {
        "answer": final_response.text,

        "source": {
            "title": result["title"],
            "url": result["url"]
        }
    }


# ============================================================
# USER INTERFACE
# ============================================================

st.markdown(
    '<div class="main-title">🤖 Wikipedia Search Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered research assistant using Wikipedia + Gemini'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ============================================================
# SESSION MEMORY
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []

if len(st.session_state.messages) == 0:

    st.markdown("""
    <div class="info-card">

    ### 👋 Welcome!

    Ask me a question and I'll search Wikipedia,
    identify the most relevant information, and
    generate a clear answer.

    **I can also understand follow-up questions.**

    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💡 Try an example")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🧠 Who was Alan Turing?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "Who was Alan Turing?"

    with col2:

        if st.button(
            "🤖 What is AI?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "What is artificial intelligence?"

    col3, col4 = st.columns(2)

    with col3:

        if st.button(
            "📞 Who invented the telephone?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "Who invented the telephone?"

    with col4:

        if st.button(
            "🌌 What is relativity?",
            use_container_width=True
        ):

            st.session_state.example_question = \
                "What is the theory of relativity?"


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("source"):

            st.markdown("---")

            st.markdown(
                f"""
                <div class="source-card">

                📚 <b>Wikipedia Source</b><br><br>

                <b>{message['source']['title']}</b><br>

                <a href="{message['source']['url']}" target="_blank">
                🔗 Open Wikipedia Article
                </a>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about a topic..."
)

if "example_question" in st.session_state:

    question = st.session_state.example_question

    del st.session_state.example_question


if question:

    # Display user question
    with st.chat_message("user"):

        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching Wikipedia and thinking..."
        ):

            result = wikipedia_agent(
                question,
                st.session_state.messages
            )

        st.markdown(result["answer"])

        if result["source"]:

            st.markdown("---")

            st.markdown(
                f"""
                <div class="source-card">

                📚 <b>Wikipedia Source</b><br><br>

                <b>{result['source']['title']}</b><br>

                <a href="{result['source']['url']}" target="_blank">
                🔗 Open Wikipedia Article
                </a>

                </div>
                """,
                unsafe_allow_html=True
            )

    # Save conversation
    st.session_state.messages.append({

        "role": "user",

        "content": question

    })

    st.session_state.messages.append({

        "role": "assistant",

        "content": result["answer"],

        "source": result["source"]

    })


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 Wikipedia Agent")

    st.write(
        """
        An AI-powered research assistant that
        searches Wikipedia and generates answers
        using Gemini.
        """
    )

    st.divider()

    st.subheader("⚙️ Agent Capabilities")

    st.write("🔎 Wikipedia Search")
    st.write("🧠 AI Article Selection")
    st.write("💬 Conversation Memory")
    st.write("📚 Source Attribution")
    st.write("🤖 Gemini Tool Calling")

    st.divider()

    st.subheader("💡 Example Topics")

    st.write("• Artificial Intelligence")

    st.write("• Computer Science")

    st.write("• History")

    st.write("• Scientists")

    st.write("• Technology")

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()
