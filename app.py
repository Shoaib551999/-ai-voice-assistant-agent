import pandas as pd
from log_reader import read_agent_logs
import time
from agent_logger import log_tool_execution
import os
import json
import hashlib
import tempfile
from pathlib import Path

import pyttsx3
import streamlit as st
from dotenv import load_dotenv
from groq import Groq


from database import (
    initialize_database,
    save_message,
    load_messages,
    clear_messages,
    get_tasks,
    complete_task,
    get_notes,
    save_note,
)


from agent_tools import TOOLS, execute_tool


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🎙️",
    layout="centered",
)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found in your .env file.")
    st.stop()

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"
WHISPER_MODEL = "whisper-large-v3-turbo"


# ==========================================
# 2. DATABASE AND SESSION MEMORY
# ==========================================

initialize_database()

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

if "speech_audio" not in st.session_state:
    st.session_state.speech_audio = {}

if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


# ==========================================
# 3. SPEECH-TO-TEXT
# ==========================================

def transcribe_audio(audio_file):
    """
    Convert browser microphone audio into text
    using Whisper through Groq.
    """

    transcription = client.audio.transcriptions.create(
        file=(
            "recording.wav",
            audio_file.getvalue(),
        ),
        model=WHISPER_MODEL,
        response_format="json",
        language="en",
    )

    return transcription.text.strip()


# ==========================================
# 4. AI AGENT WITH FUNCTION CALLING
# ==========================================


def generate_response(user_text):
    """
    Multi-step AI agent with bounded tool execution.
    """

    MAX_TOOL_ROUNDS = 4

    system_prompt = (
        "You are a helpful personal AI voice assistant. "
        "Respond naturally, clearly, and concisely. "
        "You can save and retrieve notes, create tasks, "
        "retrieve tasks, and complete tasks. "
        "Use tools only when appropriate. "
        "Do not invent task IDs, notes, or tool results. "
        "When asked to complete a task by its description, "
        "first retrieve tasks to identify its exact ID. "
        "If multiple tasks match, ask the user to clarify. "
        "Never claim an action succeeded unless a tool "
        "result explicitly confirms success. "
        "Do not repeat successful write operations."
    )

    conversation = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    # Add recent conversation history
    conversation.extend(
        st.session_state.messages[-20:]
    )

    conversation.append({
        "role": "user",
        "content": user_text
    })

    # Prevent repeating the same write operation
    executed_writes = set()

    for round_number in range(MAX_TOOL_ROUNDS + 1):

        # Disable further tools after reaching the limit
        allow_tools = round_number < MAX_TOOL_ROUNDS

        request = {
            "model": MODEL,
            "messages": conversation,
            "reasoning_effort": "low",
            "max_completion_tokens": 800
        }

        if allow_tools:
            request.update({
                "tools": TOOLS,
                "tool_choice": "auto",
                "parallel_tool_calls": False
            })

        response = client.chat.completions.create(
            **request
        )

        message = response.choices[0].message

        if not message.tool_calls:
            answer = (message.content or "").strip()

            if not answer:
                raise RuntimeError(
                    "The AI returned an empty response."
                )

            return answer

        conversation.append(
            message.model_dump(exclude_none=True)
        )

        
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name

            # Start execution timer
            start_time = time.perf_counter()

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )

                if not isinstance(arguments, dict):
                    raise ValueError("Invalid tool arguments.")

                write_key = (
                    function_name,
                    json.dumps(arguments, sort_keys=True)
                )

                is_write = function_name in {
                    "save_note",
                    "create_task",
                    "complete_task"
                }

                if is_write and write_key in executed_writes:
                    result = {
                        "success": False,
                        "error": (
                            "This write operation was already "
                            "executed during this request."
                        )
                    }

                else:
                    result = execute_tool(
                        function_name,
                        arguments
                    )

                    if is_write and result.get("success"):
                        executed_writes.add(write_key)

            except Exception as error:
                result = {
                    "success": False,
                    "error": str(error)
                }

            # Calculate execution time
            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            # Record execution metadata
            log_tool_execution(
                tool_name=function_name,
                success=result.get("success", False),
                duration_ms=duration_ms
            )

            # Return the tool result to the AI model
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })


    raise RuntimeError(
        "The agent exceeded its execution limit."
    )


# ==========================================
# 5. TEXT-TO-SPEECH
# ==========================================

def generate_speech(text):
    """
    Convert text into a WAV file using
    the local Windows speech engine.
    """

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False,
    ) as temp_file:
        audio_path = temp_file.name

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.save_to_file(text, audio_path)
        engine.runAndWait()

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        if len(audio_bytes) < 100:
            raise RuntimeError(
                "Speech audio was not generated."
            )

        return audio_bytes

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


# ==========================================
# 6. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🎙️ Voice AI")

    st.markdown("### AI Assistant Dashboard")

    st.info("AI Assistant Ready")

    st.divider()

    st.markdown("### Technology Stack")

    st.write("🐍 Python")
    st.write("🎙️ Whisper Speech Recognition")
    st.write("🧠 Groq LLM")
    st.write("🔊 Text-to-Speech")
    st.write("🌐 Streamlit")
    st.write("🗄️ SQLite")
    st.write("🤖 AI Function Calling")

    st.divider()

    st.markdown("### Session Statistics")

    total_questions = sum(
        1
        for message in st.session_state.messages
        if message["role"] == "user"
    )

    st.metric(
        "Questions Asked",
        total_questions,
    )

    st.divider()

    st.caption(
        "AI Voice Assistant — Local Development"
    )


# ==========================================
# 7. MAIN APPLICATION INTERFACE
# ==========================================

st.title("🎙️ AI Voice Assistant")

st.write(
    "Your personal AI assistant powered by "
    "Python, Whisper, Groq, and SQLite."
)

st.divider()

st.subheader("🎤 Talk to your assistant")

st.write(
    "Record a question or ask your assistant "
    "to save notes and manage tasks."
)

audio = st.audio_input(
    "Record your voice",
    sample_rate=16000,
)


# ==========================================
# 8. PROCESS VOICE INPUT
# ==========================================

if audio is not None:

    audio_bytes = audio.getvalue()

    audio_id = hashlib.sha256(
        audio_bytes
    ).hexdigest()

    if audio_id != st.session_state.last_audio_id:

        with st.spinner("Processing your voice..."):

            try:
                user_text = transcribe_audio(audio)

                if user_text:

                    ai_response = generate_response(
                        user_text
                    )

                    # Store messages in memory.
                    st.session_state.messages.extend([
                        {
                            "role": "user",
                            "content": user_text,
                        },
                        {
                            "role": "assistant",
                            "content": ai_response,
                        },
                    ])

                    # Persist messages to SQLite.
                    save_message(
                        "user",
                        user_text,
                    )

                    save_message(
                        "assistant",
                        ai_response,
                    )

                    st.session_state.last_audio_id = audio_id

                    # Generate spoken response.
                    try:
                        speech = generate_speech(
                            ai_response
                        )

                        message_index = (
                            len(st.session_state.messages) - 1
                        )

                        st.session_state.speech_audio[
                            message_index
                        ] = speech

                    except Exception as speech_error:

                        st.warning(
                            "Voice generation failed: "
                            f"{speech_error}"
                        )

                else:
                    st.warning(
                        "No speech detected. Please try again."
                    )

            except Exception as error:

                st.error(
                    f"Error processing voice: {error}"
                )


# ==========================================
# 9. CONVERSATION DISPLAY
# ==========================================

st.divider()

st.subheader("💬 Conversation")

if not st.session_state.messages:
    st.info(
        "No conversation yet. "
        "Record your voice to get started."
    )

for index, message in enumerate(
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )

        # Display audio for assistant responses.
        if message["role"] == "assistant":

            audio_data = (
                st.session_state.speech_audio.get(
                    index
                )
            )

            if audio_data:
                st.audio(
                    audio_data,
                    format="audio/wav",
                )


# ==========================================
# 10. DOWNLOAD CONVERSATION
# ==========================================

if st.session_state.messages:

    conversation_json = json.dumps(
        st.session_state.messages,
        indent=4,
        ensure_ascii=False,
    )

    st.download_button(
        label="📥 Download Conversation",
        data=conversation_json,
        file_name="voice_assistant_chat.json",
        mime="application/json",
    )


# ==========================================
# 11. CLEAR CONVERSATION
# ==========================================

if st.button("🗑️ Clear Conversation"):

    clear_messages()

    st.session_state.messages = []
    st.session_state.speech_audio = {}
    st.session_state.last_audio_id = None

    st.rerun()


# ==========================================
# 12. TASK MANAGEMENT DASHBOARD
# ==========================================

st.divider()

st.header("📋 Task Management Dashboard")

pending_tasks = get_tasks("pending")
completed_tasks = get_tasks("completed")


# ------------------------------------------
# Task Statistics
# ------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Tasks",
        len(pending_tasks) + len(completed_tasks),
    )

with col2:
    st.metric(
        "Pending Tasks",
        len(pending_tasks),
    )

with col3:
    st.metric(
        "Completed Tasks",
        len(completed_tasks),
    )


# ------------------------------------------
# Pending Tasks
# ------------------------------------------

st.divider()

st.subheader("⏳ Pending Tasks")

if not pending_tasks:

    st.info("You have no pending tasks.")

else:

    for task in pending_tasks:

        task_col, button_col = st.columns(
            [4, 1]
        )

        with task_col:

            st.write(
                f"**Task #{task['id']}** — "
                f"{task['title']}"
            )

        with button_col:

            if st.button(
                "✅ Done",
                key=f"complete_task_{task['id']}",
            ):

                success = complete_task(
                    task["id"]
                )

                if success:
                    st.rerun()

                else:
                    st.warning(
                        "Task already completed "
                        "or not found."
                    )


# ------------------------------------------
# Completed Tasks
# ------------------------------------------

st.divider()

st.subheader("✅ Completed Tasks")

if not completed_tasks:

    st.info("No completed tasks yet.")

else:

    for task in completed_tasks:

        st.markdown(
            f"~~Task #{task['id']} — "
            f"{task['title']}~~"
        )


# ==========================================
# 13. NOTES MANAGEMENT DASHBOARD
# ==========================================

st.divider()
st.header("📝 Notes Management Dashboard")

notes = get_notes()

st.metric("Total Saved Notes", len(notes))

# Create a note manually
with st.form("add_note_form", clear_on_submit=True):
    new_note = st.text_area(
        "Write a new note",
        placeholder="Enter something you want to remember...",
        max_chars=2000,
    )

    submitted = st.form_submit_button("💾 Save Note")

    if submitted:
        if new_note.strip():
            save_note(new_note)
            st.rerun()
        else:
            st.warning("Please enter a note before saving.")

st.divider()

st.subheader("📚 Saved Notes")

if not notes:
    st.info("You haven't saved any notes yet.")

else:
    for note in notes:
        with st.expander(
            f"Note #{note['id']} — {note['created_at']}"
        ):
            st.write(note["content"])


# ==========================================
# AGENT MONITORING DASHBOARD
# ==========================================

st.divider()
st.header("📊 Agent Monitoring Dashboard")

# Read execution logs
logs = read_agent_logs()

if not logs:
    st.info("No agent execution logs available yet.")

else:
    df = pd.DataFrame(logs)

    # --------------------------------------
    # Calculate performance statistics
    # --------------------------------------

    total_calls = len(df)

    successful_calls = (
        df["Status"] == "SUCCESS"
    ).sum()

    failed_calls = (
        df["Status"] == "FAILED"
    ).sum()

    success_rate = (
        successful_calls / total_calls * 100
        if total_calls > 0 else 0
    )

    avg_duration = df["Duration (ms)"].mean()

    # --------------------------------------
    # Display KPIs
    # --------------------------------------

    metric1, metric2 = st.columns(2)
    metric3, metric4 = st.columns(2)

    with metric1:
        st.metric("Total Tool Calls", total_calls)

    with metric2:
        st.metric("Success Rate", f"{success_rate:.1f}%")

    with metric3:
        st.metric("Failed Calls", failed_calls)

    with metric4:
        st.metric(
            "Avg. Tool Duration",
            f"{avg_duration:.2f} ms"
        )

    st.divider()

    # --------------------------------------
    # Tool usage chart
    # --------------------------------------

    st.subheader("Tool Usage")

    tool_counts = df["Tool"].value_counts()

    st.bar_chart(tool_counts)

    # --------------------------------------
    # Execution duration chart
    # --------------------------------------

    st.subheader("Average Duration by Tool")

    duration_by_tool = (
        df.groupby("Tool")["Duration (ms)"]
        .mean()
        .sort_values(ascending=False)
    )

    st.bar_chart(duration_by_tool)

    # --------------------------------------
    # Execution history
    # --------------------------------------

    st.subheader("Recent Tool Executions")

    st.dataframe(
        df.iloc[::-1].head(50),
        width="stretch",
        hide_index=True
    )

    if st.button("🔄 Refresh Monitoring"):
        st.rerun()

# ==========================================
# 14. FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Voice Assistant | "
    "Python • Groq • Whisper • SQLite • Streamlit"
)
