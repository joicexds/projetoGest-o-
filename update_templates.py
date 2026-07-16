import os, glob

files = glob.glob('templates/*.html')
target1 = '<div class="user-info">Olá, {{ user.first_name|default:user.username }}</div>'
target2 = '<div class="user-info" style="display: flex; gap: 1rem;">\n                Olá, {{ user.first_name|default:user.username }}\n            </div>'
target3 = '<div class="user-info">\n                Olá, {{ user.first_name|default:user.username }}\n            </div>'
target4 = '<div class="user-info" style="display: flex; gap: 1rem;">Olá, {{ user.first_name|default:user.username }}</div>'
rep = "{% include 'includes/topbar_user.html' %}"

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'class="user-info"' in content:
        import re
        content = re.sub(r'<div class="user-info".*?>\s*Olá, \{\{ user\.first_name\|default:user\.username \}\}\s*</div>', rep, content, flags=re.DOTALL)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
