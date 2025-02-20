import os
import sys
import io
import gradio as gr
from dotenv import load_dotenv
import subprocess
import google.generativeai

# Load Environment Variables
load_dotenv()

# Get API key
google_api_key = os.getenv("GEMINI_API_KEY")

if google_api_key:
    print(f"Gemini API key exists and begins with: {google_api_key[:8]}")
else:
    print("Gemini API key not set. Exiting...")

# Configure Google Generative AI
google.generativeai.configure(api_key=google_api_key)

# System Message
system_message = (
    "You are an assistant that reimplements Python code in high-performance C++ for an M1 Mac. "
    "Respond only with C++ code; use comments sparingly and do not provide any explanation other than occasional comments. "
    "The C++ response needs to produce an identical output in the fastest possible time."
)

# User Message Prompt
def user_prompt_for(python):
    return (
        "Rewrite this Python code in C++ with the fastest possible implementation that produces identical output in the least time. "
        "Respond only with C++ code; do not explain your work other than a few comments. "
        "Pay attention to number types to ensure no integer overflows. Remember to #include all necessary C++ libraries such as iomanip.\n\n"
        + python
    )

# Generate message payload for Gemini API
def message_for(python):
    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt_for(python)}
    ]

# Write the generated C++ code to a file called optimized.cpp
def write_output(cpp):
    code = cpp.replace("```cpp", "").replace("```", "")
    with open("optimized.cpp", "w") as f:
        f.write(code)
    print("Optimized C++ code saved to optimized.cpp")

# Gemini Model Selection & Streaming
def message_gemini_stream(python, model):
    gemini = google.generativeai.GenerativeModel(
        model_name=model,
        system_instruction=system_message
    )

    response = gemini.generate_content(user_prompt_for(python), stream=True)
    
    collected_text = ""
    for chunk in response:
        if hasattr(chunk, "text"):
            collected_text += chunk.text
            print(chunk.text, end="")

    return collected_text


# Gradio UI
with gr.Blocks() as ui:
    gr.Markdown("## Convert Python Code to C++ using Gemini AI")

    with gr.Row():
        python = gr.Textbox(label="Python code:", lines=10)
        cpp = gr.Textbox(label="Generated C++ code:", lines=10)

    with gr.Row():
        model = gr.Dropdown(["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"], label="Select Gemini Model", value="gemini-1.5-flash")

    with gr.Row():
        convert = gr.Button("Convert to Code")
       
    
    convert.click(message_gemini_stream, inputs=[python, model], outputs=[cpp])
    
ui.launch(inbrowser=True)