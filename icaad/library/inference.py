from openai import OpenAI
import pdfplumber
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
with open(f'/{here}/inference.json') as config_file:
    config = json.load(config_file)

API_KEY = config["API_KEY"]  ## fill your API Key here.

# ## Read File Data

async def inference_initiate(source):
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

  

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt_nuanced,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return f"{chat_completion.choices[0].message.content} {chat_completion.choices[0].message.content}"


#"1.1.1 Case Citation - State v Kuman [2000] PNGLR 313\n1.1.2 Court’s Jurisdiction - CourtofFirstInstance\n1.1.3 Charge(s) - Rape (Section 6 of the Criminal Code Act) and Intentional Grievous Bodily Harm (Section 319 of the Criminal Code Act)\n1.1.4 Charge category - Sexual Violence\n1.1.5 First time offender - No\n1.1.6 First time offender, agree/disagree? - Disagree\n1.1.7 Starting Sentence - 5 years\n1.1.8 Alternative Starting Sentence - 5 years\n1.1.9 Aggravating factors - 2 years\n1.1.10 Mitigating factors - 1 year\n1.1.11 Final sentence - 6 years\n1.1.12 Customary practices - No\n1.1.13 Gender stereotypes - No\n1.1.14 Sole breadwinner - No\n1.1.15 Other factor(s) - No\n1.1.16 Type of gender discrimination - N\n1.1.17 Sentence reduction 1 - 0\n1.1.18 Sentence reduction 2 - 0\n1.1.19 Final sentence (including suspended sentence) - 6 years\n1.1.20 Positive judicial statements (women’s rights) - The judicial officer emphasized upholding the human rights of women and girls in handling Sexual or Gender Based Violence cases.\n1.1.21 Negative judicial statements (women’s rights) - There were no negative judicial statements regarding women's rights in this case. 1.1.1 Case Citation - State v Kuman [2000] PNGLR 313\n1.1.2 Court’s Jurisdiction - CourtofFirstInstance\n1.1.3 Charge(s) - Rape (Section 6 of the Criminal Code Act) and Intentional Grievous Bodily Harm (Section 319 of the Criminal Code Act)\n1.1.4 Charge category - Sexual Violence\n1.1.5 First time offender - No\n1.1.6 First time offender, agree/disagree? - Disagree\n1.1.7 Starting Sentence - 5 years\n1.1.8 Alternative Starting Sentence - 5 years\n1.1.9 Aggravating factors - 2 years\n1.1.10 Mitigating factors - 1 year\n1.1.11 Final sentence - 6 years\n1.1.12 Customary practices - No\n1.1.13 Gender stereotypes - No\n1.1.14 Sole breadwinner - No\n1.1.15 Other factor(s) - No\n1.1.16 Type of gender discrimination - N\n1.1.17 Sentence reduction 1 - 0\n1.1.18 Sentence reduction 2 - 0\n1.1.19 Final sentence (including suspended sentence) - 6 years\n1.1.20 Positive judicial statements (women’s rights) - The judicial officer emphasized upholding the human rights of women and girls in handling Sexual or Gender Based Violence cases.\n1.1.21 Negative judicial statements (women’s rights) - There were no negative judicial statements regarding women's rights in this case."