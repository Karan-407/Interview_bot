import uuid
from typing import Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
import requests
from STT import continuous_speech_recognition
from TTS import text_to_speech_offline
from langgraph.graph.message import add_messages
from pdf_reader import extract_text_from_pdf
from prompt import context_prompt, first_question_prompt, follow_up_prompt, decision_prompt
import json
from langgraph.types import Command

load_dotenv()

llm  = ChatOpenAI(model="gpt-4o")

class State(TypedDict):
    messages: Annotated[list[str], add_messages]
    resume_content: str
    interview_context:str
    user_ready: bool
    interview_started: bool
    answers: Annotated[list[str], add_messages]
    questions: Annotated[list[str], add_messages]

def resume_processor(state: State):
    print("Processing resume... ")
    pdf_path = "/Users/karanveersingh/Code/interview_bot/resumes/Karanveer Singh.pdf"
    try:
        resume_text = extract_text_from_pdf(pdf_path)

        prompt = context_prompt.format(resume_content = resume_text)
        context_response = llm.invoke(prompt)

        return {
            "resume_content": resume_text,
            "interview_context": context_response.content,
            "messages":["Resume processed successfully"]
        }
    except Exception as e:
        return {
            "messages": [f"Error processing resume: {str(e)}"]
        }
    
def readiness_check(state: State):
    print("Checking readiness... ")
    ready_message = "We have analyzed your resume and are ready to start the interview. Are you ready to begin?"
    
    # Convert to speech
    text_to_speech_offline(ready_message)
    
    # Listen for user response
    try:
        user_response = continuous_speech_recognition()
        
        # Check if user confirmed
        user_ready = check_user_confirmation(user_response)
        
        return {
            "user_ready": user_ready,
            "messages": [f"User response: {user_response}"]
        }
    
    except Exception as e:
        return {
            "user_ready": False,
            "messages": [f"Error in speech recognition: {str(e)}"]
        }

def check_user_confirmation(user_response):

    accepted_response = ["yes", "yeah", "yep", "sure", "ready", "let's go", "start"]
    if any(char.lower() for char in user_response):
        return True
    else:
        return False
    
def conduct_interview(state: State):

    print("Started interview... ")
    if not state.get("interview_started"):
        # First question
        
        prompt = first_question_prompt.format(resume_content=state["interview_context"])
        question_response = llm.invoke(prompt)
        question = question_response.content
        
        # Speak the question
        text_to_speech_offline(question)
        user_answer = continuous_speech_recognition()
        
        return {
            "interview_started": True,
            "question": [question],
            "answers": [user_answer],
            "messages": [f"Asked: {question}"]
        }
    
    else:
        # Continue interview flow
        return continue_interview(state)

def continue_interview(state: State):
    try:
        user_answer = state.get("answers")[-1].content
        # Generate follow-up question
        prompt = follow_up_prompt.format(interview_context=state.get("interview_context"),
                                         previous_question=state.get("questions"),
                                         previous_answer=state.get("answers"),
                                         current_answer = user_answer
                                         )
        
        next_question_response = llm.invoke(prompt)
        next_question = next_question_response.content
        
        # Speak the follow-up question
        text_to_speech_offline(next_question)
        user_answer = continuous_speech_recognition()
        
        return {
            "questions": [next_question],
            "answers": [user_answer],
            "messages": [f"Candidate answered: {user_answer}", f"Asked: {next_question}"]
        }
        
    except Exception as e:
        return {
            "messages": [f"Error in interview continuation: {str(e)}"]
        }
    

def not_ready_handler(state: State):
    """Handle when user is not ready"""
    print("⏸️ User not ready, waiting...")
    
    wait_message = "No problem! Take your time. Let me know when you're ready to start the interview."
    text_to_speech_offline(wait_message)
    
    return {
        "user_ready": False,
        "messages": ["User not ready, waiting for confirmation"]
    }


def check_readiness(state: State) -> str:
    """Determine next step based on user readiness"""
    if state.get("user_ready") == True:
        return "conduct_interview"
    else:
        return "not_ready_handler"
    

def should_continue_interview(state: State) -> str:
    """Determine if interview should continue using LLM decision making"""
    
    # Extract relevant information from state
    conversation_history = state.get("messages", [])
    interview_duration = state.get("duration_minutes", 0)
    candidate_response = state.get("answers", [])[-1]
    interview_objectives = state.get("questions", [])
    
    prompt = decision_prompt.format(interview_duration=interview_duration,no_of_exchange=len(conversation_history),
                                     interview_objectives=interview_objectives,recent_conversation=conversation_history[-5:],
                                     user_answer=candidate_response)
    # Call your LLM (adjust based on your setup)
    response = llm.invoke(prompt)
    response = json.loads(response.content)
    
    # Log the decision for debugging
    state["last_decision_reason"] = response['reason']
    
    if response['decision'] == "STOP":
        print(response["reason"])
        return "end_interview"  # Your end state
    else:
        return "conduct_interview"  


def create_interview_graph():

    graph_builder = StateGraph(State)
    graph_builder.add_node("resume_processor", resume_processor)
    graph_builder.add_node("readiness_check", readiness_check)
    graph_builder.add_node("conduct_interview", conduct_interview)
    graph_builder.add_node("not_ready_handler", not_ready_handler)
    
    # Add edges
    graph_builder.add_edge(START, "resume_processor")
    graph_builder.add_edge("resume_processor", "readiness_check")
    
    # Conditional edge based on user readiness
    graph_builder.add_conditional_edges(
        "readiness_check",
        check_readiness,
        {
            "conduct_interview": "conduct_interview",
            "not_ready_handler": "not_ready_handler"
        }
    )
    
    # Loop back to readiness check if user wasn't ready
    graph_builder.add_edge("not_ready_handler", "readiness_check")
    
    # Continue interview loop
    graph_builder.add_conditional_edges(
        "conduct_interview",
        should_continue_interview,
        {
            "conduct_interview": "conduct_interview",
            "end_interview": END
        }
    )
    
    # Compile with memory for state persistence
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    
    return graph




def main():
    """Main execution function"""
    # Create the interview graph
    interview_graph = create_interview_graph()
    
    # Initial state
    initial_state = {
        "messages": ["Starting interview system"],
        "resume_content": "None",
        "interview_context": "None",
        "user_ready": "None",
        "interview_started": False,
        "answers": "None",
        "questions": "None"
    }
    
    # Configuration for thread persistence
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    print("🚀 Starting AI Interview System...")
    
    try:
        # Run the graph
        for step in interview_graph.stream(initial_state, config):
            print(f"Step completed: {step}")
            
    except KeyboardInterrupt:
        print("\n🛑 Interview stopped by user")
    except Exception as e:
        print(f"❌ Error in interview system: {str(e)}")


main()