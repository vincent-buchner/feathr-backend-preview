import re

def isEmail(text: str) -> bool:
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.fullmatch(email_pattern, text))

def isUUID4(text: str) -> bool:
    uuid_pattern = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    return bool(re.fullmatch(uuid_pattern, text))