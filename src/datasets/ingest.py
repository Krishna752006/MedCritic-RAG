import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Iterable


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def parse_medquad(path: str) -> List[Dict[str, Any]]:
    """Parse a MedQuAD JSON (flexible formats) into a list of corpus entries.

    Output entry format:
    {"id": "MedQuAD-<n>", "title": str, "text": str, "source": "MedQuAD", "metadata": {...}}
    """
    p = Path(path)
    data = _load_json(p)
    entries: List[Dict[str, Any]] = []
    counter = 0

    # Case A: typical squad-like structure: {"data": [{"paragraphs":[{"context":...,"qas":[...]}]}]}
    if isinstance(data, dict) and 'data' in data:
        for article in data.get('data', []):
            title = article.get('title') or 'MedQuAD'
            for para in article.get('paragraphs', []):
                context = para.get('context', '')
                for qa in para.get('qas', []):
                    q = qa.get('question') or qa.get('q') or qa.get('query') or ''
                    a = ''
                    if 'answers' in qa and qa['answers']:
                        a = qa['answers'][0].get('text', '')
                    elif 'answer' in qa:
                        a = qa['answer']
                    counter += 1
                    entries.append({
                        'id': f'MedQuAD-{counter}',
                        'title': title,
                        'text': f"{context}\n\nQ: {q}\nA: {a}",
                        'source': 'MedQuAD',
                        'metadata': {'question': q, 'answer': a},
                    })
        return entries

    # Case B: list of qas or flat structure
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                q = item.get('question') or item.get('q') or item.get('query') or ''
                a = item.get('answer') or ''
                context = item.get('context') or item.get('passage') or ''
                counter += 1
                entries.append({
                    'id': f'MedQuAD-{counter}',
                    'title': item.get('title') or 'MedQuAD',
                    'text': f"{context}\n\nQ: {q}\nA: {a}",
                    'source': 'MedQuAD',
                    'metadata': {'question': q, 'answer': a},
                })
        return entries

    # Fallback: unknown format
    return entries


def parse_pubmedqa(path: str) -> List[Dict[str, Any]]:
    """Parse PubMedQA-like files. Supports JSONL, JSON array, and CSV with common column names.

    Output entry format mirrors parse_medquad with source 'PubMedQA'.
    """
    p = Path(path)
    entries: List[Dict[str, Any]] = []
    counter = 0

    # Try JSON lines
    try:
        with p.open('r', encoding='utf-8') as f:
            first = f.readline()
            f.seek(0)
            # Heuristic: if first char is '{' treat as jsonl or array
            if first.strip().startswith('{') or first.strip().startswith('['):
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        q = item.get('question') or item.get('query') or ''
                        context = item.get('context') or item.get('abstract') or ''
                        a = item.get('answer') or item.get('label') or ''
                        counter += 1
                        entries.append({
                            'id': f'PubMedQA-{counter}',
                            'title': item.get('title') or 'PubMedQA',
                            'text': f"{context}\n\nQ: {q}\nA: {a}",
                            'source': 'PubMedQA',
                            'metadata': {'question': q, 'answer': a},
                        })
                    return entries
    except Exception:
        # not JSON; continue to CSV attempt
        pass

    # Try CSV
    try:
        with p.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                q = row.get('question') or row.get('Question') or row.get('query') or ''
                context = row.get('context') or row.get('abstract') or ''
                a = row.get('answer') or row.get('label') or ''
                counter += 1
                entries.append({
                    'id': f'PubMedQA-{counter}',
                    'title': row.get('title') or 'PubMedQA',
                    'text': f"{context}\n\nQ: {q}\nA: {a}",
                    'source': 'PubMedQA',
                    'metadata': {'question': q, 'answer': a},
                })
        return entries
    except Exception:
        pass

    # Last resort: try reading as jsonl (line per json)
    try:
        with p.open('r', encoding='utf-8') as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    item = json.loads(ln)
                    q = item.get('question') or item.get('query') or ''
                    context = item.get('context') or item.get('abstract') or ''
                    a = item.get('answer') or item.get('label') or ''
                    counter += 1
                    entries.append({
                        'id': f'PubMedQA-{counter}',
                        'title': item.get('title') or 'PubMedQA',
                        'text': f"{context}\n\nQ: {q}\nA: {a}",
                        'source': 'PubMedQA',
                        'metadata': {'question': q, 'answer': a},
                    })
                except Exception:
                    continue
        return entries
    except Exception:
        return entries


def write_jsonl(entries: Iterable[Dict[str, Any]], out_path: str) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')


def merge_into_bm25(entries: List[Dict[str, Any]], bm25_path: str = 'data/knowledge/bm25_corpus.json') -> None:
    p = Path(bm25_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if p.exists():
        try:
            with p.open('r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # ensure unique ids by prefixing when conflicts
    existing_ids = {item.get('id') for item in existing if isinstance(item, dict)}
    new_entries = []
    for e in entries:
        eid = e.get('id')
        if not eid or eid in existing_ids:
            # create a new id
            base = e.get('source', 'doc')
            suffix = 1
            candidate = f"{base}-{suffix}"
            while candidate in existing_ids:
                suffix += 1
                candidate = f"{base}-{suffix}"
            e['id'] = candidate
            existing_ids.add(candidate)
        else:
            existing_ids.add(eid)
        new_entries.append(e)

    merged = existing + new_entries
    with p.open('w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    print('This module provides ingestion helpers; import and call parse_medquad/parse_pubmedqa from a script.')
