"""
Clean invalid st.button kwargs (type, use_container_width, etc.)
and add stable key="..." args when missing in smart-notification-app.py.
Creates a .bak backup before writing changes.

Run (Windows PowerShell / cmd):
    cd "c:\Users\itzzzdave\Desktop\smart-notification-app"
    python .\tools\fix_streamlit_buttons.py
"""
import re
from pathlib import Path

SRC = Path(r"c:\Users\itzzzdave\Desktop\smart-notification-app\smart-notification-app.py")
if not SRC.exists():
    print("Source file not found:", SRC)
    raise SystemExit(1)

text = SRC.read_text(encoding="utf-8")
backup = SRC.with_suffix(SRC.suffix + ".bak")
backup.write_text(text, encoding="utf-8")
print("Backup written to", backup)

# Simple pattern (handles single- and multi-line st.button(...) calls)
pattern = re.compile(r"st\.button\((.*?)\)", re.DOTALL)

def replace_match(m):
    inner = m.group(1)
    # remove unsupported kwargs
    inner_clean = re.sub(r"\b(type|use_container_width)\s*=\s*[^,)\n]+,?", "", inner, flags=re.IGNORECASE)
    # collapse duplicated commas and trim
    inner_clean = re.sub(r",\s*,", ",", inner_clean)
    inner_clean = re.sub(r"^\s*,\s*", "", inner_clean)
    inner_clean = re.sub(r",\s*$", "", inner_clean)
    # if key already present, return cleaned
    if re.search(r"\bkey\s*=", inner_clean):
        return f"st.button({inner_clean})"

    # extract first string literal as label (if any) for key name
    label_match = re.match(r'\s*([\'"])(.*?)\1', inner_clean.strip(), re.DOTALL)
    label = label_match.group(2) if label_match else "button"
    safe = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_') or "button"
    key = f"{safe}_auto_{replace_match.counter}"
    replace_match.counter += 1

    # append key
    new_inner = inner_clean.strip()
    if new_inner:
        # ensure no trailing comma
        new_inner = new_inner.rstrip(',')
        new_inner = f'{new_inner}, key="{key}"'
    else:
        new_inner = f'key="{key}"'

    return f"st.button({new_inner})"

replace_match.counter = 1

new_text = pattern.sub(replace_match, text)

if new_text == text:
    print("No changes made (either no st.button found or already clean).")
else:
    SRC.write_text(new_text, encoding="utf-8")
    print("Updated file written:", SRC)
    print("Please restart your Streamlit app.")