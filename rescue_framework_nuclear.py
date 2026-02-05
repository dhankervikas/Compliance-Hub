
import os

file_path = r"C:\Projects\Compliance_Product\Frontend\src\components\FrameworkDetail.js"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Truncate at line 1745 (just after p-8 opens)
# Line 1744 is index 1743. We want to keep it.
# So slice [:1744]
cut_index = 1744
new_lines = lines[:cut_index]

tail = """
                                            <div className="text-center py-12 text-gray-400">
                                                <p>Section Content Reset for Recovery</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )
                        }
                </div>
                </div>
            </>
        );
    };
};

export default FrameworkDetail;
"""

final_content = "".join(new_lines) + tail

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"Nuclear truncation at line {cut_index} applied.")
