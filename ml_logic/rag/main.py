from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import PydanticOutputParser

from typing import List, Dict, Any
from pydantic import Field, BaseModel

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["LANGCHAIN_TRACING"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

class CVEvalInput(BaseModel):
    target_job_desc: str = Field(description="The ideal job description for the role")
    cv: str = Field(description="Uploaded cv to be evaluated")

class CVEvalResult(BaseModel):
    relevance_score: int = Field(default=0, ge = 0, le = 100, description="Overall relevance score from 0-100")
    assessment: str = Field(default="",description="Overall assesment of the uploaded cv")
    strengths: List[str] = Field(default=[""], description="List of candidate's strengths")
    drawbacks: List[str] = Field(default=[""], description="Areas where candidate can improve")
    recommendations: List[str] = Field(default=[""], description="Actionable recommendations")

#vector database = FAISS
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"device":"cpu"})
vectore_store = FAISS.load_local("/app/vector-store/faiss_index", embedder, allow_dangerous_deserialization=True)

# query = "what are the required skills for a data scientist
# response = vectore_store.similarity_search(query=query, k=3)

# print(response[0])dex", embeddings=embedder, allow_dangerous_deserialization=True)
output_parser = PydanticOutputParser(pydantic_object=CVEvalResult)

# model = mistral
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
mistral = Ollama(base_url=ollama_url, model="mistral")

format_instructions = """{
  "relevance_score": integer (0-100),
  "assessment": string,
  "strengths": [list of strings],
  "drawbacks": [list of strings],
  "recommendations": [list of strings]
}"""

#prompt
prompt = PromptTemplate(
    input_variables=["similar_jobs", "target_job_desc", "cv"],
    template="""You are an expert HR professional. Evaluate the candidate's CV against the job description and generate the relevance score based on this comparison.

## Similar Job Descriptions for Context:
{similar_jobs}

## Target Job Description:
{target_job_desc}

## Candidate CV:
{cv}

## Instructions:
Analyze the candidate's qualifications and provide a structured evaluation using the retrieved similar job descriptions as general context.

- You may refer to these similar roles to understand general expectations for the job type, but do not rely entirely on them.
- Avoid overfitting your evaluation to overly specific or unique details in the retrieved descriptions.
- Focus instead on the candidate's fit for the overall role, considering broader industry expectations and the provided job description.

Evaluate the following areas:
1. Skills alignment with job requirements
2. Experience relevance and level
3. Educational background fit
4. Overall suitability for the role


## Required Output Format:
You MUST respond with a valid JSON object in this exact format:

{format_instructions}

IMPORTANT: Respond ONLY with the JSON object, no additional text.""",
    partial_variables={"format_instructions": format_instructions}
)

#getting the 5 most relevent job descriptions to the required job
def get_similar_jobs(inputs: Dict[str, Any]) -> str:
  target_job = inputs["target_job_desc"]
  similar_docs = vectore_store.similarity_search_with_score(target_job, k=5)

  formatted_similar_jobs = []
  for i, (doc, score) in enumerate(similar_docs, 1):
    job_txt = f"""
    ### Similar Job {i} (Similarity: {score:.3f}):
    **Title:** {doc.metadata.get('Job Title')}
    **Requirements:** {doc.page_content}...
    ---"""
    formatted_similar_jobs.append(job_txt)
    print(job_txt)
    print("\n ======= \n")
  return "\n".join(formatted_similar_jobs)

def safe_output_parse(x):
   if x is None:
      raise ValueError("LLM returned no output. Try reducing input size or change the model.")
   x = x.strip()
   return x

#evaluation chain
# eval_chain_gemma = (
#    RunnableParallel({
#       "similar_jobs": RunnableLambda(get_similar_jobs),
#       "target_job_desc": RunnablePassthrough() | (lambda x: x["target_job_desc"]),
#       "cv": RunnablePassthrough() | (lambda x: x["cv"])
#    }) 
#    | prompt
#    | gemma
#    | RunnableLambda(safe_output_parse)
#    | output_parser
# )

eval_chain_mistral = (
   RunnableParallel({
      "similar_jobs": RunnableLambda(get_similar_jobs),
      "target_job_desc": RunnablePassthrough() | (lambda x: x["target_job_desc"]),
      "cv": RunnablePassthrough() | (lambda x: x["cv"])
   })
   | prompt
   | mistral
   | RunnableLambda(safe_output_parse)
   | output_parser
)

def testing():
   # cv = '- : as a recent graduate in computer science with 6-months of experience in flutter, i am excited to apply for the position of flutter developer at your company. though i have not worked with android studio, i am willing to learn and adapt as per the requirement. i have experience in handling user-friendly ui based on requirements in a flutter and knowledge of firebase. i am comfortable working with cross-platform frameworks. while i have not worked with location services and video recording, i am eager to learn and implement them. i am a strong team player with a commitment to perfection and am ready to face new challenges.'
  # jd = 'we are looking for hire experts flutter developer. so you are eligible this post then apply your resume. job types: full-time, part-time salary: 20,000.00 - 40,000.00 per month benefits: flexible schedule food allowance schedule: day shift supplemental pay: joining bonus overtime pay experience: total work: 1 year (preferred) housing rent subsidy: yes industry: software development work remotely: temporarily due to covid-19'
  # testcv = CVEvalInput(target_job_desc=jd, cv=cv)
  # out = CVEvalResult()

  # chain = eval_chain.with_types(input_type=testcv, output_type=out)
  # output = chain.invoke(testcv)
  # print("Relevance Score:", output.relevance_score)
  # print("Assessment:", output.assessment)
  # print("Strengths:", output.strengths)
  # print("Drawbacks:", output.drawbacks)
  # print("Recommendations:", output.recommendations)
  # print(output)


  # print(output_parser.get_format_instructions())
  pass