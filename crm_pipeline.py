import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from crm import list_opportunities, create_opportunity, list_companies, create_company

BASE = Path(__file__).parent
orazen_companies = [
    ("Orazen", "orazen.online"),
    ("Bufala Bar", "bufalabar.it"),
    ("Crazy Smash", "crazysmash.it"),
    ("Bookoraa", "bookoraa.com"),
    ("OpenWA", "openwa.io"),
    ("WAora", "waora.io"),
]

print("=== Creating Orazen companies ===")
company_ids = {}
for name, domain in orazen_companies:
    try:
        c = create_company(name, domain)
        cid = c.get("data", {}).get("company", {}).get("id")
        company_ids[name] = cid
        print(f"✓ {name}: {cid}")
    except Exception as e:
        print(f"✗ {name}: {e}")

print("\n=== Creating pipeline opportunities ===")
stages = ["NEW", "CONTACTED", "QUALIFIED", "PROPOSAL", "NEGOTIATION", "WON", "LOST"]
for company_name, domain in orazen_companies:
    cid = company_ids.get(company_name)
    if not cid:
        continue
    
    for stage in stages:
        try:
            create_opportunity(
                title=f"{company_name} - {stage}",
                company_id=cid,
                stage=stage,
                amount=0,
                currency="EUR"
            )
        except Exception as e:
            print(f"✗ {company_name} {stage}: {e}")

print("\nPipeline setup complete")
