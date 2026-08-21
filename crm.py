#!/usr/bin/env python3
"""
Twenty CRM management client for Orazen.
Uses the confirmed REST API at https://crm.orazen.online/rest
"""
import requests, json, sys
from typing import Optional

BASE = "https://crm.orazen.online/rest"
TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjBkYjQ3OWIwLWZlYTQtNGY0Yy1iY2ZlLWM2M2U4NmVlY2Y5ZSJ9.eyJzdWIiOiJhZTdlMGE5ZC1kOTFkLTRhYjEtYWYxMi1jMmY3NTAyMTk1OWEiLCJ1c2VySWQiOiJhZTdlMGE5ZC1kOTFkLTRhYjEtYWYxMi1jMmY3NTAyMTk1OWEiLCJ3b3Jrc3BhY2VJZCI6ImQ5NDdlNzNlLTRkN2QtNDQ1OC1hZTY0LTk3ODk3MjE5OGU2YyIsIndvcmtzcGFjZU1lbWJlcklkIjoiZWVlMDVjMTktNmRjOC00ZjcxLTkzYzEtMDcwMjJhOTJjNmNmIiwidXNlcldvcmtzcGFjZUlkIjoiZDYzNzZlZjQtMDA4NS00YzMwLThiMDktYzM1ZjYzMjZhZTA5IiwidHlwZSI6IlBMQVlHUk9VTkQiLCJhdXRoUHJvdmlkZXIiOiJwYXNzd29yZCIsImlhdCI6MTc4NzI4Nzc1OSwiZXhwIjoxNzg3Mjk0OTU5fQ.CLJs4Je25pM9KciikaD-zhV02tVpPnL2M0Hqtsg5vt_KzEVdAVQ6Di1lm60QmldVlpU9qZQudOA5Wv5R2wXTjw"

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

ORAZEN_STAGE_MAP = {
    "Lead": "NEW",
    "Contacted": "SCREENING",
    "Qualified": "SCREENING",
    "Demo": "MEETING",
    "Negotiation": "PROPOSAL",
    "Won": "CUSTOMER",
}

def oraizen_to_twenty_stage(stage: str) -> str:
    return ORAZEN_STAGE_MAP.get(stage, stage)

def twenty_to_orazen_stage(stage: str) -> str:
    inv = {v: k for k, v in ORAZEN_STAGE_MAP.items()}
    return inv.get(stage, stage)

def list_people(limit=20, cursor=None):
    params = {"limit": limit}
    if cursor:
        params["starting_after"] = cursor
    r = requests.get(f"{BASE}/people", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

def search_people(query, limit=10):
    r = requests.get(f"{BASE}/people", headers=HEADERS, params={"q": query, "limit": limit})
    r.raise_for_status()
    return r.json()

def create_person(first_name, last_name, email, phone=None, company_id=None):
    payload = {
        "name": {"firstName": first_name, "lastName": last_name},
        "emails": {"primaryEmail": email, "additionalEmails": []},
    }
    if phone:
        payload["phones"] = {"primaryPhoneNumber": phone, "primaryPhoneCountryCode": "", "primaryPhoneCallingCode": "+1", "additionalPhones": []}
    if company_id:
        payload["companyId"] = company_id
    r = requests.post(f"{BASE}/people", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

def list_companies(limit=20):
    r = requests.get(f"{BASE}/companies", headers=HEADERS, params={"limit": limit})
    r.raise_for_status()
    return r.json()

def create_company(name, domain=None):
    payload = {"name": name}
    if domain:
        payload["domainName"] = {
            "primaryLinkLabel": "Website",
            "primaryLinkUrl": f"https://{domain}",
            "secondaryLinks": []
        }
    r = requests.post(f"{BASE}/companies", headers=HEADERS, json=payload)
    r.raise_for_status()
    data = r.json()
    return data.get("data", {}).get("createCompany") or data.get("data", {}).get("company") or data

def list_opportunities(limit=20):
    r = requests.get(f"{BASE}/opportunities", headers=HEADERS, params={"limit": limit})
    r.raise_for_status()
    return r.json()

def create_opportunity(title, company_id, person_id=None, stage=None, amount=None, currency="EUR"):
    payload = {
        "title": title,
        "companyId": company_id,
    }
    if person_id:
        payload["personId"] = person_id
    if stage:
        payload["stage"] = stage
    if amount is not None:
        payload["amount"] = amount
        payload["currency"] = currency
    r = requests.post(f"{BASE}/opportunities", headers=HEADERS, json=payload)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: crm.py list_people | search <query> | create_person | create_company | create_opportunity | list_companies | list_opportunities")
        sys.exit(1)
    
    cmd = sys.argv[1]
    try:
        if cmd == "list_people":
            print(json.dumps(list_people(), indent=2))
        elif cmd == "search" and len(sys.argv) > 2:
            print(json.dumps(search_people(sys.argv[2]), indent=2))
        elif cmd == "create_person" and len(sys.argv) >= 5:
            print(json.dumps(create_person(sys.argv[2], sys.argv[3], sys.argv[4]), indent=2))
        elif cmd == "create_company" and len(sys.argv) >= 3:
            print(json.dumps(create_company(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None), indent=2))
        elif cmd == "create_opportunity" and len(sys.argv) >= 4:
            print(json.dumps(create_opportunity(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None), indent=2))
        elif cmd == "list_companies":
            print(json.dumps(list_companies(), indent=2))
        elif cmd == "list_opportunities":
            print(json.dumps(list_opportunities(), indent=2))
        else:
            print("Invalid command or missing args")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
