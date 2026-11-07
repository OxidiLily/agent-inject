#!/usr/bin/env python3
"""Cari bukti lokal dan catat ringkasan sesi non-rahasia."""
import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

WORD = re.compile(r"[\w-]{3,}", re.UNICODE)
SECRET = re.compile(r"(?i)(password|passwd|api[_ -]?key|secret|token|authorization)\s*[:=]\s*\S+")
MAX_BYTES = 128_000
AGENTS = {"claude", "codex", "hermes", "opencode", "openclaw"}


def search(root: Path, query: str, limit: int = 8):
    terms = set(WORD.findall(query.casefold()))
    sessions = root / "Sessions"
    if not sessions.is_dir() or sessions.is_symlink():
        raise ValueError(f"direktori Sessions tidak aman/tidak tersedia: {sessions}")
    results = []
    for file in sessions.rglob("*.md"):
        try:
            if file.is_symlink() or not file.resolve().is_relative_to(sessions.resolve()):
                continue
            if not file.is_file() or file.stat().st_size > MAX_BYTES:
                continue
            with file.open(encoding="utf-8", errors="replace") as stream:
                for number, line in enumerate(stream, 1):
                    matches = terms.intersection(WORD.findall(line.casefold()))
                    if matches and not SECRET.search(line):
                        results.append((len(matches), str(file), number))
        except (OSError, UnicodeError):
            continue
    return sorted(results, key=lambda row: (-row[0], row[1], row[2]))[:limit]


def clean(value: str, maximum: int):
    value = " ".join(value.split())
    if not value or len(value) > maximum or SECRET.search(value) or any(ord(c) < 32 for c in value):
        raise ValueError("catatan kosong, terlalu panjang, atau berpotensi berisi secret")
    return value.replace("\\", "\\\\").replace("`", "'").replace("[", "(").replace("]", ")")


def record(root: Path, agent: str, topic: str, question: str, answer: str, sources: str, problem: str = ""):
    if agent not in AGENTS:
        raise ValueError("agent tidak dikenal")
    topic, question, answer, sources = clean(topic, 80), clean(question, 400), clean(answer, 1200), clean(sources, 500)
    if problem:
        problem = clean(problem, 1000)
    sessions = root / "Sessions"
    if not sessions.is_dir() or sessions.is_symlink():
        raise ValueError(f"direktori Sessions tidak aman/tidak tersedia: {sessions}")
    slug = re.sub(r"[^a-z0-9]+", "-", topic.casefold()).strip("-")[:50]
    if not slug:
        raise ValueError("topik tidak valid")
    path = sessions / f"{slug}.md"
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_size > MAX_BYTES)):
        raise ValueError("target catatan tidak aman")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = f"### {now} — Agent: {agent}\n- Pertanyaan: {question}\n- Jawaban: {answer}\n- Sumber: {sources}\n"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(-\s*Terakhir diperbarui:\s*).*", rf"\g<1>{now}", text, count=1)
        marker = "## Timeline / Delta\n"
        text = text.replace(marker, marker + entry + "\n", 1) if marker in text else text.rstrip() + "\n\n" + entry
    else:
        text = (f"# {topic}\n\n- Dibuat: {now}\n- Terakhir diperbarui: {now}\n- Status: active\n\n"
                f"## Tujuan\n{question}\n\n## Konteks penting\n- Sumber: {sources}\n\n"
                f"## Keputusan\n- {answer}\n\n## Timeline / Delta\n{entry}\n"
                "## Verifikasi\n- N/A\n\n## Risiko / blocker\n- N/A\n\n"
                "## Langkah berikut\n- Menunggu tanggapan atau instruksi lanjutan dari pengguna.\n")
    if problem:
        marker = "## Masalah yang sering timbul\n"
        text = text.replace(marker, marker + f"- {problem}\n", 1) if marker in text else text.rstrip() + f"\n\n{marker}- {problem}\n"
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("catatan mencapai batas ukuran")
    temp = path.with_name(path.name + ".tmp")
    try:
        temp.write_text(text, encoding="utf-8", newline="\n")
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    lookup = subs.add_parser("search")
    lookup.add_argument("query")
    lookup.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    note = subs.add_parser("record")
    note.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    note.add_argument("--masalah", default="")
    for name in ("agent", "topic", "question", "answer", "sources"):
        note.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        if args.command == "search":
            rows = search(args.root, args.query)
            for _, file, line in rows:
                print(f"{file}:{line}")
            if not rows:
                print("Tidak ada bukti Sessions; lakukan riset terverifikasi. Jangan mengarang.")
        else:
            print(record(args.root, args.agent, args.topic, args.question, args.answer, args.sources, args.masalah))
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Gagal: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
