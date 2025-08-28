from langchain_core.prompts import PromptTemplate

context_prompt_template = """
You are an expert HR recruiter.  
You will be provided with the candidate's resume in plain text format:  
{resume_content}  

Your task is to carefully analyze the resume and perform the following actions:  
1. Extract the **resume summary / professional overview**.  
2. Extract the **skills**.  
3. Extract the **projects**.  
4. Extract the **education**.  

Guidelines:  
- Capture only the important and relevant details from the resume.  
- Do not add any information that is not explicitly present in the resume.  
- Ensure the output is accurate and concise.  
- Return the final result strictly as a JSON object in the following structure:  

{{
  "summary": "...",
  "skills": [...],
  "projects": [...],
  "education": [...]
}}
"""

context_prompt = PromptTemplate(
    template=context_prompt_template,
    input_variables=["resume_content"]
)
