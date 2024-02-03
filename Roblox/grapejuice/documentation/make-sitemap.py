import sys

from typing import Union
from pathlib import Path
from string import Template

page_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$TITLE</title>
</head>
<body>

<h1>$TITLE</h1>

<ul>
$INDEX_ITEMS
</ul>

</body>
</html>
""")

def make_sitemap(title: str, root_path: Union[str, Path]):
    if not isinstance(root_path, Path):
        root_path = Path(root_path)

    root_path = root_path.resolve()

    files = [x.relative_to(root_path) for x in root_path.rglob("*") if x.is_file()]
    file_lines = [f"<li> <a href=\"{x}\">{x}</a> </li>" for x in files]

    page = page_template.substitute({
        "TITLE": title,
        "INDEX_ITEMS": "\n".join(file_lines)
    })

    with open("sitemap.html", "w+") as fp:
        fp.write(page)

if __name__ == "__main__":
    make_sitemap(sys.argv[1], sys.argv[2])