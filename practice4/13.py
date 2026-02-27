import json
import re

def resolve_query(data, query):
    
    parts = query.split('.')
    current = data

    try:
        for part in parts:
            
            tokens = re.findall(r'[^\[\]]+|\[\d+\]', part)
            
            for token in tokens:
                if token.startswith('['):
                    
                    index = int(token[1:-1])
                    if not isinstance(current, list) or index >= len(current):
                        return "NOT_FOUND"
                    current = current[index]
                else:
                    
                    if not isinstance(current, dict) or token not in current:
                        return "NOT_FOUND"
                    current = current[token]

        return json.dumps(current, separators=(',', ':'))

    except:
        return "NOT_FOUND"


data = json.loads(input())
q = int(input())

for _ in range(q):
    query = input().strip()
    result = resolve_query(data, query)
    print(result)