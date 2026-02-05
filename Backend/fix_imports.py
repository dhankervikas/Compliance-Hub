import sys 
sys.path.insert(0, '.') 
 
with open('app/services/ai_policy_service.py', 'r', encoding='utf-8') as f: 
    content = f.read() 
 
content = content.replace('from policy_template_structure', 'from app.services.policy_template_structure') 
content = content.replace('from policy_intents', 'from app.services.policy_intents') 
 
with open('app/services/ai_policy_service.py', 'w', encoding='utf-8') as f: 
    f.write(content) 
 
print('Fixed!') 
