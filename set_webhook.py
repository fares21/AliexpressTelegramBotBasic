import requests

TOKEN = '7203070953:AAHTg1OwfXo3koUeO_IsHRjnvXsAcjYaY9w'
WEBHOOK_URL = 'https://d14d-196-65-23-91.ngrok-free.app/webhook'  # Ensure to add /webhook at the end

url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
response = requests.get(url)
print(response.json())
