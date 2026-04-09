import time
from playwright.sync_api import sync_playwright

def test_crawl_dut():
    print("Bắt đầu khởi động Playwright...")
    with sync_playwright() as p:
        # Khởi chạy trình duyệt có giao diện (headless=False) để mình nhìn thấy nó làm gì
        browser = p.chromium.launch(headless=False, slow_mo=500) 
        page = browser.new_page()

        print("Đang truy cập Hệ thống tín chỉ DUT...")
        page.goto("http://sv.dut.udn.vn/G_ListCTDT.aspx")

        # 1. Tìm và chọn "K. Công nghệ Thông tin" trong dropdown "Thuộc khoa"
        print("Đang lọc Khoa Công nghệ Thông tin...")
        # Lấy tất cả các thẻ select, tìm thẻ có chứa chữ "Khoa", sau đó chọn option IT
        page.locator("select").nth(1).select_option(label="K. Công nghệ Thông tin")

        # 2. Đợi trang web load lại dữ liệu (PostBack của ASP.NET)
        print("Đang đợi server trả về danh sách...")
        time.sleep(3) # Tạm dừng 3 giây cho chắc ăn

        # 3. Tìm các hàng (tr) có chứa chữ "K2025"
        print("Đang tìm các chương trình K2025...")
        k2025_rows = page.locator("tr", has_text="K2025")
        
        count = k2025_rows.count()
        print(f"Đã tìm thấy {count} chương trình của năm 2025!")

        if count > 0:
            # 4. Lấy hàng đầu tiên (Công nghệ Thông tin K2025 Đặc thù _ Kỹ sư)
            first_row = k2025_rows.nth(0)
            
            # 5. Tìm cái icon Kính Lúp trong hàng đó và Click vào
            print("Đang click thử vào Kính Lúp của hàng đầu tiên...")
            
            # Thường icon kính lúp sẽ có thẻ <img> hoặc <input type="image">. 
            # Mình dùng CSS Selector trỏ thẳng vào thẻ ảnh nằm trong ô cuối cùng
            first_row.locator("img, input[type='image']").click()
            
            print("Hãy quan sát trên màn hình xem điều gì xảy ra tiếp theo!")
            # Dừng 10 giây để bro kịp nhìn xem nó mở ra Popup hay Tab mới
            time.sleep(10) 
        else:
            print("Không tìm thấy chữ K2025, có thể do mạng lag trang chưa load kịp.")

        browser.close()

if __name__ == "__main__":
    test_crawl_dut()