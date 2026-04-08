import requests
import os
from PIL import Image
from datetime import datetime

# Config
GITHUB_USER = "thmspllgr"
TOKEN = os.getenv("GITHUB_TOKEN")

def image_to_ascii_svg(image_path, new_width=130, start_x=30, start_y=55, line_height=10):
    ASCII_CHARS = ["@", "#", "8", "&", "o", ":", "*", ".", " "]
    
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Image not found ({e}). Placeholder.")
        return f'<text x="{start_x}" y="{start_y}" class="title">[Image simulation.png not found]</text>'

    # Resize
    width, height = image.size
    ratio = height / width / 3.1
    new_height = int(new_width * ratio)
    image = image.resize((new_width, new_height)).convert("L")
    pixels = image.getdata()
    
    ascii_str = ""
    for pixel in pixels:
        index = pixel * len(ASCII_CHARS) // 256
        index = min(index, len(ASCII_CHARS) - 1)
        ascii_str += ASCII_CHARS[index]
    
    svg_output = ""
    current_y = start_y
    img_width = image.width
    
    for i in range(0, len(ascii_str), img_width):
        line = ascii_str[i:i+img_width]
        line = line.replace("&", "&amp;").replace(" ", "&#160;")
        svg_output += f'  <text x="{start_x}" y="{current_y}" class="title" xml:space="preserve">{line}</text>\n'
        current_y += line_height
        
    return svg_output

def get_github_stats():
    headers = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
    
    # Repos
    user_url = f"https://api.github.com/users/{GITHUB_USER}"
    user_data = requests.get(user_url, headers=headers).json()
    public_repos = user_data.get("public_repos", 0)

    # Stars
    repos_url = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100"
    repos_data = requests.get(repos_url, headers=headers).json()
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data) if isinstance(repos_data, list) else 0

    return {
        "{{REPOS}}": str(public_repos),
        "{{STARS}}": str(total_stars),
        "{{COMMITS}}": "more than 1",
        "{{EMAIL}}": "thomas.pellegrin@etu.unistra.fr"
    }

def main():
    print("Generating ASCII")
    ascii_art = image_to_ascii_svg("simulation.png")
    
    print("Retrieving GitHub stats")
    stats = get_github_stats()
    
    print("Reading template.svg")
    try:
        with open("template.svg", "r", encoding="utf-8") as file:
            svg_content = file.read()
    except FileNotFoundError:
        print("template.svg not found.")
        return

    print("Injecting data")
    svg_content = svg_content.replace("{{ASCII_ART}}", ascii_art)
    for key, value in stats.items():
        svg_content = svg_content.replace(key, value)

    print("Saving github_stats.svg")
    with open("github_stats.svg", "w", encoding="utf-8") as file:
        file.write(svg_content)
    
    print(f"[{datetime.now()}] success")

if __name__ == "__main__":
    main()
