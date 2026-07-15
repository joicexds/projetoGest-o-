import re

file_path = "core/views.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# For GastoForm, AdiantamentoForm, ReceitaForm
forms_to_update = ['GastoForm', 'AdiantamentoForm', 'ReceitaForm']

for form in forms_to_update:
    # Pattern to match form instantiation without user
    # form_adiantamento = AdiantamentoForm(request.POST) -> form_adiantamento = AdiantamentoForm(request.POST, user=request.user)
    # Be careful not to match ones already having user=request.user
    
    # regex matches: FormName(something) where something does not contain user=request.user
    pattern = rf"({form}\([^)]*)(?<!user=request\.user)(\))"
    
    def replacer(match):
        inner = match.group(1)
        if "user=request.user" in inner:
            return match.group(0)
        
        # if the parenthesis is empty e.g. AdiantamentoForm()
        if inner.endswith('('):
            return inner + "user=request.user)"
        else:
            return inner + ", user=request.user)"
            
    content = re.sub(pattern, replacer, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Form instantiations updated in views.py.")
