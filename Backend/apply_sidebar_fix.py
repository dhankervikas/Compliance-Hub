
import os

sidebar_source = "Sidebar_Premium.js"
sidebar_target = r"..\..\Frontend\src\components\Sidebar.js"
app_target = r"..\..\Frontend\src\App.js"

# 1. Apply Sidebar
try:
    with open(sidebar_source, "r", encoding="utf-8") as f:
        content = f.read()
    with open(sidebar_target, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Replaced Sidebar.js with Premium Layout.")
except Exception as e:
    print(f"Error applying sidebar: {e}")

# 2. Update App.js Routes
try:
    with open(app_target, "r", encoding="utf-8") as f:
        app_content = f.read()

    # Define Placeholder Component
    placeholder_cmp = """
const PlaceholderPage = ({ title }) => (
  <div className="p-8">
    <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
    <div className="bg-white p-12 rounded-xl border border-gray-200 shadow-sm text-center">
      <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
        <span className="text-2xl">🚧</span>
      </div>
      <h3 className="text-lg font-medium text-gray-900">Under Construction</h3>
      <p className="text-gray-500 mt-2">The <b>{title}</b> module is effectively linked but awaiting content.</p>
    </div>
  </div>
);
"""

    # Check if Placeholder is already there
    if "const PlaceholderPage" not in app_content:
        # Insert before function App()
        app_content = app_content.replace("function App()", f"{placeholder_cmp}\nfunction App()")

    # List of new routes to add
    new_routes = [
        '<Route path="/controls" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Controls" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/monitors" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Monitors" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/get-started" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Get Started" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/documents" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Documents" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/policies" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Policies" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/risk" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Risk Management" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/vendors" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Vendors" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/frameworks" element={<ProtectedRoute><ProtectedLayout><Dashboard /></ProtectedLayout></ProtectedRoute>} />', # Frameworks -> Dashboard for list
        '<Route path="/trust-report" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Trust Report" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/people" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="People" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/groups" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Groups" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/computers" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Computers" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/checklists" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Checklists" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/access" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Access" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/access-reviews" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Access Reviews" /></ProtectedLayout></ProtectedRoute>} />',
        '<Route path="/settings" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Settings" /></ProtectedLayout></ProtectedRoute>} />',
    ]

    # Insert Route definitions
    # Find the Dashboard route to insert after
    if '<Route path="/dashboard"' in app_content:
        # Construct the injection block
        injection = "\n          ".join(new_routes)
        # Find the line with dashboard
        lines = app_content.splitlines()
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if 'path="/dashboard"' in line and 'element={' in line and '/>' not in line: 
                # Multi-line route? Wait, App.js might be formatted.
                # Let's search for the closing tag of dashboard route or simply insert before the wildcard
                pass 
        
        # Simpler approach: Replace the Wildcard route with New Routes + Wildcard
        # Wildcard is: <Route path="*" ... />
        split_marker = '<Route path="/"' # Usually near the end
        if split_marker in app_content:
             parts = app_content.split(split_marker)
             app_content = parts[0] + injection + "\n          " + split_marker + parts[1]
             print("SUCCESS: Injected new routes into App.js")
             
             with open(app_target, "w", encoding="utf-8") as f:
                 f.write(app_content)
        else:
             print("WARNING: Could not find insertion point in App.js")

except Exception as e:
    print(f"Error updating App.js: {e}")
