from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import pdf_to_images
from app.ocr import run_ocr
from app.extractor import extract_fields
from app.validator import validate
import shutil, os, json, traceback

os.makedirs("outputs", exist_ok=True)

app = FastAPI(title="CMS 1500 Extractor")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    temp_path = os.path.join("outputs", f"temp{ext}")

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if ext in [".jpg", ".jpeg", ".png"]:
            image_paths = [temp_path]
        elif ext == ".pdf":
            image_paths = pdf_to_images(temp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        full_text = ""
        for img in image_paths:
            full_text += run_ocr(img) + "\n"

        raw_data = extract_fields(full_text)
        result = validate(raw_data)

        out_path = os.path.join("outputs", f"{file.filename}_result.json")
        with open(out_path, "w") as f:
            json.dump(result.dict(), f, indent=2)

        return result.dict()

    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass