#!/usr/bin/env python3
"""
Sync approved outreach leads into Twenty CRM.
Reads leads/tracker.md for approved rows with emails,
then creates Person + Company + Opportunity in CRM.
"""
import re, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from crm import create_person, create_company, create_opportunity, oraizen_to_twenty_stage

BASE = Path(__file__).parent.parent / "orazen-lead-engine"
TRACKER = BASE / "leads" / "tracker.md"

def extract_email(contact_text):
    """Extract email from contact column like 'email: x@y.com' or just 'x@y.com'."""
    if not contact_text:
        return None
    m = re.search(r'[\w\.-]+@[\w\.-]+', contact_text)
    return m.group(0) if m else None

def parse_tracker(path):
    text = path.read_text()
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 5:
            continue
        # Skip header and separator rows
        if parts[0].lower() in ["business", "---", "businesses"]:
            continue
        
        business = parts[0]
        problem = parts[1] if len(parts) > 1 else ""
        offer = parts[2] if len(parts) > 2 else ""
        contact = parts[3] if len(parts) > 3 else ""
        status = parts[4] if len(parts) > 4 else ""
        
        rows.append({
            "business": business,
            "problem": problem,
            "offer": offer,
            "contact": contact,
            "status": status,
        })
    return rows

def sync_approved():
    rows = parse_tracker(TRACKER)
    approved = [r for r in rows if r["status"].lower() == "approved"]
    print(f"Found {len(approved)} approved leads")
    
    synced = 0
    for row in approved:
        email = extract_email(row["contact"])
        if not email:
            print(f"⚠ Skipping {row['business']} - no email")
            continue
        
        # Extract name from business name
        full_name = row["business"].split(" - ")[0].split(" | ")[0].strip()
        parts = full_name.split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
        
        try:
            # Create company
            company = create_company(row["business"])
            company_id = company.get("data", {}).get("company", {}).get("id")
            
            # Create person
            person = create_person(first, last, email, company_id=company_id)
            person_id = person.get("data", {}).get("person", {}).get("id")
            
            # Create opportunity
            twenty_stage = oraizen_to_twenty_stage("Lead")
            create_opportunity(
                title=f"Orazen SaaS - {row['business']}",
                company_id=company_id,
                person_id=person_id,
                stage=twenty_stage,
                amount=149,
                currency="EUR"
            )
            
            print(f"✓ Synced: {email} ({row['business']})")
            synced += 1
        except Exception as e:
            print(f"✗ Failed {email}: {e}")
    
    print(f"\nSynced {synced}/{len(approved)} leads to CRM")

if __name__ == "__main__":
    sync_approved()
