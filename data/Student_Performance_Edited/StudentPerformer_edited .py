
import requests
import json

# URL of the JSON data
url = "https://api.nusmods.com/v2/2023-2024/moduleList.json"  # Replace with your actual URL

# Fetch the data from the URL
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = response.json()  # If the response is JSON, requests can directly parse it
    module_codes = [module['moduleCode'] for module in data]
    print(module_codes) # Do something with the data, like printing or further processing
else:
    print(f"Failed to retrieve data: {response.status_code}")


