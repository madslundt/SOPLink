import re

def reformat_markdown(content: str) -> str:
    # Use regex to replace 3 or more newlines with 2 newlines
    cleaned_content = re.sub(r'\n{3,}', '\n\n', content)

    return cleaned_content