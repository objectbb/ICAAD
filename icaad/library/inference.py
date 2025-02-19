from openai import OpenAI
import pdfplumber
import json
import os
from dotenv import load_dotenv
import pandas as pd
from library.utility.build_pyd_class import add_field
from pydantic import BaseModel

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import ValidationError

here = os.path.dirname(os.path.abspath(__file__))
with open(f'/{here}/inference.json') as config_file:
    config = json.load(config_file)

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")  ## fill your API Key here.

class FeatureCaseModel(BaseModel):
    name: str

def load_features_model():
    # ## Read File Data
    # Reads the CSV file into a DataFrame
    df = pd.read_csv("Features.csv", usecols=['Feature Name','Feature Type','Prompt','Validation for LLM','Notes/Comments', 'Default Value'])
    filtered_df = df.loc[df['Prompt'].notna()]

    prompt = ""
    for index, row in df.iterrows():
        add_field(FeatureCaseModel, row['Feature Name'], str, row['Prompt'],row['Default Value'])
        prompt += f"{row['Feature Name']}-{row['Prompt']}, "

    return prompt

def load_pfds_prompt(source):
    with pdfplumber.open(f"/{here}/sample_cases/{source}") as pdf:
        # Extract text from each page
        text1 = 'Data: \n'
        for page in pdf.pages:
            text1 += page.extract_text().strip()

    with pdfplumber.open(f"/{here}/{config["FE_CATEGORICAL_VARIABLES_FILE"]}") as pdf:
        # Extract text from each page
        instructions_cat = 'Prompt: \n'
        for page in pdf.pages:
            instructions_cat += page.extract_text().strip()

    with pdfplumber.open(f"/{here}/{config["FE_INSTRUCTIONS_NUANCED_VARIABLES_FILE"]}") as pdf:
        # Extract text from each page
        instructions_nuanced = 'Prompt: \n'
        for page in pdf.pages:
            instructions_nuanced += page.extract_text().strip()

    prompt_cat = text1 + ' ' + instructions_cat
    prompt_nuanced = text1 + ' ' + instructions_nuanced
    return prompt_cat + prompt_nuanced
  
def run_query(prompt):

    client = OpenAI(
        api_key=API_KEY,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return f"{chat_completion.choices[0].message.content}"

def parse(instructions, query):
    llm = Ollama(model="gpt-3.5-turbo")
    parser = JsonOutputParser(pydantic_object=FeatureCaseModel)

    # Define a prompt template for assessing tweet content
    # and include the formatting instructions 
    prompt = PromptTemplate(
        template="""
        {{instructions}}
        {format_instructions}
        
        {query_text}
        """,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Construct a Langchain Chain to connect the prompt template with the LLM and Pydantic parser
    chain = prompt | llm | parser
    result = chain.invoke({"query_text": query})
    
    return result

async def inference_initiate(source):
    general_instructions = f"Populate the fields in the json object <Feature Name>:<Value> using the below variables mentioned. {load_features_model()} Do not output as a text table. If there are multiple charges, answer the below questions based on the highest/most serious charge."
    query = load_pfds_prompt(source) 
    return run_query(query + general_instructions)
