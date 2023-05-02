import keyring
from cryptography.fernet import Fernet
import os
import platform
import json
from urllib.parse import urlparse

key_name = "scraping_interface_password_manager_key"
service_name = "scraping_interface"
file_name = "login.txt"

def create_key():
    # Password manager key
    stored_key = keyring.get_password(service_name, key_name)

    if stored_key is None:
        key = Fernet.generate_key()
        keyring.set_password(service_name, key_name, key.decode("utf-8"))
        print("Key generated and stored.")

def get_key():
    stored_key = keyring.get_password(service_name, key_name)
    if stored_key is None:
        create_key()
        stored_key = keyring.get_password(service_name, key_name)
    return stored_key.encode("utf-8")

def save_login_file(login_info):
    # Use the key to create a Fernet object
    cipher_suite = Fernet(get_key())

    # Read existing data from the file
    app_data_folder = get_app_data_folder()
    os.makedirs(app_data_folder, exist_ok=True)
    file_path = os.path.join(app_data_folder, file_name)

    # Decrypt the existing data if the file exists
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            encrypted_data = f.read()
            decrypted_data = cipher_suite.decrypt(encrypted_data).decode("utf-8")
            existing_login_data = json.loads(decrypted_data)
    else:
        existing_login_data = []

    # Extract the domain name from the given URL
    domain_name = get_domain_name(login_info['url'])

    if domain_name is None:
        return

    # Find the matching login info
    login_info_updated = False
    for i, stored_login_info in enumerate(existing_login_data):
        stored_domain_name = get_domain_name(stored_login_info['url'])

        if stored_domain_name is None:
            continue

        # If a matching domain is found, update the login_info
        if domain_name == stored_domain_name:
            existing_login_data[i] = login_info
            login_info_updated = True
            break

    # If no match is found, append the new login_info to the existing data
    if not login_info_updated:
        existing_login_data.append(login_info)

    # Convert the updated login data to a JSON string
    updated_login_data_json = json.dumps(existing_login_data)

    # Encrypt the JSON string
    encrypted_updated_login_data = cipher_suite.encrypt(updated_login_data_json.encode("utf-8"))

    # Store encrypted_updated_login_data securely in a file
    with open(file_path, "wb") as f:
        f.write(encrypted_updated_login_data)

    # Set file permissions to read and write for the owner only (chmod 600)
    os.chmod(file_path, 0o600)

def get_app_data_folder():
    system = platform.system()

    if system == "Windows":
        app_data_folder = os.path.join(os.environ["APPDATA"], "ScrapingInterface")
    elif system == "Darwin":  # macOS
        app_data_folder = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'ScrapingInterface')
    else:  # Linux and other Unix-based systems
        app_data_folder = os.path.join(os.path.expanduser('~'), '.scraping_interface')
    return app_data_folder

def get_login_info_for_url(url):
    # Use the key to create a Fernet object
    cipher_suite = Fernet(get_key())

    # Read encrypted data from the file
    app_data_folder = get_app_data_folder()
    file_path = os.path.join(app_data_folder, file_name)

    if not os.path.exists(file_path):
        return None

    with open(file_path, "rb") as f:
        encrypted_data = f.read()

    # Decrypt the data
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode("utf-8")
    login_data = json.loads(decrypted_data)

    domain_name = get_domain_name(url)
    if domain_name is None:
        return None

    # Find the matching login info
    for login_info in login_data:
        stored_domain_name = urlparse(login_info['url']).netloc.split(".")
        if len(stored_domain_name) >= 2:
            stored_domain_name = ".".join(stored_domain_name[-2:])
        else:
            continue

        if domain_name == stored_domain_name:
            return login_info

    # If no match is found, return None
    return None

def clear_stored_passwords():
    app_data_folder = get_app_data_folder()
    file_path = os.path.join(app_data_folder, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def get_domain_name(url):
    domain_name = urlparse(url).netloc.split(".")
    
    if len(domain_name) >= 2:
        domain_name = ".".join(domain_name[-2:])
    else:
        domain_name = None

    return domain_name
