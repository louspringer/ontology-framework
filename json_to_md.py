import json

def convert_json_to_md(json_data):
    if not isinstance(json_data, dict) or 'conversation' not in json_data:
        raise ValueError("Invalid JSON structure: missing 'conversation' key")
    if 'title' not in json_data['conversation']:
        raise ValueError("Invalid JSON structure: missing 'title' key")
    md_output = f"# {json_data['conversation']['title']}\n\n"
    
    # Initial Question
    md_output += "## Initial Question\n"
    md_output += f"**Q:** {json_data['conversation']['initial_question']['question']}\n\n"
    md_output += f"**A:** {json_data['conversation']['initial_question']['answer']}\n\n"
    
    # Memory Management
    md_output += "## Memory Management\n"
    md_output += f"**Q:** {json_data['conversation']['memory_management']['question']}\n\n"
    md_output += f"**A:** {json_data['conversation']['memory_management']['answer']}\n\n"
    
    # Solution Evolution
    md_output += "## Solution Evolution\n\n"
    md_output += "### Initial Implementation\n"
    md_output += f"{json_data['conversation']['solution_evolution']['initial_implementation']['description']}\n\n"
    md_output += "```python\n"
    md_output += f"{json_data['conversation']['solution_evolution']['initial_implementation']['code']}\n"
    md_output += "```\n\n"
    
    md_output += "### Final Implementation\n"
    md_output += f"{json_data['conversation']['solution_evolution']['final_implementation']['description']}\n\n"
    md_output += "```python\n"
    md_output += f"{json_data['conversation']['solution_evolution']['final_implementation']['code']}\n"
    md_output += "```\n\n"
    
    # Key Learnings
    md_output += "## Key Learnings\n\n"
    
    md_output += "### Cache Types\n"
    for item in json_data['conversation']['key_learnings']['cache_types']:
        md_output += f"- {item}\n"
    md_output += "\n"
    
    md_output += "### Memory Management\n"
    for item in json_data['conversation']['key_learnings']['memory_management']:
        md_output += f"- {item}\n"
    md_output += "\n"
    
    md_output += "### Best Practices\n"
    for item in json_data['conversation']['key_learnings']['best_practices']:
        md_output += f"- {item}\n"
    
    return md_output

def main():
    with open('bear.json', 'r') as f:
        json_data = json.load(f)
    
    markdown_content = convert_json_to_md(json_data)
    
    with open('bear.md', 'w') as f:
        f.write(markdown_content)

if __name__ == "__main__":
    main() 