import os

target_path = r"C:\Users\dhank\OneDrive\Documents\Compliance_Product\Frontend\src\components\Controls.js"

with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target the button onClick handler logic to REPLICATE it in the auto-trigger logic if we were to inject it.
# BUT wait, we want to inject it inside the `onClick`? NO, we want it when expanded.
# The current code fetches data ONLY when button is clicked?
# Let's check the code:
# It seems assessments are fetched when?
# Ah, the code DOES NOT fetch assessments on expand automatically? 
# In `Controls.js`: 
# {expandedControl === control.id && ( ... 
#    {assessments[control.id] ... ? ... : <button onClick={trigger}>}
# }
# It seems `assessments` are not fetched on expand.
# We need to add `useEffect` or fetch on expand logic.
# However, Controls.js is a functional component.
# We can change `toggleControl` to fetch if missing.

search_str = """  const toggleControl = (id) => {
    setExpandedControl(expandedControl === id ? null : id);
  };"""

replace_str = """  const toggleControl = async (id) => {
    const isExpanding = expandedControl !== id;
    setExpandedControl(isExpanding ? id : null);
    
    if (isExpanding) {
        // Auto-fetch and Auto-Trigger logic
        try {
            let data = await assessmentService.getForControl(id);
            
            // AUTOMATION: If no data or error, trigger analysis automatically
            if (!data || data.length === 0 || (data[0] && data[0].gaps && data[0].gaps.startsWith("AI Error"))) {
                console.log("Auto-triggering AI for control", id);
                // Optionally show loading state here if we had one
                await assessmentService.triggerAnalysis(id);
                data = await assessmentService.getForControl(id);
            }
            
            setAssessments(prev => ({ ...prev, [id]: data }));
        } catch (e) {
            console.error("Auto-fetch failed", e);
        }
    }
  };"""

if search_str in content:
    new_content = content.replace(search_str, replace_str)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Injected Auto-Trigger into toggleControl.")
else:
    print("Could not find toggleControl definition.")
