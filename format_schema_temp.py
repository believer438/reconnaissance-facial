from pathlib import Path
import re

path = Path('sql/schema.sql')
text = path.read_text(encoding='utf-8')
result = []
idx = 0
pattern = re.compile(r'CREATE TABLE "[^"]+" \(')
while idx < len(text):
    m = pattern.search(text, idx)
    if not m:
        result.append(text[idx:])
        break
    start = m.start()
    result.append(text[idx:start])
    level = 0
    in_quote = False
    pos = start
    while pos < len(text):
        ch = text[pos]
        if ch == '"':
            in_quote = not in_quote
        elif not in_quote:
            if ch == '(':
                level += 1
            elif ch == ')':
                level -= 1
                if level == 0 and text[pos:pos+2] == ');':
                    pos += 2
                    break
        pos += 1
    block = text[start:pos]
    header, body = block.split('(', 1)
    body = body.rsplit(')', 1)[0]
    fields = []
    current = []
    level = 0
    in_quote = False
    for ch in body:
        if ch == '"':
            in_quote = not in_quote
            current.append(ch)
        elif not in_quote:
            if ch == '(':
                level += 1
                current.append(ch)
            elif ch == ')':
                level -= 1
                current.append(ch)
            elif ch == ',' and level == 0:
                field = ''.join(current).strip()
                if field:
                    fields.append(field)
                current = []
            else:
                current.append(ch)
        else:
            current.append(ch)
    if current:
        field = ''.join(current).strip()
        if field:
            fields.append(field)
    new_block = header.strip() + ' (\n'
    for i, field in enumerate(fields):
        suffix = ',' if i < len(fields) - 1 else ''
        new_block += '    ' + field.strip() + suffix + '\n'
    new_block += ');\n\n'
    result.append(new_block)
    idx = pos
out = ''.join(result)
path.write_text(out, encoding='utf-8')
print('Reformat complete')
