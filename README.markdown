# Financial Data Analysis & Interactive Dashboard

## Project Overview

This project provides an end-to-end solution for scraping, extracting, and analyzing financial data from quarterly and annual reports of companies listed on the Colombo Stock Exchange (CSE), specifically DIPD.N0000 and REXP.N0000. The system includes:

- **Backend Pipeline**: Python scripts for scraping PDFs, extracting financial metrics, and creating a clean dataset.
- **Frontend Dashboard**: A React.js-based interface for visualizing trends and key performance indicators (KPIs).
- **Chatbot**: An AI-powered interface using the Google Gemini API for natural language queries on financial data.

The pipeline processes PDF reports, extracts metrics like Revenue, Gross Profit, and Net Income, and presents them through an interactive dashboard with toggles for quarterly/annual views and cross-company comparisons.

## Prerequisites

### Software Requirements

- **Python 3.8+**: For running the backend scripts.
- **Node.js 18+**: For running the React frontend and Express backend.
- **Google Chrome**: Required for Playwright (used in scraping).

### Python Dependencies

Install via `pip`:

```bash
pip install pandas pdfplumber aiohttp aiofiles playwright tqdm
```

Install Playwright browsers:

```bash
playwright install
```

### Node.js Dependencies

Install via `npm`:

```bash
npm install react react-dom react-router-dom recharts papaparse react-icons @google/generative-ai express axios
```

### Additional Setup

- **Google Gemini API Key**: Required for the chatbot. Set as an environment variable (`GEMINI_API_KEY`) in the backend.
- **CSE Website Access**: Ensure `https://www.cse.lk` is accessible for scraping.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd financial-data-analysis
   ```

2. **Backend Setup**:

   - Install Python dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     (Create `requirements.txt` with the above Python dependencies if not provided.)
   - Install Playwright browsers:
     ```bash
     playwright install
     ```

3. **Frontend Setup**:

   - Navigate to the frontend directory (if separate, e.g., `frontend/`):
     ```bash
     cd frontend
     npm install
     ```

4. **Backend Server Setup**:

   - Navigate to the backend directory (if separate, e.g., `backend/`):
     ```bash
     cd backend
     npm install
     ```
   - Set the Gemini API key:
     ```bash
     export GEMINI_API_KEY=<your-api-key>  # On Windows, use `set` instead of `export`
     ```

5. **Directory Structure**:
   Ensure the following structure exists:

   ```
   CSE-FINA-...
   ├── backend/
   │   ├── node_modules/           # Node.js dependencies for backend
   │   ├── .env                    # Environment variables (e.g., GEMINI_API_KEY)
   │   ├── Dockerfile              # Docker configuration file
   │   ├── package-lock.json       # Lock file for npm dependencies
   │   ├── package.json            # Node.js package configuration
   |   ├── server.js               # backend of the Chat bot
   |   ├── scripts/
   |   │   ├── dataset.py              # Script to create clean dataset
   |   │   ├── extractor.py            # Script to extract metrics from PDFs
   |   │   ├── pdfselector.py          # Script to select top PDFs
   |   │   └── scraper.py              # Script to scrape PDFs from CSE
   ├── ├── data/
   │       ├── processed/
   │       │   ├── clean_dataset.csv   # Cleaned dataset for dashboard
   │       │   ├── financial_data.csv  # Raw extracted financial data
   │       ├── raw_files/              # Directory for selected raw PDFs
   |   ├── downloads/                  # Temporary storage for scraped PDFs
   |
   ├── frontend/dashboard/
   │   │   ├── node_modules/       # Node.js dependencies for dashboard
   │   ├── public/                 # Static files for React app
   │   │   ├──clean_dataset.csv   # Cleaned dataset for dashboard
   │   ├── src/                    # Source files for React app
   │   │   ├── App.jsx             # Main React component
   │   │   ├── chatBot.css         # Styles for chatbot
   │   │   ├── chatBot.jsx         # Chatbot component
   │   │   ├── dashboard.css       # Styles for dashboard
   │   │   ├── dashboard.jsx       # Dashboard component
   │   │   ├── main.jsx            # React app entry point
   │   │   ├── rout.jsx            # Routing configuration
   │   │   ├── trendDash.css       # Styles for trend dashboard
   │   │   ├── trendDash.jsx       # Trend comparison dashboard
   │   │   └── gitignore           # Git ignore file (if in src)
   │   ├── .eslintrc.config.js     # ESLint configuration
   │   ├── index.html              # HTML entry point (duplicate check)
   │   ├── package-lock.json       # Lock file for npm dependencies
   │   ├── package.json            # Node.js package configuration

   ├── .env                        # Environment variables (root level)
   ├── Dockerfile                  # Docker configuration (root level)
   ├── package-lock.json           # Lock file for npm dependencies (root level)
   ├── package.json                # Node.js package configuration (root level)
   └── README.md                   # Project documentation
   ```

## Usage

### 1. Data Scraping

Run the scraper to download PDFs from the CSE website:

```bash
python scripts/scraper.py
```

- Downloads PDFs for DIPD.N0000 and REXP.N0000 to `data/downloads/`.
- Configurable years in `TARGET_YEARS` (default: 2022–2025).

### 2. PDF Selection

Filter and move the top 14 PDFs per company:

```bash
python scripts/pdfselector.py
```

- Moves selected PDFs to `data/raw_files/` with standardized naming.

### 3. Data Extraction

Extract financial metrics from PDFs:

```bash
python scripts/extractor.py
```

- Outputs `data/processed/financial_data.csv` with extracted metrics.
- Note: OCR is disabled by default (`USE_OCR = False`). Enable if needed for scanned PDFs.

### 4. Dataset Creation

Normalize data into a clean CSV:

```bash
python scripts/dataset.py
```

- Outputs `data/processed/clean_dataset.csv` for dashboard consumption.

### 5. Running the Dashboard

Start the React frontend:

```bash
cd frontend
npm start
```

- Access at `http://localhost:3000`.
- Features:
  - Company selection dropdown.
  - Quarterly/annual view toggle.
  - KPI cards for latest quarter metrics.
  - Line/bar charts for trends.
  - Navigation to trend comparison page (`/trend`).

### 6. Running the Chatbot Backend

Start the Node.js server:

```bash
cd backend
node server.js
```

- Serves at `http://localhost:3001`.
- Handles chatbot queries via the `/ask` endpoint.

### 7. Compiling the Report

- Upload `report.tex` and any images (e.g., `dashboard_screenshot.png`) to Overleaf.
- Compile using PDFLaTeX to generate the final report PDF.

## Deliverables

- **Final Report**: `report.tex` (LaTeX document with project details).
- **Source Code**: Python scripts, React frontend, and Node.js backend.
- **Dataset**: `data/processed/clean_dataset.csv`.
- **Screenshots**: Dashboard screenshots (upload to Overleaf or include in `figures/`).
- **Screen Recording**: Video demonstrating the full pipeline (scraping to dashboard).

## Notes

- **Data Limitations**: Some PDFs may fail extraction due to non-standard layouts. Check logs in `extractor.py` output for errors.
- **Chatbot Scope**: Limited to `clean_dataset.csv` context. Complex queries may require refinement.
- **Scalability**: To add more companies, update `SYMBOLS` in `scraper.py` and `pdfselector.py`, and define new regex patterns in `extractor.py` if needed.
- **Environment**: Ensure stable internet for scraping and API calls. Proxy settings may be required for CSE access in restricted networks.

## Troubleshooting

- **Scraping Errors**: Verify CSE website accessibility and Playwright browser installation.
- **Extraction Failures**: Check PDF readability in `data/raw_files/`. Enable OCR in `extractor.py` for scanned PDFs.
- **Dashboard Issues**: Ensure `clean_dataset.csv` is in the correct path (`/data/` relative to the frontend).
- **Chatbot Errors**: Confirm the Gemini API key is set and the backend server is running.

For further assistance, contact Kithuni Devma Wickramasinghe.
