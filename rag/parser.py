import re
from typing import List, Tuple

def extract_docs_links_with_context(text: str) -> list:
    """
    Extract markdown links starting with '/docs/' along with the context in which they appear.
    For each link, the function records:
      - The markdown link URL (matching the pattern /docs/{variable})
      - The link label (the text between the square brackets [ ])
      - The nearest preceding Markdown heading (lines starting with '##')

    Args:
        text (str): The input text (e.g., the text resource from your Document)

    Returns:
        list: A list of dictionaries where each dictionary has:
              - "heading": the nearest '##' header (None if no header encountered yet)
              - "label": the link label extracted from the markdown link
              - "link": the URL part matching '/docs/{variable}'
    """
    result = []
    current_heading = None

    # Regex to capture markdown headers (lines starting with '##')
    header_regex = re.compile(r"^##\s*(.*)$")
    
    # Regex to capture markdown links of the form [label](/docs/...)
    link_regex = re.compile(r"\[([^\]]+)\]\(\s*(\/docs\/[^\)'\"]+)\s*\)")
    
    # Process the text line by line.
    lines = text.splitlines()
    for line in lines:
        # Check if the line is a header (starting with "##")
        header_match = header_regex.match(line)
        if header_match:
            current_heading = header_match.group(1).strip()
            current_heading = re.sub(r"[^A-Za-z0-9 ]+", "", current_heading)

        # Look for markdown links in the current line.
        for match in link_regex.finditer(line):
            raw_label = match.group(1).strip()
            link = match.group(2).strip()
            cleaned_label = re.sub(r"[^A-Za-z0-9 ]+", "", raw_label)
            result.append({
                "heading": current_heading,
                "label": cleaned_label,
                "link": link
            })
    return result


def extract_section_by_title(text: str, title_name: str) -> str:
    """
    Args:
        text (str): The complete document text.
        title_name (str): The title name to search for in the document.

    Returns:
        str: The extracted section text. Returns an empty string if the start marker is not found.
    """
    start_marker = f"\n\n# {title_name}\n\n"
    end_marker = "\n\nGot questions?"
    
    start_index = text.find(start_marker)
    if start_index == -1:
        # Start marker not found in the document.
        return ""
    
    # Move the start index to the end of the start marker.
    start_index += len(start_marker)
    
    end_index = text.find(end_marker, start_index)
    if end_index == -1:
        extracted = text[start_index:]
    else:
        extracted = text[start_index:end_index]
    
    # Prepend the markdown heading for the title to the extracted text.
    return f"# {title_name}\n\n{extracted}"

def update_titles(links_with_context: list, title_key: str = "title") -> list:
    """
    Update titles in the list of dictionaries by prepending the current heading to the title.
    
    Args:
        links_with_context (list): List of dictionaries where each dictionary has a title field.
        title_key (str): The key name for the title (default is "title").
        
    Returns:
        list: The updated list with modified titles.
    """
    current_prefix = ""
    for item in links_with_context:
        title = item.get(title_key, "")
        heading = item.get("heading", "")
        if title.startswith("__"):
            # Found a prefix header. Strip leading underscores and trim spaces.
            current_prefix = title.lstrip("_").strip()
        else:
            if current_prefix:
                # Prepend the current prefix and a space to the current title.
                item[title_key] = f"{heading} {current_prefix} {title}"
    return links_with_context

""" 
import re
import os
import json
from llama_index.readers.web import SimpleWebPageReader

# First, build a list of full URLs from links_with_context.
urls = []
for item in links_with_context:
    curr_link = item['link']
    full_url = f"https://help.zluri.com{curr_link}"
    urls.append(full_url)

# Load all documents once using the list of URLs.
reader = SimpleWebPageReader(html_to_text=True)
documents = reader.load_data(urls)

# Loop over each document along with its corresponding link data.
for idx, document in enumerate(documents):
    # Retrieve the corresponding item from links_with_context. 
    # (Assumes the order of documents returned matches the order of URLs provided.)
    item = links_with_context[idx]
    curr_label = item['label']
    extracted = extract_section_by_title(document.text, curr_label)
    # Add the extracted text back into the dictionary.
    item['text'] = extracted

# Optionally, export the list of dictionaries to a JSON file.
with open("extracted_docs.json", "w", encoding="utf-8") as f:
    json.dump(links_with_context, f, indent=4)

    
We extracted documentation structure and stored preprocessed knwoledge base in following form:
[
    {
        heading : Heading group under which this particular section comes in
        link : Link used to scrape the particular section
        label : Section title / label
        text : Preprocessed text containing information on each title section
    }
]
"""