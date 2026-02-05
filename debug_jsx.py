
import re

def check_structure(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    
    # Simple tokenizer for important symbols
    # We want to track: { } ( ) <div </div>
    # and maybe < > but > is ambiguous.
    
    for i, line in enumerate(lines):
        lnum = i + 1
        
        # Strip strings/comments roughly (simplified)
        # This is a heuristic parser
        
        # Look for tags
        # Find all <tag or </tag
        tags = re.finditer(r'</?([a-zA-Z0-9\.]+|>)', line)
        
        # Also find braces/parens
        # We need to process them in order of appearance
        
        # Tokenizer approach
        tokens = []
        
        # Tags
        for m in re.finditer(r'</?([a-zA-Z0-9\._]+)|/>', line):
            is_close = m.group(0).startswith('</')
            is_self_close = m.group(0).endswith('/>')
            tag_name = m.group(1) if not is_self_close else None
            if not is_self_close:
                tokens.append((m.start(), 'TAG', m.group(0), tag_name, is_close))
                
        # Braces
        for m in re.finditer(r'[\{\}\(\)\[\]]', line):
            tokens.append((m.start(), 'BRACE', m.group(0)))
            
        tokens.sort(key=lambda x: x[0])
        
        for t in tokens:
            kind = t[1]
            val = t[2]
            
            if kind == 'BRACE':
                if val in '{(':
                    stack.append((val, lnum))
                elif val == '}':
                    if not stack or stack[-1][0] != '{':
                        print(f"Error at {lnum}: Unexpected }} (Stack: {stack[-1] if stack else 'Empty'})")
                        return
                    stack.pop()
                elif val == ')':
                    if not stack or stack[-1][0] != '(':
                        print(f"Error at {lnum}: Unexpected ) (Stack: {stack[-1] if stack else 'Empty'})")
                        return
                    stack.pop()
                    
            elif kind == 'TAG':
                # Skip component tags or lower case?
                # Focus on div
                tag = t[3]
                if tag == 'div':
                    if t[4]: # Close </div
                        # Search stack for matching div
                        # Here we cheat and assume stack tracks tags too
                        # But we mixed braces and tags.
                        # Strict JSX mismatch: <div> { </div> } is invalid.
                        # So they share stack.
                        if not stack or stack[-1][0] != 'div':
                             print(f"Error at {lnum}: Unexpected </div> (Stack: {stack[-1] if stack else 'Empty'})")
                             # Don't return, keep going to see more context? No, strict.
                             # return 
                             pass # Warn
                        else:
                            stack.pop()
                    else: # Open <div
                        stack.append(('div', lnum))

    if stack:
        print(f"Unclosed items at EOF: {stack}")
    else:
        print("Structure OK")

check_structure("Frontend/src/components/FrameworkDetail.js")
