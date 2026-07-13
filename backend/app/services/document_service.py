import json
import mimetypes
import re
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from backend.app.config.settings import settings
from backend.app.services.ocr_service import OCRService


class DocumentService:
    def __init__(self, ocr_service: OCRService | None = None):
        self.ocr_service = ocr_service or OCRService()
        self.storage_dir = settings.document_storage_dir
        self.original_dir = self.storage_dir / "originals"
        self.text_dir = self.storage_dir / "extracted_text"
        self.metadata_dir = self.storage_dir / "metadata"
        self._records: dict[str, dict] = {}
        for directory in (self.original_dir, self.text_dir, self.metadata_dir):
            directory.mkdir(parents=True, exist_ok=True)
        self._load_existing_metadata()

    def upload_document(self, file: UploadFile, chat_id: str | None = None) -> dict:
        filename = self._sanitize_filename(file.filename or "uploaded_document")
        extension = Path(filename).suffix.lower()
        if extension not in settings.allowed_report_extensions:
            raise ValueError("Unsupported file format. Please upload PDF, PNG, JPG, JPEG, or TIFF.")

        size_bytes = self._get_size(file)
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValueError(f"File is too large. Maximum allowed size is {settings.max_upload_mb} MB.")

        document_id = str(uuid.uuid4())
        stored_filename = f"{document_id}_{filename}"
        storage_path = self.original_dir / stored_filename

        file.file.seek(0)
        with storage_path.open("wb") as output:
            shutil.copyfileobj(file.file, output)

        is_image = extension in {".png", ".jpg", ".jpeg", ".tiff"}
        extracted_text = self.ocr_service.extract_text(str(storage_path), is_image=is_image)
        layout_metadata = self.ocr_service.extract_layout_metadata(str(storage_path), is_image=is_image)
        layout_metadata["ocr_fallback_used"] = bool(is_image or layout_metadata.get("ocr_fallback_used"))

        text_path = self.text_dir / f"{document_id}.txt"
        text_path.write_text(extracted_text, encoding="utf-8")

        record = {
            "id": document_id,
            "chat_id": chat_id,
            "original_filename": filename,
            "stored_filename": stored_filename,
            "content_type": file.content_type or mimetypes.guess_type(filename)[0],
            "size_bytes": size_bytes,
            "storage_path": str(storage_path),
            "extracted_text_path": str(text_path),
            "extracted_text": extracted_text,
            "metadata": {
                "extension": extension,
                "is_image": is_image,
                "layout": layout_metadata,
                "text_length": len(extracted_text),
            },
        }
        self._save_metadata(record)
        self._records[document_id] = record
        return self._public_record(record)

    def list_documents(self, chat_id: str | None = None) -> list[dict]:
        records = list(self._records.values())
        if chat_id:
            records = [record for record in records if record.get("chat_id") == chat_id]
        return [self._public_record(record) for record in records]

    def get_document(self, document_id: str) -> dict:
        record = self._records.get(document_id)
        if not record:
            raise KeyError(f"Document not found: {document_id}")
        return self._public_record(record)

    def get_extracted_text(self, document_id: str) -> dict:
        record = self._records.get(document_id)
        if not record:
            raise KeyError(f"Document not found: {document_id}")
        path = Path(record["extracted_text_path"])
        text = path.read_text(encoding="utf-8") if path.exists() else record.get("extracted_text", "")
        return {"document_id": document_id, "text": text}

    def _get_size(self, file: UploadFile) -> int:
        if getattr(file, "size", None) is not None:
            return int(file.size)
        current = file.file.tell()
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(current)
        return size

    def _sanitize_filename(self, filename: str) -> str:
        name = Path(filename).name
        name = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
        return name or "uploaded_document"

    def _save_metadata(self, record: dict) -> None:
        metadata_path = self.metadata_dir / f"{record['id']}.json"
        metadata_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    def _load_existing_metadata(self) -> None:
        for metadata_path in self.metadata_dir.glob("*.json"):
            try:
                record = json.loads(metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            self._records[record["id"]] = record

    def _public_record(self, record: dict) -> dict:
        return {
            "id": record["id"],
            "chat_id": record.get("chat_id"),
            "filename": record["original_filename"],
            "content_type": record.get("content_type"),
            "size_bytes": record["size_bytes"],
            "storage_path": record["storage_path"],
            "extracted_text_path": record["extracted_text_path"],
            "metadata": record["metadata"],
        }
