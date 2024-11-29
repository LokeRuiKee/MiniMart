# Define the URL where Label Studio is accessible and the API key for your user account
LABEL_STUDIO_URL = 'http://localhost:8080'
# API key is available at the Account & Settings > Access Tokens page in Label Studio UI
API_KEY = '9845591928787ffc90f413c368b388d67c5b629f'

# Import the SDK and the client module
from label_studio_sdk.client import LabelStudio

# Connect to the Label Studio API and check the connection
ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=API_KEY)


