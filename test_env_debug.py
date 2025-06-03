from dotenv import load_dotenv
import os

load_dotenv()

print('Loaded GRAPHDB-related environment variables:')
for key in os.environ:
    if key.startswith('GRAPHDB'):
        print(f'{key}={os.environ[key]}') 