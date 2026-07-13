"""CLI for ingesting MedQuAD and PubMedQA into the project's BM25 corpus.

Usage examples:
  python scripts/ingest_medical_datasets.py --medquad path/to/medquad.json --pubmedqa path/to/pubmedqa.jsonl --out-dir data/knowledge/ingested
  python scripts/ingest_medical_datasets.py --pubmedqa data/pubmedqa.csv --merge-bm25

If --merge-bm25 is set, the parsed entries will be appended to data/knowledge/bm25_corpus.json
"""
import argparse
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path so `from src...` imports work when
# running scripts from the `scripts/` directory.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.datasets.ingest import parse_medquad, parse_pubmedqa, write_jsonl, merge_into_bm25


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--medquad', type=str, help='Path to MedQuAD JSON file')
    parser.add_argument('--pubmedqa', type=str, help='Path to PubMedQA file (jsonl/json/csv)')
    parser.add_argument('--out-dir', type=str, default='data/knowledge/ingested', help='Directory to write ingested jsonl files')
    parser.add_argument('--merge-bm25', action='store_true', help='Merge ingested documents into data/knowledge/bm25_corpus.json')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    merged_entries = []

    if args.medquad:
        print(f'Parsing MedQuAD from {args.medquad}...')
        med_entries = parse_medquad(args.medquad)
        out_path = out_dir / 'medquad_corpus.jsonl'
        write_jsonl(med_entries, str(out_path))
        print(f'Wrote {len(med_entries)} MedQuAD entries to {out_path}')
        total += len(med_entries)
        merged_entries.extend(med_entries)

    if args.pubmedqa:
        print(f'Parsing PubMedQA from {args.pubmedqa}...')
        pub_entries = parse_pubmedqa(args.pubmedqa)
        out_path = out_dir / 'pubmedqa_corpus.jsonl'
        write_jsonl(pub_entries, str(out_path))
        print(f'Wrote {len(pub_entries)} PubMedQA entries to {out_path}')
        total += len(pub_entries)
        merged_entries.extend(pub_entries)

    if total == 0:
        print('No datasets provided; nothing to do.')
        return

    print(f'Total ingested entries: {total}')

    if args.merge_bm25:
        bm25_path = 'data/knowledge/bm25_corpus.json'
        print(f'Merging {total} entries into {bm25_path}...')
        merge_into_bm25(merged_entries, bm25_path)
        print('Merge completed.')


if __name__ == '__main__':
    main()
