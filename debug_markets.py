import requests
import json

r = requests.get('https://api.elections.kalshi.com/trade-api/v2/events', 
                 params={'limit': 200, 'with_nested_markets': 'true'})
d = r.json()

# Find 2028 presidential election
e = next((x for x in d.get('events', []) if x['event_ticker'] == 'KXPRESPERSON-28'), None)

if e:
    print(f"Event: {e['title']}")
    print(f"Markets: {len(e['markets'])}")
    print()
    for m in e['markets'][:15]:
        name = m.get('yes_sub_title', 'Unknown')
        yes_bid = m.get('yes_bid', 0)
        yes_ask = m.get('yes_ask', 0)
        last_price = m.get('last_price', 0)
        print(f"{name}: yes_bid={yes_bid}, yes_ask={yes_ask}, last_price={last_price}")
else:
    print("Event not found")
