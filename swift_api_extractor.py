import subprocess
import json
import os

def run_sourcekitten_doc(file_path):
    """Run SourceKitten doc on a Swift file and return parsed JSON."""
    result = subprocess.run(
        ["sourcekitten", "doc", "--single-file", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    if result.returncode != 0:
        print(f"SourceKitten failed for {file_path}: {result.stderr}")
        return None
    try:
        data = json.loads(result.stdout)
        # sourcekitten doc outputs: { "filepath": { ... } }
        # So flatten to the inner dict:
        if isinstance(data, dict):
            data = next(iter(data.values()))
        return data
    except Exception as e:
        print(f"Failed to parse JSON for {file_path}: {e}")
        return None

def extract_entities(entities, indent=0):
    lines = []
    pad = '  ' * indent
    for entity in entities:
        kind = entity.get('key.kind', '')
        name = entity.get('key.name', '')
        doc = entity.get('key.doc.comment', '')
        typename = entity.get('key.typename', '')
        inherited = entity.get('key.inheritedtypes', [])
        inherited_str = ''
        if inherited:
            inherited_str = ': ' + ', '.join(t.get('key.name', '') for t in inherited)
        children = entity.get('key.substructure', [])
        
        # Type declarations
        if kind.endswith('class'):
            lines.append(f"{pad}class {name}{inherited_str}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        elif kind.endswith('struct'):
            lines.append(f"{pad}struct {name}{inherited_str}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        elif kind.endswith('protocol'):
            lines.append(f"{pad}protocol {name}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        elif kind.endswith('typealias'):
            lines.append(f"{pad}typealias {name} = {typename}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        elif kind.endswith('enum'):
            lines.append(f"{pad}enum {name}{inherited_str}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        elif kind.endswith('enum.case'):
            lines.append(f"{pad}case {name}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        # Functions
        elif 'function' in kind:
            params = []
            for child in children:
                if child.get('key.kind', '').endswith('var.parameter'):
                    param_name = child.get('key.name', '')
                    param_type = child.get('key.typename', '')
                    params.append(f"{param_name}: {param_type}")
            param_str = ', '.join(params)
            return_type = entity.get('key.typename', '')
            func_type = 'func'
            if '.function.static' in kind:
                func_type = 'static func'
            elif '.function.class' in kind:
                func_type = 'class func'
            lines.append(f"{pad}{func_type} {name}({param_str}) -> {return_type}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        # Variables
        elif 'var' in kind and not kind.endswith('var.parameter'):
            var_type = 'var'
            if '.var.static' in kind:
                var_type = 'static var'
            lines.append(f"{pad}{var_type} {name}: {typename}")
            if doc:
                lines.append(f"{pad}  Doc: {doc}")
        # Recursively process children
        if children:
            lines.extend(extract_entities(children, indent + 1))
    return lines

def process_swift_file(swift_file):
    data = run_sourcekitten_doc(swift_file)
    if not data:
        return []
    entities = data.get('key.substructure', [])
    return extract_entities(entities)

def main():
    # Find all .swift files in current directory and subdirectories
    swift_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.swift'):
                swift_files.append(os.path.join(root, file))

    all_lines = []
    for swift_file in swift_files:
        all_lines.append(f"\n# File: {swift_file}\n")
        all_lines.extend(process_swift_file(swift_file))

    # Write to file
    with open('swift_api_summary.txt', 'w') as out:
        out.write('\n'.join(all_lines))

    print("Done! Output written to swift_api_summary.txt")

if __name__ == '__main__':
    main()
