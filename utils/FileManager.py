import platform
import os

def get_app_data_folder():
    try:
        system = platform.system()

        if system == "Windows":
            app_data_folder = os.path.join(os.environ["APPDATA"], "ScrapingInterface")
        elif system == "Darwin":  # macOS
            app_data_folder = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'ScrapingInterface')
        else:  # Linux and other Unix-based systems
            app_data_folder = os.path.join(os.path.expanduser('~'), '.scraping_interface')

        if not os.path.exists(app_data_folder):
            os.makedirs(app_data_folder)
            print(f"Created default folder: {app_data_folder}")

        return app_data_folder
    except Exception as e:
        print(f"Error getting the App Data folder of the system: {e}")
        return None

def get_file_path(file_name):
    try:
        app_data_folder = get_app_data_folder()
        return os.path.join(app_data_folder, file_name) if app_data_folder else file_name
    except Exception as e:
        print(f"Error getting the file path: {e}")
        return file_name