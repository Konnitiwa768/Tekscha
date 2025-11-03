import zipfile, os, sys

zipname = "custom_inventory_no_frame.zip"
outdir = "custom_inventory_no_frame"

def safe_join(base, *names):
    path = os.path.normpath(os.path.join(base, *names))
    if not os.path.commonpath([os.path.abspath(base)]) == os.path.commonpath([os.path.abspath(base), os.path.abspath(path)]):
        return None
    return path

with zipfile.ZipFile(zipname, 'r') as z:
    for member in z.infolist():
        name = member.filename.replace('\\', '/')
        while name.startswith('/') or (len(name) >= 2 and name[1] == ':' and name[0].isalpha()):
            if name.startswith('/'):
                name = name.lstrip('/')
            else:
                name = name[2:].lstrip('/')
        name = os.path.normpath(name)
        if name == "" or name.startswith(".."):
            print(f"Skipping unsafe entry: {member.filename}", file=sys.stderr)
            continue
        dest_path = safe_join(outdir, name)
        if dest_path is None:
            print(f"Skipping path outside destination: {member.filename}", file=sys.stderr)
            continue
        if member.is_dir() or name.endswith('/'):
            os.makedirs(dest_path, exist_ok=True)
            continue
        parent = os.path.dirname(dest_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with z.open(member, 'r') as src, open(dest_path, 'wb') as dst:
            dst.write(src.read())
