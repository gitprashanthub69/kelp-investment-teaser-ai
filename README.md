# Kelp - AI-Powered Investment Teaser Generator

**Kelp** is an intelligent platform that transforms raw company documents (PDFs) into professional, investor-ready PowerPoint presentations in minutes. Designed for M&A advisors, investment bankers, and PE/VC professionals.

---

## 🎯 What is Kelp?

Kelp automates the creation of **investment teasers** — the confidential marketing documents used to attract potential buyers or investors for a company. Instead of spending hours manually creating these presentations, Kelp uses AI to:

1. **Extract** key information from uploaded PDF documents
2. **Analyze** the business model, financials, and market position
3. **Generate** a professional 4-slide PowerPoint presentation
4. **Provide** citations and data sources for verification

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **AI Document Analysis** | Extracts company info, customers, assets, certifications from PDFs |
| **Automatic PPT Generation** | Creates professional investment teasers with consistent branding |
| **Strict Data Accuracy** | Shows "NA" for missing data — never fabricates numbers |
| **Multi-User Support** | Each user manages their own projects/deals |
| **Local Execution** | Runs entirely on your machine — no cloud dependency |
| **Citation Reports** | Generates PDF with sources for all extracted data |

---

## 📊 Generated PPT Structure

The AI generates a **4-slide investment teaser**:

| Slide | Title | Content |
|-------|-------|---------|
| **1** | Title Slide | Project codename, sector badge, confidentiality notice |
| **2** | Business Overview | Company description, customers, assets, certifications, product portfolio, revenue split |
| **3** | Financial Performance | Revenue/EBITDA trends, key metrics, global presence, export markets |
| **4** | Investment Highlights | 6 key investment reasons, "Why Invest?" summary |

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | React 18 + Vite + TailwindCSS |
| **Backend** | Python FastAPI |
| **Database** | SQLite (local) / PostgreSQL (production) |
| **AI Engine** | Google Gemini / OpenAI GPT-4 |
| **PDF Processing** | PyMuPDF, pdfplumber |
| **PPT Generation** | python-pptx |
| **Task Queue** | Celery (Redis in production, in-memory locally) |

---

## 📋 Prerequisites

Ensure these are installed on your Windows machine:

| Software | Version | Download |
|----------|---------|----------|
| **Python** | 3.10 or higher | [python.org/downloads](https://python.org/downloads) |
| **Node.js** | 18 or higher | [nodejs.org](https://nodejs.org) |

> **Tip**: During Python installation, check "Add Python to PATH".

---

## 🚀 Quick Start (3 Steps)

### Step 1: Download
Download and extract the `kelp_project` folder to any location.

### Step 2: Start
Double-click **`start_local.bat`** in the `kelp_project` folder.

> First run takes 2-3 minutes to install dependencies. Subsequent runs are instant.

### Step 3: Open
Once you see "Application is starting!", open your browser to:
- **Application**: [http://localhost:5173](http://localhost:5173)

---

## 📱 How to Use

### 1️⃣ Create Account
1. Go to [http://localhost:5173/signup](http://localhost:5173/signup)
2. Enter any email and password
3. Click **Sign Up**

### 2️⃣ Login
1. Go to [http://localhost:5173/login](http://localhost:5173/login)
2. Enter your credentials
3. Click **Sign In**

### 3️⃣ Create a New Deal
1. Click **"+ New Deal"** button (top right corner)
2. Enter a project name (e.g., "Project Titan", "ABC Corp Deal")
3. Click **"Create Workspace"**

### 4️⃣ Upload Documents
1. Find your project card on the dashboard
2. Click **"Upload"** button
3. Select your PDF file (company profile, financial statements, etc.)
4. Wait for upload confirmation

### 5️⃣ Generate Teaser
1. Click **"Generate"** button on the project card
2. Status changes: `Pending` → `Processing` → `Completed`
3. Processing typically takes 30-60 seconds

### 6️⃣ Download Results
Once completed, you'll see two download buttons:
- **Download Teaser (PPT)** — Your investment presentation
- **Download Citations (PDF)** — Data sources and references

---

## 📁 Project Structure

```
kelp_project/
│
├── start_local.bat          # One-click startup script
├── README.md                 # This file
│
├── backend/                  # Python FastAPI server
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   ├── core/             # Configuration, security
│   │   ├── db/               # Database models
│   │   ├── services/         # Business logic
│   │   │   ├── intelligence.py    # AI narrative generation
│   │   │   ├── ppt_generator.py   # PowerPoint creation
│   │   │   ├── parser.py          # PDF text extraction
│   │   │   └── s3_service.py      # File storage
│   │   └── schemas/          # Data validation
│   ├── data/                 # Local file storage
│   └── requirements.txt      # Python dependencies
│
└── frontend/
    └── frontend/             # React application
        ├── src/
        │   ├── pages/        # Dashboard, Auth, Landing
        │   ├── components/   # Reusable UI components
        │   └── App.jsx       # Main router
        └── package.json      # Node dependencies
```

---

## 🔧 Configuration

### Environment Variables (Optional)
Located in `backend/.env`:

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key for AI generation |
| `OPENAI_API_KEY` | OpenAI API key (alternative AI) |
| `USE_LOCAL_STORAGE` | Set to `True` for local file storage |

> **Note**: The app works without API keys using fallback templates, but AI-generated content will be more generic.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| **Blank dashboard** | Hard refresh with `Ctrl + Shift + R` |
| **Login error** | Check if backend terminal shows errors |
| **PPT not downloading** | Ensure generation completed (status = "Completed") |
| **Port 5173 in use** | Close other apps using that port |
| **"Python not found"** | Reinstall Python with "Add to PATH" checked |
| **Slow first start** | Normal — dependencies are being installed |

---


---

## 📄 License

Proprietary. All rights reserved.

---

*Kelp — Transforming documents into deal-ready presentations.*
