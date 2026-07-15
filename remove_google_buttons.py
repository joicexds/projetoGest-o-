import re

files = [
    "templates/registration/login.html",
    "templates/registration/cadastro.html"
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to match the entire social-login-container block
    pattern = r'<div class="social-login-container".*?</div>\s*</div>'
    
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Google buttons removed.")
