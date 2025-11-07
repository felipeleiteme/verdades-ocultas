#!/usr/bin/env python3
"""Gera um EPUB a partir dos arquivos Markdown do manuscrito."""

from __future__ import annotations

import argparse
from pathlib import Path

from ebooklib import epub
import markdown

PROJECT_TITLE = (
    "Verdades Ocultas: Processos Inovadores para Entender o que os Clientes "
    "Realmente Querem (Antes Deles Mesmos)"
)
AUTHOR = "Felipe Leite"


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def build_epub(root: Path, output: Path) -> Path:
    manuscript = root / "manuscrito"
    chapters_dir = manuscript / "capitulos"
    files = [manuscript / "Sumario.md"] + sorted(chapters_dir.glob("capitulo_*.md"))

    book = epub.EpubBook()
    book.set_identifier("verdades-ocultas")
    book.set_title(PROJECT_TITLE)
    book.set_language("pt-BR")
    book.add_author(AUTHOR)

    chapters = []
    for idx, path in enumerate(files, start=1):
        text = path.read_text(encoding="utf-8")
        title = first_heading(text, path.stem)
        html = markdown.markdown(text, extensions=["extra", "toc"])
        chapter = epub.EpubHtml(
            title=title, file_name=f"chap_{idx:02d}.xhtml", lang="pt-BR"
        )
        chapter.content = f"<h1>{title}</h1>" + html
        book.add_item(chapter)
        chapters.append(chapter)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    output.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(output), book)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="dist/Verdades_Ocultas.epub",
        help="caminho final do EPUB (padrão: dist/Verdades_Ocultas.epub)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output_path = (repo_root / args.output).resolve()
    created = build_epub(repo_root, output_path)
    print(f"EPUB criado em {created}")


if __name__ == "__main__":
    main()
