from src.ingestion.ocr_engine import OCREngine
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.vlm_extractor import VLMExtractor

try:
    import fitz
    PYMUPDF_RENDER_AVAILABLE = True
except ImportError:
    PYMUPDF_RENDER_AVAILABLE = False


class OCRService:
    def __init__(self):
        self.ocr = OCREngine()
        self.pdf = PDFParser()
        self.vlm = VLMExtractor()

    def extract_text(self, file_path: str, is_image: bool = False) -> str:
        if is_image:
            return self.ocr.perform_ocr(file_path)
        text = self.pdf.extract_text(file_path)
        if self._looks_like_scanned_pdf(text):
            fallback_text = self.extract_scanned_pdf_text(file_path)
            if fallback_text:
                return fallback_text
        return text

    def extract_scanned_pdf_text(self, file_path: str) -> str:
        if not PYMUPDF_RENDER_AVAILABLE:
            return self.ocr.perform_ocr(file_path)

        text_lines = []
        doc = fitz.open(file_path)
        try:
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image_path = f"{file_path}.page-{page_index + 1}.png"
                pixmap.save(image_path)
                try:
                    text_lines.append(self.ocr.perform_ocr(image_path))
                finally:
                    import os

                    if os.path.exists(image_path):
                        os.remove(image_path)
        finally:
            doc.close()

        return "\n".join(line for line in text_lines if line).strip()

    def extract_layout_metadata(self, file_path: str, is_image: bool = False) -> dict:
        if is_image:
            return self.vlm.extract_visual_elements(file_path)

        metadata = {
            "document_type": "PDF Medical Report",
            "has_tables": False,
            "pages": 0,
            "layout_blocks": [],
            "ocr_fallback_used": False,
        }
        if not PYMUPDF_RENDER_AVAILABLE:
            metadata["parser"] = "pdf_text_fallback"
            return metadata

        try:
            doc = fitz.open(file_path)
        except Exception:
            metadata["parser"] = "pdf_layout_unavailable"
            metadata["ocr_fallback_used"] = True
            return metadata

        try:
            metadata["pages"] = len(doc)
            blocks = []
            for page_index in range(len(doc)):
                page = doc.load_page(page_index)
                page_blocks = page.get_text("blocks")
                for block in page_blocks[:20]:
                    text = block[4].strip() if len(block) > 4 and block[4] else ""
                    if not text:
                        continue
                    blocks.append(
                        {
                            "page": page_index + 1,
                            "bbox": [round(float(value), 2) for value in block[:4]],
                            "text_preview": text[:180],
                        }
                    )
                    if "|" in text or "\t" in text or self._looks_tabular(text):
                        metadata["has_tables"] = True
            metadata["layout_blocks"] = blocks[:80]
        finally:
            doc.close()

        return metadata

    def _looks_like_scanned_pdf(self, text: str) -> bool:
        normalized = (text or "").strip()
        if not normalized:
            return True
        return len(normalized) < 40

    def _looks_tabular(self, text: str) -> bool:
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) < 2:
            return False
        numeric_lines = sum(any(char.isdigit() for char in line) for line in lines)
        return numeric_lines >= 2
