import os
import requests

WORKFLOW_ID = "8e635116-b18e-4ffb-b56d-43086b995d76"
API_KEY = os.getenv("IBM_AGENT_STUDIO_API_KEY")

URLS_TO_TRY = [
    f"https://agentstudio.servicesessentials.ibm.com/api/v1/run/{WORKFLOW_ID}",
    f"https://langflow.servicesessentials.ibm.com/api/v1/run/{WORKFLOW_ID}",
]

payload = {
    "input_value": "hello from apitest",
    "input_type": "chat",
    "output_type": "chat",
}

headers = {
    "x-api-key": API_KEY or "",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

for url in URLS_TO_TRY:
    print("\n=== Testing:", url, "===")
    r = requests.post(url, json=payload, headers=headers, timeout=60, allow_redirects=True)

    print("Final URL:", r.url)
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("content-type", ""))

    # Print first 400 chars so we can see login HTML vs JSON
    body = (r.text or "").strip()
    print("Body (first 400 chars):")
    print(body[:400])

    # If JSON, print keys
    if "application/json" in (r.headers.get("content-type") or ""):
        try:
            j = r.json()
            print("JSON keys:", list(j.keys())[:20])
        except Exception as e:
            print("JSON parse error:", e)