import os
import json
from collections import defaultdict
from utils.password_manager import get_domain_name
from utils.file_manager import get_folder_path

TEMPLATE_FOLDER = get_folder_path("templates")

def save_template(url, process_manager, column_titles):
    try:
        create_folder()
        columns = []
        for i, column in enumerate(process_manager.columns):
            columns.append({
                "xpath": column.xpath,
                "visual_index": column.visual_index,
                "first_text": column.first_text,
                "num_elements": column.num_elements,
                "column_title": column_titles[i]
            })

        template = {
            "url": url,
            "pagination_xpath": process_manager.pagination_xpath,
            "columns": columns
        }

        domain = get_domain_name(url)
        count = 1
        while os.path.exists(_get_template_path(domain, count)):
            count += 1

        with open(_get_template_path(domain, count), "w") as f:
            json.dump(template, f)
            
        return True
    except Exception as e:
        print(f"Error saving template: {e}")
        return False

def create_folder():
    if not os.path.exists(TEMPLATE_FOLDER):
        os.makedirs(TEMPLATE_FOLDER)

def _get_template_path(domain, count):
    suffix = f"_({count})" if count > 1 else ""
    filename = f"{domain}{suffix}.json"
    return os.path.join(TEMPLATE_FOLDER, filename)

def list_templates():
    files = os.listdir(TEMPLATE_FOLDER)
    domains = defaultdict(int)
    for file in files:
        if file.endswith(".json"):
            domain = file[:-5]
            domains[domain] += 1

    domain_list = []
    for domain, count in domains.items():
        for i in range(1, count + 1):
            suffix = f"_({i})" if i > 1 else ""
            domain_list.append(f"{domain}{suffix}")

    return domain_list

def load_template(index):
    domain_list = list_templates()
    if index < 0 or index >= len(domain_list):
        return None

    domain = domain_list[index]
    with open(_get_template_path(domain, 0), "r") as f:
        template = json.load(f)

    return template

def get_column_data_from_template(template, key):
    result = []
    try:
        for column in template["columns"]:
            result.append(column[key])
        return result
    except Exception as e:
        print(f"Error getting data from template: {e}")
        return None

def get_domain(name):
    if "_" in name:
        return name.split("_")[0]
    else:
        return name
