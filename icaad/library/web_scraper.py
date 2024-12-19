import pandas as pd
from string import Template
import requests
from bs4 import BeautifulSoup
import csv
import pdfkit
import pdfplumber
import os
import json
import boto3


with open('web_scraper.json') as config_file:
    config = json.load(config_file)

### CONFIG
FILTER_COUNTRIES = config['FILTER_COUNTRIES']
YEAR_PREFIX = config["YEAR_PREFIX"]  ## any year starting with "20"
FORCE_REFRESH = True  ## Let this be false

BASE_URL = config["BASE_URL"]
COUNTRY_OUTPUT = config["COUNTRY_OUTPUT"]
FILTER_COUNTRIES = [x.lower() for x in FILTER_COUNTRIES]
COUNTRY_NAMESPACE_DICT = {}
COUNTRY_YEAR_DICT = {}
COUNTRY_NAMESPACE_URL_TEMPLATE = Template("${base_url}${country_lower}/cases/${country_upper}LawRp/index.html")
AVAILABLE_COUNTRY_LIST = config["AVAILABLE_COUNTRY_LIST"]



def logging(output):
    print(output)

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logging(f"Directory '{directory_path}' created.")
    else:
        logging(f"Directory '{directory_path}' already exists.")

def check_file_exists(file_path):
    if os.path.isfile(file_path):
        logging(f"File '{file_path}' exists.")
        return True
    else:
        logging(f"File '{file_path}' does not exist.")
        return False


def save_dict_to_file(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)
    logging(f"Dictionary saved to '{file_path}'")


def load_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        dictionary = json.load(file)
    logging(f"Dictionary loaded from '{file_path}'")
    return dictionary

def extract_links_from_pdf(pdf_file):
    urls = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract the annotations (including links)
            annotations = page.annots
            if annotations:
                for annot in annotations:
                    if 'uri' in annot:
                        urls.append(annot['uri'])
    return urls

def get_year_cases():
    year_cases_dict = {}
    for k,v in COUNTRY_YEAR_DICT.items():
        year_cases_dict[k] = {}
        for year_url in v:
            year = year_url.split("/")[-2]
            file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/indexes.pdf"
            create_directory_if_not_exists(f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}")
            if FORCE_REFRESH or check_file_exists(file_path) is False:
                download_html_as_pdf(year_url, file_path)
            urls = extract_links_from_pdf(file_path)
            urls = [x for x in urls if year in x]
            year_cases_dict[k][year] = urls
    return year_cases_dict

def scrape_hyperlinks_to_csv(url, output_csv):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Link Text', 'URL'])
            for link in links:
                link_text = link.get_text(strip=True)
                link_url = link.get('href')
                if link_url:
                    writer.writerow([link_text, link_url])
        logging(f"Scraping completed. Data saved to {output_csv}")
    except requests.exceptions.RequestException as e:
        logging(f"Error occurred while making the request: {e}")
    except Exception as e:
        logging(f"An error occurred: {e}")

def get_countries_namespaces():
    create_directory_if_not_exists("downloads")
    if check_file_exists(COUNTRY_OUTPUT) is False:
        scrape_hyperlinks_to_csv(BASE_URL, COUNTRY_OUTPUT)
    df = pd.read_csv(COUNTRY_OUTPUT)
    filtered_df = df[df['Link Text'].str.lower().isin([value.lower() for value in FILTER_COUNTRIES])]
    # column_values_list = filtered_df['column_name'].tolist()
    result_dict = pd.Series(filtered_df['URL'].values, index=filtered_df['Link Text']).to_dict()
    for k,v in result_dict.items():
        result_dict[k] = v.split("/")[1].split(".")[0]
    return result_dict

def get_countries_years():
    year_dict = {}
    for k,v in COUNTRY_NAMESPACE_DICT.items():
        year_dict[k] = COUNTRY_NAMESPACE_URL_TEMPLATE.safe_substitute(base_url=BASE_URL, country_lower=v.lower(), country_upper=v.upper())
    create_directory_if_not_exists("downloads/countries")
    for k,v in year_dict.items():
        file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/indexes.pdf"
        create_directory_if_not_exists(f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}")

        if FORCE_REFRESH or check_file_exists(file_path) is False:
            download_html_as_pdf(v, file_path)
        urls = extract_links_from_pdf(file_path)
        urls = [x for x in urls if x.startswith(v.replace("index.html", YEAR_PREFIX))]
        year_dict[k] = urls
    return year_dict

def download_html_as_pdf(url, output_pdf):
    logging(f"Start downloading...{url} {output_pdf}")
    try:
        # Define path to wkhtmltopdf binary, if needed. Uncomment below line if wkhtmltopdf isn't in PATH
        # pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

        # Convert the given URL to a PDF and save it locally
        pdfkit.from_url(url, output_pdf)
        logging(f"PDF saved successfully as {output_pdf}")
    except Exception as e:
        logging(f"Error occurred: {e}")

def generate_COUNTRY_NAMESPACE_DICT():
    dict_file_path = "downloads/countries.json"
    COUNTRY_NAMESPACE_DICT = {}
    ''' 
    if check_file_exists(dict_file_path):
        COUNTRY_NAMESPACE_DICT = load_dict_from_file(dict_file_path)
    else:
    '''
    COUNTRY_NAMESPACE_DICT = get_countries_namespaces()
    save_dict_to_file(COUNTRY_NAMESPACE_DICT, dict_file_path)

    logging(COUNTRY_NAMESPACE_DICT)

    return COUNTRY_NAMESPACE_DICT

def generate_COUNTRY_YEAR_DICT():
    dict_file_path = "downloads/countries_urls.json"
    COUNTRY_YEAR_DICT = {}
    if FORCE_REFRESH is False and check_file_exists(dict_file_path):
        COUNTRY_YEAR_DICT = load_dict_from_file(dict_file_path)
    else:
        COUNTRY_YEAR_DICT = get_countries_years()
        for k,v in COUNTRY_YEAR_DICT.items():
            COUNTRY_YEAR_DICT[k] = [x + "index.html" for x in COUNTRY_YEAR_DICT[k]]
        save_dict_to_file(COUNTRY_YEAR_DICT, dict_file_path)

    return COUNTRY_YEAR_DICT

def generate_COUNTRY_YEAR_CASES_DICT():
    dict_file_path = "downloads/countries_years_urls.json"
    COUNTRY_YEAR_CASES_DICT = {}
    if FORCE_REFRESH is False and check_file_exists(dict_file_path):
        COUNTRY_YEAR_CASES_DICT = load_dict_from_file(dict_file_path)
    else:
        COUNTRY_YEAR_CASES_DICT = get_year_cases()
        save_dict_to_file(COUNTRY_YEAR_CASES_DICT, dict_file_path)
    
    return COUNTRY_YEAR_CASES_DICT

def download_cases():
    return_msg = ""
    logging(f"Start downloading...")

    for k,v in COUNTRY_YEAR_CASES_DICT.items():
        if v.items():
            for year, urls in v.items():
                for url in urls:
                    case_num = url.split("/")[-1].split(".")[0]
                    file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases/{case_num}.pdf"
                    create_directory_if_not_exists(f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases")
                    if check_file_exists(file_path) is False:
                        download_html_as_pdf(url, file_path)
            logging(f"All Cases for {k} for year {year} have been downloaded.")
        else:
            return_msg += "Empty "
    return return_msg

def upload_to_objectstore():

    # Create S3 service client
    svc = boto3.client(
    's3',
    aws_access_key_id=config["AWS_CREDENTIALS"]["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_CREDENTIALS"]["AWS_SECRET_ACCESS_KEY"],
    endpoint_url=config["AWS_CREDENTIALS"]["AWS_ENDPOINT_URL_S3"]
    )

    # List buckets
    response = svc.list_buckets()

    for bucket in response['Buckets']:
        logging(f'  {bucket["Name"]}')

    # List objects
    response = svc.list_objects_v2(Bucket=config["AWS_CREDENTIALS"]["BUCKET_NAME"])

    if response.get("Contents") is not None:
        for obj in response['Contents']:
            logging(f'  {obj["Key"]}')

    # Upload file
    for path, dirs, files in os.walk("downloads/"):
        logging(files)
        for file in files:
            file_s3 = os.path.normpath(path + '/' + file)
            file_local = os.path.join(path, file)
            logging("Upload:", file_local, "to target:", file_s3, end="")
            response = svc.upload_file(file_local, config["AWS_CREDENTIALS"]["BUCKET_NAME"], file_s3)
            logging(response)
    return response


def init():
    global COUNTRY_NAMESPACE_DICT 
    COUNTRY_NAMESPACE_DICT = generate_COUNTRY_NAMESPACE_DICT()
    global COUNTRY_YEAR_DICT 
    COUNTRY_YEAR_DICT = generate_COUNTRY_YEAR_DICT()
    global COUNTRY_YEAR_CASES_DICT
    COUNTRY_YEAR_CASES_DICT = generate_COUNTRY_YEAR_CASES_DICT()
