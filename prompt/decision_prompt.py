from langchain_core.prompts import PromptTemplate

decision_prompt_template = """
    You are an AI interview assistant helping to decide whether to continue or end an interview.
    
    INTERVIEW CONTEXT:
    - Duration so far: {interview_duration} minutes
    - Number of exchanges: {no_of_exchange}
    - Interview objectives: {interview_objectives}
    - User Answer: {user_answer}
    
    RECENT CONVERSATION:
    {recent_conversation}  # Last 5 exchanges
    
    DECISION CRITERIA:
    - Continue if: More information needed, candidate is engaged, objectives not fully met, under 45 minutes
    - Stop if: Sufficient information gathered, candidate seems fatigued, all objectives covered, over 60 minutes, or natural conclusion reached
    - If the user didn't answer 3 question consecutively then end the interview.
    
    Based on this context, should the interview CONTINUE or STOP?
    
    Respond with exactly one word: "CONTINUE" or "STOP"
    
    Then on a new line, provide a brief reason (max 20 words).

    Return your answer as **valid JSON only**. 
    ** The out should contain two fields "decision" and "reason"
    ** Do not include Markdown code fences, explanations, or extra text. 
    ** The response must be directly parseable by `json.loads`.
    """

decision_prompt = PromptTemplate(
    template=decision_prompt_template,
    input_variables=["interview_duration", "no_of_exchange", "interview_objectives","recent_conversation", "user_answer"]
)