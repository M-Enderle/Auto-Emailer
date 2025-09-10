from pathlib import Path

# Directories used by the application
TEMPLATES_DIR = "emailer/templates"
STATIC_DIR = "emailer/static"
TINYMCE_DIR = "tinymce-dist"

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

EXCEL_DIR = Path("excel_uploads")
EXCEL_DIR.mkdir(exist_ok=True)

JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True)


