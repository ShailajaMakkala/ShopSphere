import sys

filepath = r'd:\ShopSphere_Deployed\ShopSphere\data.json'
with open(filepath, 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    print("BOM found, removing...")
    with open(filepath, 'wb') as f:
        f.write(content[3:])
    print("BOM removed.")
else:
    print("No BOM found.")
