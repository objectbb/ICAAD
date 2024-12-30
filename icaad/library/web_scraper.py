import pandas as pd
from string import Template
import requests
from bs4 import BeautifulSoup
import csv
import pdfkit
import pdfplumber
import os
import json
from collections import defaultdict
import time
import asyncio
import datetime
import boto3
import uuid

uuid_str = ""

with open('web_scraper.json') as config_file:
    config = json.load(config_file)

### CONFIG
YEAR_PREFIX = config["YEAR_PREFIX"]  ## any year starting with "20"
FORCE_REFRESH = config["FORCE_REFRESH"] == "True"   ## Let this be false

BASE_URL = config["BASE_URL"]
#COUNTRY_OUTPUT = config["COUNTRY_OUTPUT"]
COUNTRY_OUTPUT = f"downloads/{uuid_str}/countries.csv"

COUNTRY_NAMESPACE_DICT = {}
COUNTRY_YEAR_DICT = {}
COUNTRY_NAMESPACE_URL_TEMPLATE = Template("${base_url}${country_lower}/cases/${country_upper}LawRp/index.html")
AVAILABLE_COUNTRY_LIST = config["AVAILABLE_COUNTRY_LIST"]

def logging(output):
    print(f"{output} {datetime.datetime.now()}")

async def current_status():
    return ""

def convert_to_hms(seconds):
    """Converts seconds to hours, minutes, and seconds."""

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return hours, minutes, seconds

def boto_client(service):
    return boto3.client(
        service,
        aws_access_key_id=config["AWS_CREDENTIALS"]["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=config["AWS_CREDENTIALS"]["AWS_SECRET_ACCESS_KEY"],
        endpoint_url=config["AWS_CREDENTIALS"]["AWS_ENDPOINT_URL_S3"]
    )

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

            if FORCE_REFRESH is True or not check_file_exists(file_path):
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
    create_directory_if_not_exists(f"downloads/{uuid_str}")
    if check_file_exists(COUNTRY_OUTPUT) is False:
        scrape_hyperlinks_to_csv(BASE_URL, COUNTRY_OUTPUT)
    df = pd.read_csv(COUNTRY_OUTPUT)
    filtered_df = df[df['Link Text'].str.lower().isin([value.lower() for value in FILTER_COUNTRIES])]
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

        if FORCE_REFRESH is True or not check_file_exists(file_path):
            download_html_as_pdf(v, file_path)

        urls = extract_links_from_pdf(file_path)
        urls = [x for x in urls if x.startswith(v.replace("index.html", YEAR_PREFIX))]
        year_dict[k] = urls
    return year_dict
  
def download_html_as_pdf(url, output_pdf):
    logging(f"Start downloading...{url} {output_pdf}")

    try:
        pdfkit.from_url(url, output_pdf)
        logging(f"PDF saved successfully as {output_pdf}")
        return True
    except Exception as e:
        logging(f"Error occurred: {e}")
        return False
    
def generate_COUNTRY_NAMESPACE_DICT():
    dict_file_path = f"downloads/{uuid_str}/countries.json"
    COUNTRY_NAMESPACE_DICT = {}
    COUNTRY_NAMESPACE_DICT = get_countries_namespaces()
    save_dict_to_file(COUNTRY_NAMESPACE_DICT, dict_file_path)

    logging(COUNTRY_NAMESPACE_DICT)

    return COUNTRY_NAMESPACE_DICT

def generate_COUNTRY_YEAR_DICT():
    dict_file_path = f"downloads/{uuid_str}/countries_urls.json"
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
    dict_file_path = f"downloads/{uuid_str}/countries_years_urls.json"
    COUNTRY_YEAR_CASES_DICT = {}
    if FORCE_REFRESH is False and check_file_exists(dict_file_path):
        COUNTRY_YEAR_CASES_DICT = load_dict_from_file(dict_file_path)
    else:
        COUNTRY_YEAR_CASES_DICT = get_year_cases()
        save_dict_to_file(COUNTRY_YEAR_CASES_DICT, dict_file_path)
    
    return COUNTRY_YEAR_CASES_DICT
   
def convert_to_html(path, output_pdf):
    logging(f"Start downloading...{path} {output_pdf}")

    try:
        pdfkit.from_url(path, output_pdf)
        logging(f"PDF saved successfully as {output_pdf}")
        return True
    except Exception as e:
        logging(f"Error occurred: {e}")
        return False

def download_cases():
    return_msg = "Completed"
    status_msg = f"Start downloading cases..."

    logging(status_msg)

    start_time = time.perf_counter()

    for k,v in COUNTRY_YEAR_CASES_DICT.items():
        if v.items():
            for year, urls in v.items():
                for url in urls:
                    case_num = url.split("/")[-1].split(".")[0]
                    file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases/{case_num}.pdf"
                    create_directory_if_not_exists(f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases")

                    if FORCE_REFRESH is True or not check_file_exists(file_path):
                        st = time.perf_counter()
                        download_html_as_pdf(url, file_path)
                        dt = time.perf_counter() - st
                        hours, minutes, seconds = convert_to_hms(dt)
                        yield f"{file_path} Download time: {hours} hours, {minutes} minutes, {seconds} seconds"

            status_msg = f"All Cases for {k} for year {year} have been downloaded."

            logging(status_msg)
            yield f"{status_msg}  {datetime.datetime.now()}"
        else:
            return_msg = f"No cases for {k}"

    duration = time.perf_counter() - start_time
    hours, minutes, seconds = convert_to_hms(duration)

    yield f"{return_msg} Duration: {hours} hours, {minutes} minutes, {seconds} seconds"

async def report_per_country_local():
    start_time = time.perf_counter()
    conversion_stats = defaultdict(dict)
    logging(f"Start calculations...")

    for k,v in COUNTRY_YEAR_CASES_DICT.items():
       
        if v.items():
            for year, urls in v.items():
                conversion_stats[k][year] = {"missing": 0, "total": 0}
               
                for url in urls:
                    case_num = url.split("/")[-1].split(".")[0]
                    file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases/{case_num}.pdf"
                   
                    conversion_stats[k][year]["total"] +=1
                    if check_file_exists(file_path) is False:
                         conversion_stats[k][year]["missing"] +=1
                       
            logging(f"{conversion_stats}")
        else:
            return_msg = f"No stats for country {k}"

    duration = time.perf_counter() - start_time
    hours, minutes, seconds = convert_to_hms(duration)

    conversion_stats["duration"] = f"{hours} hours, {minutes} minutes, {seconds} seconds"
    return conversion_stats
        
async def objectstore_stats():
    return_msg = ""
    start_time = time.perf_counter()
    conversion_stats = defaultdict(dict)
  
   # Create S3 service client
    svc = boto_client('s3')

    for k,v in COUNTRY_YEAR_CASES_DICT.items():      
        if v.items():
            for year, urls in v.items():
                conversion_stats[k][year] = {"missing": 0, "total": 0}
               
                for url in urls:
                    case_num = url.split("/")[-1].split(".")[0]
                    file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases/{case_num}.pdf"
                   
                    conversion_stats[k][year]["total"] +=1

                    res = svc.list_objects_v2(Bucket=config["AWS_CREDENTIALS"]["BUCKET_NAME"], Prefix=file_path, MaxKeys=1)
                    if 'Contents' not in res:
                        conversion_stats[k][year]["missing"] +=1
                    
            logging(f"{conversion_stats}")
        else:
            logging (f"No stats for country {k}")

    duration = time.perf_counter() - start_time
    hours, minutes, seconds = convert_to_hms(duration)

    conversion_stats["duration"] = f"{hours} hours, {minutes} minutes, {seconds} seconds"

    return conversion_stats

async def upload_file(svc, path, file):
    file_s3 = os.path.normpath(path + '/' + file)
    file_local = os.path.join(path, file)
    response_msg = f"""Upload:{file_local} to target: {file_s3} """
    logging(response_msg)
    response = svc.upload_file(file_local, config["AWS_CREDENTIALS"]["BUCKET_NAME"], file_s3)
    logging(response)
    return f"response: {response} activity: {response_msg}"

async def upload_to_objectstore():
    return_msg = "Completed"
    start_time = time.perf_counter()
    
    # Create S3 service client
    svc = boto_client('s3')

    # Upload file
    for path, dirs, files in os.walk("downloads/"):
        logging(files)
        L = await asyncio.gather(*[upload_file(svc, path, file) for file in files])
        logging(L)
        yield L

    duration = time.perf_counter() - start_time
    hours, minutes, seconds = convert_to_hms(duration)

    yield f"{return_msg} Duration: {hours} hours, {minutes} minutes, {seconds} seconds"

async def whats_on_objectstore():
    return_msg = "Completed"

    start_time = time.perf_counter()    
    # Create S3 service client
    svc = boto_client('s3')
    response = svc.list_buckets()

    for bucket in response['Buckets']:
        yield f'{bucket["Name"]}'

    # List objects
    response = svc.list_objects_v2(Bucket=config["AWS_CREDENTIALS"]["BUCKET_NAME"])

    if response.get("Contents") is not None:
        for obj in response['Contents']:
            yield f'{obj["Key"]}'

    duration = time.perf_counter() - start_time
    hours, minutes, seconds = convert_to_hms(duration)

    yield f"{return_msg} Duration: {hours} hours, {minutes} minutes, {seconds} seconds"

async def init(filter,refresh=False):

    global uuid_str
    uuid_str = str(uuid.uuid4())

    global FORCE_REFRESH
    FORCE_REFRESH = refresh  == "True"

    global FILTER_COUNTRIES 
    FILTER_COUNTRIES = [x.lower() for x in filter["countries"]]

    global COUNTRY_NAMESPACE_DICT 
    COUNTRY_NAMESPACE_DICT = generate_COUNTRY_NAMESPACE_DICT()
    global COUNTRY_YEAR_DICT 
    COUNTRY_YEAR_DICT = generate_COUNTRY_YEAR_DICT()

    global COUNTRY_YEAR_CASES_DICT
    COUNTRY_YEAR_CASES_DICT = generate_COUNTRY_YEAR_CASES_DICT()
    