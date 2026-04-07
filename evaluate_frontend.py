import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        logs = []
        page.on("console", lambda msg: logs.append(f"CONSOLE: {msg.type} {msg.text}"))
        page.on("pageerror", lambda exc: logs.append(f"ERROR: {exc}"))
        page.on("requestfailed", lambda req: logs.append(f"REQUEST FAILED: {req.url} {req.failure}"))
        
        await page.goto("https://yajd19-openenv-incident.hf.space")
        await page.wait_for_timeout(3000)
        
        print("Clicking Load Scenario button...")
        try:
            await page.get_by_text("Load Scenario").click()
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Failed to click button: {e}")
            
        print("--- CAPTURED LOGS ---")
        for log in logs:
            print(log)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
