"""Validate this book's local publication files using the standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(r"(!?)\[[^\]\n]*\]\(([^)\n]+)\)")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")


def prose(text: str) -> str:
    """Exclude fenced examples so sample paths are not treated as links."""
    lines = []
    fence = ""
    for line in text.splitlines():
        match = FENCE.match(line)
        if not fence and match:
            fence = match[1]
        elif fence:
            if re.fullmatch(r"\s{0,3}" + re.escape(fence[0]) +
                            "{" + str(len(fence)) + r",}\s*", line):
                fence = ""
        else:
            lines.append(line)
    return "\n".join(lines)


def local_target(root: Path, source: Path, reference: str) -> Path | None:
    reference = reference.strip().strip("<>")
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    if parsed.path.startswith("/"):
        raise ValueError(f"site-root path: {reference}")
    target = (source.parent / unquote(parsed.path)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {reference}")
    return target


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    links = 0
    images: set[Path] = set()
    markdown = sorted(p for p in root.rglob("*.md")
                      if not any(part.startswith(".") for part in p.relative_to(root).parts))
    for file in markdown:
        data = file.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{file.relative_to(root)}: not UTF-8")
            continue
        if data.startswith(b"\xef\xbb\xbf") or b"\r" in data:
            errors.append(f"{file.relative_to(root)}: expected UTF-8 without BOM and LF")
        body = prose(text)
        for match in LINK.finditer(body):
            image, reference = match.groups()
            try:
                target = local_target(root, file, reference)
                if target is None:
                    if image:
                        errors.append(f"{file.relative_to(root)}: non-local body image")
                    continue
                links += 1
                if not target.is_file():
                    errors.append(f"{file.relative_to(root)}: missing {reference}")
                elif image:
                    images.add(target)
            except ValueError as exc:
                errors.append(f"{file.relative_to(root)}: {exc}")
        if file.parent.name == "articles" and file.name != "README.md":
            if re.search(r"<(?:figure|figcaption|img|pre)\b", body):
                errors.append(f"{file.name}: unsupported site HTML remains")
            if "/blog-covers/" in text or re.search(r"\]\(/blog-assets/", text):
                errors.append(f"{file.name}: site-only image reference remains")
            if not text.startswith("# "):
                errors.append(f"{file.name}: missing visible title")

    manifest = json.loads((root / "sources/import-manifest.json").read_text(encoding="utf-8"))
    if len(manifest["articles"]) != 5 or len(manifest["assets"]) != 32:
        errors.append("expected five source articles and 32 body images")
    destinations: set[str] = set()
    for item in manifest["articles"] + manifest["assets"]:
        destination = item["destination"]
        if destination in destinations:
            errors.append(f"duplicate manifest destination: {destination}")
        destinations.add(destination)
        file = (root / destination).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            errors.append(f"missing or invalid manifest path: {destination}")
            continue
        data = file.read_bytes()
        expected = item.get("sha256", item.get("local_sha256"))
        if hashlib.sha256(data).hexdigest() != expected:
            errors.append(f"hash mismatch: {destination}")
        if "bytes" in item:
            if len(data) != item["bytes"]:
                errors.append(f"size mismatch: {destination}")
            if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
                errors.append(f"invalid WebP header: {destination}")
            if file not in images:
                errors.append(f"unreferenced imported image: {destination}")
    figures = json.loads((root / "sources/figure-manifest.json").read_text(encoding="utf-8"))
    if len(figures["figures"]) != 8:
        errors.append("expected eight handbook figures")
    for item in figures["figures"]:
        destination = item["path"]
        file = (root / destination).resolve()
        if not file.is_relative_to(root) or not file.is_file():
            errors.append(f"missing or invalid figure: {destination}")
            continue
        if hashlib.sha256(file.read_bytes()).hexdigest() != item["sha256"]:
            errors.append(f"hash mismatch: {destination}")
        if file not in images:
            errors.append(f"unreferenced handbook figure: {destination}")
    chapters = sorted((root / "chapters").glob("*.md"))
    if len(chapters) != 10:
        errors.append("expected ten chapters")
    for required in ["README.md", "LICENSE.md", "LICENSE-CODE", "CONTRIBUTING.md",
                     "articles/README.md", "sources/README.md",
                     "examples/astrbot-napcat/compose.yaml",
                     "examples/astrbot-napcat/.env.example"]:
        if not (root / required).is_file():
            errors.append(f"missing required file: {required}")
    return {"ok": not errors, "markdown_files": len(markdown), "local_references": links,
            "referenced_images": len(images), "chapters": len(chapters), "errors": errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
