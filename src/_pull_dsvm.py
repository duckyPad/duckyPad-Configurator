import os
import time
import requests

# Configuration
REPO_OWNER = "duckyPad"
REPO_NAME = "DuckStack"
DIRECTORY_PATH = "ds_compiler"
BRANCH = "master"

def download_py_files():
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{DIRECTORY_PATH}?ref={BRANCH}"
    
    response = requests.get(api_url)
    
    # Corrected attribute name below
    if response.status_code != 200:
        print(f"Error: Unable to fetch directory contents. Status code: {response.status_code}")
        print(f"Message: {response.json().get('message')}")
        return

    contents = response.json()

    for item in contents:
        time.sleep(0.1)
        if item['type'] == 'file' and item['name'].endswith('.py'):
            file_url = item['download_url']
            file_name = item['name']
            
            print(f"Downloading {file_name}...")
            
            file_response = requests.get(file_url)
            with open(file_name, 'wb') as f:
                f.write(file_response.content)

    print("\nDownload complete!")

if __name__ == "__main__":
    download_py_files()