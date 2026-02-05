import os

target_path = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Frontend\src\components\Controls.js"

with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Automation Badge to UI
# Find where badges are rendered.
# <StatusBadge status={control.status} />
# We want to add another badge next to it. Since we can't easily parse JSX with python regex reliably, 
# we'll look for the specific line and append.

search_badge = """<StatusBadge status={control.status} />"""
replace_badge = """<StatusBadge status={control.status} />
                    <span className={`px-2 py-0.5 rounded text-xs border ${
                        control.automation_status === 'automated' 
                        ? 'bg-blue-50 text-blue-700 border-blue-200' 
                        : 'bg-gray-50 text-gray-600 border-gray-200'
                    }`}>
                        {control.automation_status === 'automated' ? 'Automated' : 'Manual'}
                    </span>"""

if search_badge in content:
    content = content.replace(search_badge, replace_badge)
    print("Added Automation Badge.")
else:
    print("Could not find StatusBadge location.")

# 2. Update Auto-Trigger Logic
# We previously injected:
# if (isExpanding) {
#    ... 
#    if (!data || data.length === 0 || ...) {
#        ... triggerAnalysis ...
#    }
# }
# We need to change the condition to:
# if (control.automation_status === 'automated' && (!data || ...))

search_logic = """if (!data || data.length === 0 || (data[0] && data[0].gaps && data[0].gaps.startsWith("AI Error"))) {"""
replace_logic = """// Only auto-trigger if Automated OR if user previously ran it (heuristic)
            const shouldAutoRun = control.automation_status === 'automated';
            
            if (shouldAutoRun && (!data || data.length === 0 || (data[0] && data[0].gaps && data[0].gaps.startsWith("AI Error")))) {"""

# We need access to `control` object inside toggleControl?
# `toggleControl` takes `id`. It finds control from `controls` state?
# Wait, `toggleControl = async (id) => { ... }`
# We need to find the control object first.
# `const control = controls.find(c => c.id === id);`
# I need to verify if `toggleControl` has access to `controls`. Yes, it's in the component scope.

logic_injection_search = """const toggleControl = async (id) => {"""
logic_injection_replace = """const toggleControl = async (id) => {
    const control = controls.find(c => c.id === id);"""

if logic_injection_search in content:
    content = content.replace(logic_injection_search, logic_injection_replace)
    print("Injected control lookup in toggleControl.")
else:
    print("Could not find toggleControl start.")

if search_logic in content:
    content = content.replace(search_logic, replace_logic)
    print("Updated Auto-Trigger Condition.")
else:
    print("Could not find previous Auto-Trigger condition.")

with open(target_path, 'w', encoding='utf-8') as f:
    f.write(content)
