import pandas as pd
from string import Template
import requests
from bs4 import BeautifulSoup
import csv
from pyhtml2pdf import converter
import pdfkit
import pdfplumber
import os
import json

with open('web_scraper.json') as config_file:
    config = json.load(config_file)

### CONFIG
FILTER_COUNTRIES = config['FILTER_COUNTRIES']
YEAR_PREFIX = config["YEAR_PREFIX"]  ## any year starting with "20"
FORCE_REFRESH = False  ## Let this be false

BASE_URL = config["BASE_URL"]
COUNTRY_OUTPUT = config["COUNTRY_OUTPUT"]
FILTER_COUNTRIES = [x.lower() for x in FILTER_COUNTRIES]
COUNTRY_NAMESPACE_DICT = {}
COUNTRY_YEAR_DICT = {}
COUNTRY_NAMESPACE_URL_TEMPLATE = Template("${base_url}${country_lower}/cases/${country_upper}LawRp/index.html")
AVAILABLE_COUNTRY_LIST = config["AVAILABLE_COUNTRY_LIST"]

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

def check_file_exists(file_path):
    if os.path.isfile(file_path):
        print(f"File '{file_path}' exists.")
        return True
    else:
        print(f"File '{file_path}' does not exist.")
        return False


def save_dict_to_file(dictionary, file_path):
    with open(file_path, 'w') as file:
        json.dump(dictionary, file)
    print(f"Dictionary saved to '{file_path}'")


def load_dict_from_file(file_path):
    with open(file_path, 'r') as file:
        dictionary = json.load(file)
    print(f"Dictionary loaded from '{file_path}'")
    return dictionary

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
        print(f"Scraping completed. Data saved to {output_csv}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making the request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def download_html_as_pdf(url, output_pdf):
    print(f"Start downloading...{url} {output_pdf}")
    try:
        # Define path to wkhtmltopdf binary, if needed. Uncomment below line if wkhtmltopdf isn't in PATH
        # pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

        # Convert the given URL to a PDF and save it locally
        pdfkit.from_url(url, output_pdf)

       # weasyprint.HTML(url).write_pdf(output_pdf)

        #HTML(url).write_pdf(output_pdf)
       
        #converter.convert(url, output_pdf)

        print(f"PDF saved successfully as {output_pdf}")
    except Exception as e:
        print(f"Error occurred: {e}")


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


dict_file_path = "downloads/countries.json"
COUNTRY_NAMESPACE_DICT = {}
if check_file_exists(dict_file_path):
    COUNTRY_NAMESPACE_DICT = load_dict_from_file(dict_file_path)
else:
    COUNTRY_NAMESPACE_DICT = get_countries_namespaces()
    save_dict_to_file(COUNTRY_NAMESPACE_DICT, dict_file_path)
COUNTRY_NAMESPACE_DICT

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

dict_file_path = "downloads/countries_urls.json"
COUNTRY_YEAR_DICT = {}
if FORCE_REFRESH is False and check_file_exists(dict_file_path):
    COUNTRY_YEAR_DICT = load_dict_from_file(dict_file_path)
else:
    COUNTRY_YEAR_DICT = get_countries_years()
    for k,v in COUNTRY_YEAR_DICT.items():
        COUNTRY_YEAR_DICT[k] = [x + "index.html" for x in COUNTRY_YEAR_DICT[k]]
    save_dict_to_file(COUNTRY_YEAR_DICT, dict_file_path)
COUNTRY_YEAR_DICT

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

dict_file_path = "downloads/countries_years_urls.json"
COUNTRY_YEAR_CASES_DICT = {}
if FORCE_REFRESH is False and check_file_exists(dict_file_path):
    COUNTRY_YEAR_CASES_DICT = load_dict_from_file(dict_file_path)
else:
    COUNTRY_YEAR_CASES_DICT = get_year_cases()
    save_dict_to_file(COUNTRY_YEAR_CASES_DICT, dict_file_path)
COUNTRY_YEAR_CASES_DICT

def download_all_cases():
    print(f"Start downloading...")

    for k,v in COUNTRY_YEAR_CASES_DICT.items():
        for year, urls in v.items():
            for url in urls:
                case_num = url.split("/")[-1].split(".")[0]
                file_path = f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases/{case_num}.pdf"
                create_directory_if_not_exists(f"downloads/countries/{COUNTRY_NAMESPACE_DICT[k]}/{year}/cases")
                if check_file_exists(file_path) is False:
                    download_html_as_pdf(url, file_path)
        print(f"All Cases for {k} for year {year} have been downloaded.")
    return

download_all_cases()