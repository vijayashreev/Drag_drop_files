import os
import base64
import mimetypes

def extract_base64_image(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("image/"):
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"
    return None


    return loader.load()

def load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".pdf"]:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
    elif ext in [".docx", ".doc"]:
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        loader = UnstructuredWordDocumentLoader(file_path)
    elif ext in [".pptx"]:
        from langchain_community.document_loaders import UnstructuredPowerPointLoader
        loader = UnstructuredPowerPointLoader(file_path)
    elif ext in [".xlsx", ".xls"]:
        from langchain_community.document_loaders import UnstructuredExcelLoader
        loader = UnstructuredExcelLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return loader.load()


