
import os

target_path = r"..\..\Frontend\src\components\FrameworkDetail.js"

# Read existing
with open(target_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace header
old_header = r"""<h1 className="text-3xl font-bold text-gray-900">{framework.name}</h1>"""
new_header = r"""<h1 className="text-3xl font-bold text-gray-900">
                            {framework.name} <span className="text-sm font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded-full align-middle">(Hierarchy View)</span>
                        </h1>"""

if old_header in content:
    new_content = content.replace(old_header, new_header)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: Added Version Tag.")
else:
    print("WARNING: Header pattern not found. File might already be updated.")
