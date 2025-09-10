from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import uuid
from pathlib import Path
import asyncio

from emailer.schemas import SendMailRequest, BulkJobRequest
from emailer.services_mail import resolve_account, build_message, send_via_smtp
from emailer.services_jobs import JobManager, load_recipients_from_excel
from emailer.utils.settings import get_mail_settings
from emailer.paths import UPLOAD_DIR, EXCEL_DIR


templates = Jinja2Templates(directory="emailer/templates")
router = APIRouter()


@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    path = UPLOAD_DIR / f"{uuid.uuid4()}.{ext}"
    path.write_bytes(await file.read())
    return {"location": f"/uploads/{path.name}"}


@router.post("/upload-recipients")
async def upload_recipients(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only Excel .xlsx/.xlsm files allowed")
    dest = EXCEL_DIR / f"{uuid.uuid4()}_{file.filename}"
    dest.write_bytes(await file.read())
    return {"file_id": dest.name}


@router.post("/sendmail")
async def send_mail(payload: SendMailRequest):
    account = resolve_account(payload.from_address)
    msg = build_message(account, payload)
    try:
        await asyncio.to_thread(send_via_smtp, account, msg)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {exc}")
    return {"status": "sent"}


job_manager = JobManager()
job_manager.load_existing()


@router.post("/start-bulk")
async def start_bulk(req: BulkJobRequest):
    recipients = load_recipients_from_excel(req.file_id)
    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients found in file")
    job_id = await job_manager.add_job(recipients, req)
    return {"job_id": job_id, "total": len(recipients)}


@router.get("/jobs")
async def jobs():
    return {"jobs": job_manager.list_jobs()}


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    ok = job_manager.cancel_job(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "cancelled"}


@router.get("/mail-accounts")
async def list_mail_accounts():
    settings = get_mail_settings()
    accounts = []
    if settings.accounts:
        accounts.extend([{"key": key, "address": acc.address} for key, acc in settings.accounts.items()])
    if settings.schreiber:
        accounts.append({"key": "schreiber", "address": settings.schreiber.address})
    if not accounts:
        raise HTTPException(status_code=500, detail="No mail account configured")
    seen = set()
    unique = []
    for item in accounts:
        if item["address"] not in seen:
            seen.add(item["address"])
            unique.append(item)
    return {"accounts": unique}


