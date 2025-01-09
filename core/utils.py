import re
from typing import List, Tuple


def extract_search_replace_blocks(text):
    pattern = r"(<<<<<<< SEARCH.*?>>>>>> REPLACE)"
    matches = re.findall(pattern, text, re.DOTALL)
    
    return matches

def extract_json_blocks(text):
    pattern = r"```json\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    return matches

def extract_print_blocks(text) -> List[Tuple[str, str]]:
    pattern = r"(System\.out\.println\((.*?)\);)"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def remove_whitespace(text: str):
    text_lines = text.splitlines()
    new_text_lines = []
    for line in text_lines:
        new_text_lines.append(line.strip())
    return "\n".join(new_text_lines)