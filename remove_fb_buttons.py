import re

files = [
    "templates/registration/login.html",
    "templates/registration/cadastro.html"
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Pattern to match the facebook link tag block
    # It starts with <a href="{% provider_login_url 'facebook' %}" ... and ends with </a>
    pattern = r'<a href="\{% provider_login_url \'facebook\' %\}"[^>]*>.*?</a>'
    
    # Remove the match, dotall so it matches across newlines
    new_content = re.sub(pattern, "", content, flags=re.DOTALL)
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Facebook buttons removed.")
