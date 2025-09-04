import asyncio
import re
from pathlib import Path

import aiohttp
import aiofiles
from playwright.async_api import async_playwright


TARGET_YEARS = {"2025", "2024", "2023", "2022"}  
OUT_DIR = Path("downloads/downloads")
OUT_DIR.mkdir(exist_ok=True)


async def download_pdf(url: str, filename: Path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())
                print(f"✅ Downloaded {filename}")
            else:
                print(f"❌ Failed to download {url} (status {resp.status})")


async def open_cse_company(symbol: str = "DIPD.N0000", headless: bool = True):
    url = f"https://www.cse.lk/pages/company-profile/company-profile.component.html?symbol={symbol}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url, timeout=60_000, wait_until="domcontentloaded")

        # Click tabs
        await page.get_by_role("link", name="Financials", exact=True).click()
        await page.get_by_role("link", name="Quarterly Reports", exact=True).click()
        await page.wait_for_load_state("networkidle")

        # Find links that contain the PDF icon
        pdf_links = page.locator("a:has(i.fa.fa-file-pdf-o)")
        count = await pdf_links.count()
        print(f"📄 Found {count} PDF link(s) with icon under Quarterly Reports")

        downloads_for_symbol = 0
        company_dir = OUT_DIR / symbol.replace(".", "_")
        company_dir.mkdir(parents=True, exist_ok=True)

        for i in range(count):
            link = pdf_links.nth(i)

            # Absolute URL via DOM (resolves relative hrefs)
            abs_url = await link.evaluate("(el) => el.href")

            # Optional: filter by year found in the same table row text
            row_text = await link.evaluate(
                "(el) => (el.closest('tr')?.innerText || el.parentElement?.innerText || '')"
            )
            years_in_text = set(re.findall(r"(20\\d{2})", row_text))
            if TARGET_YEARS and years_in_text and years_in_text.isdisjoint(TARGET_YEARS):
                # Skip if row has a year but not in target set
                continue

            downloads_for_symbol += 1
            # Make a readable filename
            base_name = abs_url.split("/")[-1].split("?")[0] or "report.pdf"
            if not base_name.lower().endswith(".pdf"):
                base_name += ".pdf"
            out_file = company_dir / f"{symbol}_{downloads_for_symbol:02d}_{base_name}"

            await download_pdf(abs_url, out_file)

        print(f"✅ Done {symbol}: downloaded {downloads_for_symbol} file(s).")
        await browser.close()


async def main():
    # Use the two symbols from your assignment
    symbols = ["DIPD.N0000", "REXP.N0000"]
    for s in symbols:
        await open_cse_company(s, headless=True)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import re
from pathlib import Path

import aiohttp
import aiofiles
from playwright.async_api import async_playwright


TARGET_YEARS = {"2025", "2024", "2023", "2022"}  # adjust as you like
OUT_DIR = Path("downloads")
OUT_DIR.mkdir(exist_ok=True)


async def download_pdf(url: str, filename: Path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(await resp.read())
                print(f"✅ Downloaded {filename}")
            else:
                print(f"❌ Failed to download {url} (status {resp.status})")


async def open_cse_company(symbol: str = "DIPD.N0000", headless: bool = False):
    url = f"https://www.cse.lk/pages/company-profile/company-profile.component.html?symbol={symbol}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        await page.goto(url, timeout=60_000, wait_until="domcontentloaded")

        # Click tabs
        await page.get_by_role("link", name="Financials", exact=True).click()
        await page.get_by_role("link", name="Quarterly Reports", exact=True).click()
        await page.wait_for_load_state("networkidle")

        # Find links that contain the PDF icon
        pdf_links = page.locator("a:has(i.fa.fa-file-pdf-o)")
        count = await pdf_links.count()
        print(f"📄 Found {count} PDF link(s) with icon under Quarterly Reports")

        downloads_for_symbol = 0
        company_dir = OUT_DIR / symbol.replace(".", "_")
        company_dir.mkdir(parents=True, exist_ok=True)

        for i in range(count):
            link = pdf_links.nth(i)

            # Absolute URL via DOM (resolves relative hrefs)
            abs_url = await link.evaluate("(el) => el.href")

            #filter by year found in the same table row text
            row_text = await link.evaluate(
                "(el) => (el.closest('tr')?.innerText || el.parentElement?.innerText || '')"
            )
            years_in_text = set(re.findall(r"(20\\d{2})", row_text))
            if TARGET_YEARS and years_in_text and years_in_text.isdisjoint(TARGET_YEARS):
                # Skip if row has a year but not in target set
                continue

            downloads_for_symbol += 1
            # Make a readable filename
            base_name = abs_url.split("/")[-1].split("?")[0] or "report.pdf"
            if not base_name.lower().endswith(".pdf"):
                base_name += ".pdf"
            out_file = company_dir / f"{symbol}_{downloads_for_symbol:02d}_{base_name}"

            await download_pdf(abs_url, out_file)

        print(f"✅ Done {symbol}: downloaded {downloads_for_symbol} file(s).")
        await browser.close()


async def main():
    # Use the two symbols 
    symbols = ["DIPD.N0000", "REXP.N0000"]
    for s in symbols:
        await open_cse_company(s, headless=True)


if __name__ == "__main__":
    asyncio.run(main())
