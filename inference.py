from openai import OpenAI
import pdfplumber
import json

with open('inference.json') as config_file:
    config = json.load(config_file)

API_KEY = config["API_KEY"]  ## fill your API Key here.

# ## Read File Data

with pdfplumber.open(config["SOURCE"]) as pdf:
    # Extract text from each page
    text1 = 'Data: \n'
    for page in pdf.pages:
        text1 += page.extract_text().strip()


with pdfplumber.open(config["FE_CATEGORICAL_VARIABLES_FILE"]) as pdf:
    # Extract text from each page
    instructions_cat = 'Prompt: \n'
    for page in pdf.pages:
        instructions_cat += page.extract_text().strip()


with pdfplumber.open(config["FE_INSTRUCTIONS_NUANCED_VARIABLES_FILE"]) as pdf:
    # Extract text from each page
    instructions_nuanced = 'Prompt: \n'
    for page in pdf.pages:
        instructions_nuanced += page.extract_text().strip()


prompt_cat = text1 + ' ' + instructions_cat
prompt_nuanced = text1 + ' ' + instructions_nuanced


client = OpenAI(
    api_key=API_KEY,
)


# ## Fourth Run (8/5/24)

# ### Case-1 (State v Kuman 2000 PNGLR 313):

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt_cat,
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message.content)


chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt_nuanced,
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion.choices[0].message.content)


