import asyncio
from playwright.async_api import async_playwright

# 1. Import your async OCR function from agents.py
from agent_service.py import extract_document_details


async def main():
    # Path to the image document you want to extract data from
    document_image_path = "sample_document.png"  

    # 2. Extract data from the image using your Gemini OCR function
    print("Extracting text from image...")
    extracted_data = await extract_document_details(document_image_path)
    
    print("\nExtracted Information:")
    print(f"Name: {extracted_data.applicant_name}")
    print(f"Income: {extracted_data.annual_income}")
    print(f"State: {extracted_data.state}")
    print(f"Category: {extracted_data.category}\n")

    # 3. Launch Playwright browser
    async with async_playwright() as p:
        print("Launching browser...")
        # Set headless=False so you can see the browser open and type automatically
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 4. Navigate to your target web form
        print("Opening target website...")
        await page.goto("https://example.com/application-form")  # Replace with your actual URL

        # 5. Fill out form fields using extracted details
        # Replace the CSS selectors ('input[name="..."]') with the actual fields on your target website
        
        if extracted_data.applicant_name:
            print("Filling Name...")
            await page.fill('input[name="applicant_name"]', str(extracted_data.applicant_name))

        if extracted_data.annual_income:
            print("Filling Income...")
            await page.fill('input[name="annual_income"]', str(extracted_data.annual_income))

        if extracted_data.state:
            print("Selecting State...")
            # Use fill for standard text input, or select_option if it's a dropdown menu
            await page.fill('input[name="state"]', str(extracted_data.state))

        if extracted_data.category:
            print("Filling Category...")
            await page.fill('input[name="category"]', str(extracted_data.category))

        print("Form automation complete!")

        # Keep browser visible for 5 seconds before closing
        await page.wait_for_timeout(5000)
        await browser.close()


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())