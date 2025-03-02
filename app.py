import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_title = "Generate Blog",
                   page_icon = "💬📊",
                   layout = "centered",
                   initial_sidebar_state = "collapsed")

st.header("Generate Blog 💬📊")

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Initialize chat history and selected modela
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

if "selected_blog" not in st.session_state:
    st.session_state.selected_blog = None

if "selected_tone" not in st.session_state:
    st.session_state.selected_tone = None

# Define model details
models = {
    #"gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    #"llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    #"llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    #"mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Options for blog style :-
blogs = {"Researchers","Students","Common People"}

# Options for different tones:- 
tones = {"Professional","Informal","Cowboy"}

# Layout for model selection and max_tokens slider
col1, col2, col3, col4 = st.columns(4)

with col1:
    model_option = st.sidebar.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0  # Default to mixtral
    )

# Detect model, bolg_style and tone changes and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option
    
max_tokens_range = models[model_option]["tokens"]

with col2:
    # Adjust max_tokens slider dynamically based on the selected model
    max_tokens = st.sidebar.slider(
        "Max Tokens:",
        min_value=512,  # Minimum value to allow some flexibility
        max_value=max_tokens_range,
        # Default value or max allowed if less
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}"
    )
with col3:
    blog_style = st.sidebar.selectbox(
        "Generate Blog For:",
        options = blogs,
        index = 2
    )
#Detect the blog style:-    
if st.session_state.selected_blog != blog_style:
     st.session_state.messages = []
     st.session_state.selected_blog = blog_style

with col4:
    tone_style = st.sidebar.selectbox(
        "Select Your Blog Tone:",
        options = tones,
        index = 2
    )
#Detect the tone style     
if st.session_state.selected_tone != tone_style:
     st.session_state.message = []
     st.session_state.selected_tone = tone_style

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Enter your prompt here..."):
    if prompt is not None:
        input_prompt = f"""
            As an AI assistant, your task is to respond when a user selects a specific blog style: {blog_style} 
            and tone: {tone_style}.
            """
    st.session_state.messages.append({"role":"system","content":input_prompt})
    st.session_state.messages.append({"role": "user", "content":prompt})

    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    full_response = []   

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model = model_option,
            #blog = blog_style,
            #tone = tone_style,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")
    
    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})