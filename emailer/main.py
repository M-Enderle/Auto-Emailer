from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from emailer.paths import STATIC_DIR, TINYMCE_DIR, UPLOAD_DIR
from emailer.routes import router
from emailer.services_mail import validate_mail_credentials


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/tinymce", StaticFiles(directory=TINYMCE_DIR), name="tinymce")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.include_router(router)


@app.on_event("startup")
async def validate_credentials_on_startup():
    results = await _validate_credentials_async()
    # Log to stdout; do not crash startup to allow UI to load
    for addr, status in results.items():
        print(f"SMTP credentials check for {addr}: {status}")


async def _validate_credentials_async():
    # Run sync validation in thread to avoid blocking event loop
    import asyncio
    return await asyncio.to_thread(validate_mail_credentials)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

 
