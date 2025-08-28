from langchain_core.prompts import PromptTemplate

first_question_prompt_template = """
You are an experienced interviewer.  
You will be provided with the candidate’s resume details including:  
1. Skills  
2. Summary / Professional Overview  
3. Projects  
4. Education  

Your task:  
- Based on the provided details, generate the **first interview question**.  
- The question should:  
   1. Be specific to the candidate’s background.  
   2. Allow them to showcase their experience and expertise.  
   3. Set a positive and engaging tone for the interview.  

Return your answer as **valid JSON only**. 
  ** Do not include Markdown code fences, explanations, or extra text. 
  ** The response must be directly parseable by `json.loads`.

{{
  "opening_question": "..."
}}

Candidate resume details:  
{resume_content}

"""

first_question_prompt = PromptTemplate(
    template=first_question_prompt_template,
    input_variables=["resume_content"]
)