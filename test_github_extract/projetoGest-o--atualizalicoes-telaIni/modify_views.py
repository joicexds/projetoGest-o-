import re

file_path = "core/views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update .objects.all() to .objects.filter(usuario=request.user)
content = re.sub(r'\.objects\.all\(\)', r'.objects.filter(usuario=request.user)', content)

# 2. Update .objects.filter( to .objects.filter(usuario=request.user, 
content = re.sub(r'\.objects\.filter\((?!usuario=request.user)', r'.objects.filter(usuario=request.user, ', content)

# 3. Fix order_by that comes after objects directly e.g. .objects.order_by -> .objects.filter(usuario=request.user).order_by
content = re.sub(r'\.objects\.order_by\(', r'.objects.filter(usuario=request.user).order_by(', content)

# 4. Update get_object_or_404(Model, id=id) to get_object_or_404(Model, id=id, usuario=request.user)
content = re.sub(r'get_object_or_404\(([A-Za-z]+),\s*id=id\)', r'get_object_or_404(\1, id=id, usuario=request.user)', content)

# 5. Fix obj.save() in forms to inject request.user
# For generic form.save() in the views:
def replace_form_save(match):
    return """obj = form.save(commit=False)
            obj.usuario = request.user
            obj.save()"""

content = re.sub(r'form\.save\(\)(?!.*commit=False)', replace_form_save, content)

# 6. Inject request.user in funcionario_detail's inline forms
content = content.replace("registro.funcionario = funcionario", "registro.funcionario = funcionario\n                registro.usuario = request.user")
content = content.replace("adiantamento.funcionario = funcionario", "adiantamento.funcionario = funcionario\n                adiantamento.usuario = request.user")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Views updated successfully.")
