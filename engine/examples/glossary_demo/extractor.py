from __future__ import annotations

import argparse
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import re


@dataclass(slots=True)
class GlossaryEntry:
    term: str
    definition: str
    score: float
    occurrences: int = 0
    sources: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def merge(self, other: "GlossaryEntry") -> None:
        self.occurrences += other.occurrences
        self.score += other.score
        for source in other.sources:
            if source not in self.sources:
                self.sources.append(source)
        for item in other.evidence:
            if item not in self.evidence:
                self.evidence.append(item)
        if len(other.definition) > len(self.definition):
            self.definition = other.definition

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["score"] = round(float(self.score), 3)
        return data


STOP_TERMS = {
    "todo",
    "notiz",
    "notizen",
    "beispiel",
    "quelle",
    "quellen",
    "index",
    "übersicht",
    "hinweis",
}


def extract_glossary(input_path: Path, min_score: float = 1.0) -> list[GlossaryEntry]:
    files = _collect_markdown_files(input_path)
    entries: dict[str, GlossaryEntry] = {}

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        for entry in _extract_from_text(text, file_path):
            key = entry.term.casefold()
            if key in entries:
                entries[key].merge(entry)
            else:
                entries[key] = entry

    result = [entry for entry in entries.values() if entry.score >= min_score]
    result.sort(key=lambda e: (-e.score, e.term.casefold()))
    return result


def write_outputs(entries: list[GlossaryEntry], markdown_out: Path, json_out: Path) -> None:
    markdown_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    markdown_out.write_text(render_markdown(entries), encoding="utf-8")
    json_out.write_text(
        json.dumps({"entries": [entry.to_dict() for entry in entries]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def render_markdown(entries: list[GlossaryEntry]) -> str:
    lines = [
        "# Automatisch extrahiertes Glossar",
        "",
        "Dieses Glossar wurde aus Markdown-Notizen erzeugt. Scores sind heuristisch und dienen nur als Priorisierung.",
        "",
        "| Begriff | Definition | Score | Quellen |",
        "|---|---|---:|---|",
    ]
    for entry in entries:
        definition = _escape_table(entry.definition or "Definition ergänzen.")
        sources = ", ".join(entry.sources)
        lines.append(f"| {_escape_table(entry.term)} | {definition} | {entry.score:.2f} | {_escape_table(sources)} |")
    lines.append("")
    return "\n".join(lines)


def _collect_markdown_files(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if not input_path.exists():
        raise FileNotFoundError(f"Input-Pfad existiert nicht: {input_path}")
    return sorted(p for p in input_path.rglob("*.md") if p.is_file())


def _extract_from_text(text: str, file_path: Path) -> list[GlossaryEntry]:
    entries: list[GlossaryEntry] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", stripped)
        if heading_match:
            term = _clean_term(heading_match.group(2))
            if _is_candidate(term):
                entries.append(
                    _entry(
                        term=term,
                        definition=_nearby_definition(lines, idx),
                        file_path=file_path,
                        line_number=idx,
                        score=3.0,
                        evidence=stripped,
                    )
                )

        bold_match = re.search(r"\*\*([^*]{2,90})\*\*\s*[:–—-]\s*(.+)$", stripped)
        if bold_match:
            term = _clean_term(bold_match.group(1))
            definition = _clean_definition(bold_match.group(2))
            if _is_candidate(term):
                entries.append(_entry(term, definition, file_path, idx, 4.0, stripped))

        colon_match = re.match(r"^(?:[-*]\s*)?([A-ZÄÖÜ][\wÄÖÜäöüß./&+_\- ]{1,90})\s*:\s*(.+)$", stripped)
        if colon_match:
            term = _clean_term(colon_match.group(1))
            definition = _clean_definition(colon_match.group(2))
            if _is_candidate(term):
                entries.append(_entry(term, definition, file_path, idx, 3.5, stripped))

        for term in _inline_candidates(stripped):
            if _is_candidate(term):
                entries.append(_entry(term, "", file_path, idx, 0.75, stripped))

    return entries


def _entry(term: str, definition: str, file_path: Path, line_number: int, score: float, evidence: str) -> GlossaryEntry:
    return GlossaryEntry(
        term=term,
        definition=definition,
        score=score,
        occurrences=1,
        sources=[f"{file_path.as_posix()}:{line_number}"],
        evidence=[evidence[:220]],
    )


def _nearby_definition(lines: list[str], line_number: int) -> str:
    # line_number ist 1-basiert; wir suchen in den naechsten drei nicht-leeren Zeilen.
    for candidate in lines[line_number : line_number + 3]:
        cleaned = _clean_definition(candidate)
        if cleaned and not cleaned.startswith("#"):
            return cleaned
    return ""


def _inline_candidates(line: str) -> list[str]:
    candidates: list[str] = []

    # CamelCase / Title Case mit 2-4 Worten, z. B. "Claude Code" oder "Quality Gate".
    for match in re.finditer(r"\b([A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,3})\b", line):
        candidates.append(_clean_term(match.group(1)))

    # Akronyme, z. B. RAG, CLI, API.
    for match in re.finditer(r"\b([A-ZÄÖÜ]{2,8})\b", line):
        candidates.append(_clean_term(match.group(1)))

    return candidates


def _clean_term(value: str) -> str:
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"\[[^\]]+\]\([^)]+\)", "", value)
    value = value.strip(" -–—:;,.!?\t\r\n")
    value = re.sub(r"\s+", " ", value)
    return value


def _clean_definition(value: str) -> str:
    value = re.sub(r"^[>*\-\s]+", "", value.strip())
    value = re.sub(r"[`*_~]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _is_candidate(term: str) -> bool:
    if not term:
        return False
    lowered = term.casefold()
    if lowered in STOP_TERMS:
        return False
    if len(term) < 2 or len(term) > 90:
        return False
    if len(term.split()) > 7:
        return False
    if re.fullmatch(r"\d+", term):
        return False
    if term.startswith("http"):
        return False
    return True


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python engine/examples/glossary_demo/extractor.py",
        description="Extrahiert ein Glossar aus Markdown-Notizen.",
    )
    parser.add_argument("--input", required=True, help="Markdown-Datei oder Ordner mit Markdown-Dateien")
    parser.add_argument("--out", required=True, help="Ausgabepfad fuer Markdown-Glossar")
    parser.add_argument("--json-out", required=True, help="Ausgabepfad fuer JSON-Glossar")
    parser.add_argument("--min-score", type=float, default=1.0, help="Mindestscore fuer Begriffe (default: 1.0)")
    args = parser.parse_args(argv)

    entries = extract_glossary(Path(args.input), min_score=args.min_score)
    write_outputs(entries, Path(args.out), Path(args.json_out))
    print(f"Glossar erzeugt: {args.out} ({len(entries)} Begriffe)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
