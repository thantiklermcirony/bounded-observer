"""Make the artifact version of index.html: the same page without its own skeleton,
since the Artifact runtime supplies one. Run from the repository root or from site/."""
import pathlib, re

here = pathlib.Path(__file__).resolve().parent
src = (here / "index.html").read_text()
body = re.search(r"<body>(.*)</body>", src, re.S).group(1)
out = here / ".artifact"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(body.strip() + "\n")
print("wrote", out / "index.html", len(body), "chars")
