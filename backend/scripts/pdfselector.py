# select_move_top14.py
import shutil
from pathlib import Path

BASE_DIR = Path("C:/Users/kithu/Desktop/Job/cse-financial-analysis/backend")
DOWNLOADS_DIR = BASE_DIR / "downloads"
TARGET_DIR = BASE_DIR / "data/raw_files"

SYMBOLS = ["DIPD.N0000", "REXP.N0000"]
TOP_K = 14

def move_top14():
    for symbol in SYMBOLS:
        # subfolder in downloads uses underscore version
        subfolder = symbol.replace(".", "_")
        source_dir = DOWNLOADS_DIR / subfolder

        if not source_dir.exists():
            print(f"⚠️ Source folder not found: {source_dir}")
            continue

        # pick PDFs sorted alphabetically
        files = sorted(source_dir.glob("*.pdf"))
        if not files:
            print(f"⚠️ No PDFs found in {source_dir}")
            continue

        selected = files[:TOP_K]

        # create target folder
        target_dir = TARGET_DIR / symbol
        target_dir.mkdir(parents=True, exist_ok=True)

        # copy & rename
        for i, src in enumerate(selected, start=1):
            dst = target_dir / f"{symbol}_{i:02d}.pdf"
            shutil.copy2(src, dst)
            print(f"✅ {src.name} → {dst}")

if __name__ == "__main__":
    move_top14()
