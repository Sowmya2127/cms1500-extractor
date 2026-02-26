📄 CMS-1500 Claim Form Extractor

AI-powered web app that extracts structured data from CMS-1500 medical claim forms using OCR and LLM-based field extraction.

Built with FastAPI + Tesseract OCR + PyMuPDF + Groq LLM.

🚀 Features

Upload CMS-1500 forms (PDF, JPG, PNG)

OCR text extraction using Tesseract

AI-based structured field extraction (Groq – LLaMA 3)

Pydantic validation

JSON output saved to outputs/

🏗️ Tech Stack

FastAPI • Uvicorn • Tesseract OCR • Pytesseract • Pillow • PyMuPDF • Groq API • Pydantic • Jinja2 • python-dotenv

⚙️ Setup
1️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Install Tesseract OCR

Download (Windows):
https://github.com/UB-Mannheim/tesseract/wiki

Or install via:

Mac
brew install tesseract

Linux
sudo apt-get install tesseract-ocr

4️⃣ Add Environment Variable

Create .env file:
GROQ_API_KEY=your_api_key_here

5️⃣ Run App

uvicorn app.main:app --reload

Open:
http://127.0.0.1:8000

📤 Output

Returns structured JSON and saves to:

outputs/<filename>_result.json
