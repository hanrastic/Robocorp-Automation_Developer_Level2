from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Main function to order robots from RobotSpareBin Industries Inc.
    It navigates to the robot order website, downloads and processes the orders from a CSV file,
    and archives all the receipts after ordering.
    """
    # Configure browser settings
    browser.configure(
        #slowmo=100,
    )

    # Navigate to the robot order page
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

    # Download the orders CSV file
    http = HTTP()
    http.download(url='https://robotsparebinindustries.com/orders.csv', overwrite=True)

    # Read orders from the downloaded CSV file
    orders = Tables().read_table_from_csv('orders.csv')

    # Process each order
    for order in orders:
        place_order(order)

    # Archive all receipts after ordering
    archive_receipts()

def close_annoying_modal():
    """
    Closes the modal window if it appears on the robot order page.
    """
    page = browser.page()
    page.click("button:text('Ok')")

def place_order(order):
    """
    Handles the process of placing a single robot order.
    Includes filling the form, taking screenshots, submitting the order,
    storing the receipt as a PDF, embedding the screenshot into the PDF, and navigating back to order page.
    """
    order_number = order['Order number']
    close_annoying_modal()
    fill_the_form(order)
    screenshot = screenshot_robot(order_number)
    submit_order()
    receipt = store_receipt_as_pdf(order_number)
    embed_screenshot_to_receipt(screenshot, receipt)
    return_to_order_page()

def fill_the_form(order):
    """
    Fills out the form on the robot order page with the details from the order.
    """
    page = browser.page()

    # Fill in the robot configuration
    page.select_option('#head', order['Head'])
    page.click('#id-body-' + order['Body'])
    page.fill('[placeholder="Enter the part number for the legs"]', order['Legs'])
    page.fill('#address', order['Address'])

def screenshot_robot(order_number):
    """
    Takes a screenshot of the configured robot preview.
    """
    page = browser.page()
    page.click('#preview')
    screenshot_path = f'output/screenshots/order_{order_number}.png'
    page.screenshot(path=screenshot_path)
    return screenshot_path

def submit_order():
    """
    Submits the robot order and checks for any errors.
    """
    page = browser.page()
    order_ok = False
    while not order_ok:
        page.click('#order')
        order_ok = page.query_selector('.alert-danger') is None

def store_receipt_as_pdf(order_number):
    """
    Converts the order receipt HTML to a PDF file.
    """
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()
    
    pdf = PDF()
    pdf_path = f'output/receipts/order_{order_number}.pdf'
    pdf.html_to_pdf(receipt, pdf_path)
    return pdf_path

def return_to_order_page():
    """
    Navigates back to the robot order page to place a new order.
    """
    page = browser.page()
    page.click('#order-another')

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """
    Embeds a screenshot into the existing PDF receipt.
    """
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    """
    Archives all receipt PDFs into a single ZIP file and cleans up the output directory.
    """
    archive = Archive()
    archive.archive_folder_with_zip(folder='output/receipts/', archive_name='output/orders.zip')
