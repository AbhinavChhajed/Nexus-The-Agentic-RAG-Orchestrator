"""
Universal file loader that routes files to specialised readers
based on their extension and MIME type.
"""

import base64
import mimetypes
import os

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class UniversalLoader:
    """Traffic controller: reads any supported file and returns its text content."""

    # Extensions treated as plain-text / code
    CODE_EXTENSIONS: set[str] = {
        ".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c",
        ".h", ".sql", ".md", ".json", ".xml", ".yaml", ".yml", ".txt",
    }

    LANG_MAP: dict[str, str] = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".html": "html", ".sql": "sql", ".css": "css",
    }

    def __init__(self, llm: ChatGoogleGenerativeAI) -> None:
        self.llm = llm

    # ── Public entry point ───────────────────────────────────────────────

    def process_file(self, file_path: str) -> str:
        """Route a file to the correct reader and return its text content."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        mime_type, _ = mimetypes.guess_type(file_path)

        if ext in self.CODE_EXTENSIONS:
            return self._process_code(file_path, ext)
        if mime_type and "pdf" in mime_type:
            return self._process_pdf(file_path)
        if mime_type and "csv" in mime_type:
            return self._process_csv(file_path)
        if mime_type and "image" in mime_type:
            return self._process_image(file_path)

        return f"Unsupported file type: {mime_type or ext}"

    # ── Private readers ──────────────────────────────────────────────────

    def _process_code(self, file_path: str, ext: str) -> str:
        """Read code / text files and wrap in a markdown code fence."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            language = self.LANG_MAP.get(ext, "")
            return f"```{language}\n{content}\n```"
        except Exception as e:
            return f"Error reading code file: {e}"

    @staticmethod
    def _process_pdf(file_path: str) -> str:
        """Extract text from all pages of a PDF."""
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        return "\n".join(page.page_content for page in pages)

    @staticmethod
    def _process_csv(file_path: str) -> str:
        """Convert a CSV to a markdown table."""
        df = pd.read_csv(file_path)
        return df.to_markdown(index=False)

    def _process_image(self, file_path: str) -> str:
        """Use the LLM's vision capability to describe an image."""
        try:
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            prompt = HumanMessage(content=[
                {"type": "text", "text": "Describe the following image in detail."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
            ])
            response = self.llm.invoke([prompt])
            return response.content
        except Exception as e:
            return f"Error processing image: {e}"
