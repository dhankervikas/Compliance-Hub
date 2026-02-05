
import os

file_path = r"C:\Projects\Compliance_Product\Frontend\src\components\FrameworkDetail.js"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Truncate at line 2200 (index 2199)
# The user wants to remove everything after 2200.
# Let's keep lines up to 2200.

# Determine correct closing sequence.
# Based on visual inspection of indentation around 2200 and previous debugging:
# We are inside:
# - Fragment <>
# - Main div (min-h-screen)
# - Control Drawer (selectedControl && ( ...
# - Fixed div
# - Relative div
# - Content div (p-8)
# - likely some conditional blocks.

# The safest way to "get it to compile" as requested:
# Close EVERYTHING aggressively.

# If we cut at 2200, we are inside `onClick` handlers and JSX.
# It's cleaner to cut slightly earlier, before the complex manual actions block, to ensure we aren't mid-expression.
# Line 2195 is `{/* HYBRID ACTIONS */}`
# Line 2196 is `{showHybridActions && (`
# Let's cut at 2195.

cut_index = 2195
new_lines = lines[:cut_index]

# We need to close:
# 1. The `p-8` div (from line 1858)
# 2. The `relative` div (from line 1735)
# 3. The `fixed` div (from line 1733)
# 4. The `selectedControl && (` block
# 5. The main `min-h-screen` div (from line 1180)
# 6. The Fragment `<>` (from line 1179)
# 7. The return statement `);`
# 8. The function `};`
# 9. The export.

tail = """
                                        </div>
                                    </div>
                                    );
                                })
                            })()}
                        </div>
                    </div>
                </div>
    )
}
</>
);
};

export default FrameworkDetail;
"""

final_content = "".join(new_lines) + tail

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"Truncated at line {cut_index} and appended closing tags.")
