import requests
import glob
import sys

files = sorted(glob.glob('guidance/modules/*.ttl'))
url = 'http://localhost:7200/mcp'

for f in files:
    payload = {
        'jsonrpc': '2.0',
        'id': f,
        'method': 'validate_guidance',
        'params': {'ontology_path': f}
    }
    print(f'Validating {f}...')
    r = requests.post(url, json=payload)
    try:
        resp = r.json()
    except Exception as e:
        print(f'Error parsing response for {f}: {e}')
        sys.exit(1)
    print(resp)
    if 'error' in resp or (isinstance(resp.get('result'), dict) and not str(resp['result'].get('result', '')).startswith('Validated')):
        print(f'Validation failed for {f}')
        sys.exit(1)
print('All ontologies validated successfully.') 