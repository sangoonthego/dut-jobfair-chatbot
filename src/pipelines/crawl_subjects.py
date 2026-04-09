import time
import json
import os
from playwright.sync_api import sync_playwright

# Dam bao thu muc data ton tai
os.makedirs("data", exist_ok=True)

# Muc tieu: Dung ten nganh ban dang can
TARGET_NAME = "Công nghệ Thông tin K2024 Nhật"

def crawl_dut_academic_advisor():
    print(f"Bat dau Robot DUT - Muc tieu: {TARGET_NAME}")
    
    with sync_playwright() as p:
        # headless=False de ban theo doi truc tiep
        browser = p.chromium.launch(headless=False, slow_mo=600) 
        context = browser.new_context(viewport={'width': 1366, 'height': 768})
        page = context.new_page()

        try:
            # Buoc 1: Lay Session
            print("Buoc 1: Truy cap trang chu de thiet lap session...")
            page.goto("https://sv.dut.udn.vn/", wait_until="networkidle")
            time.sleep(2)

            # Buoc 2: Vao trang CTDT
            print("Buoc 2: Chuyen huong sang trang Chuong trinh dao tao...")
            page.goto("https://sv.dut.udn.vn/G_ListCTDT.aspx", wait_until="networkidle")
            
            # Buoc 3: Loc Khoa
            print("Buoc 3: Dang chon Khoa...")
            page.wait_for_selector("select")
            page.locator("select").nth(1).select_option(label="K. Công nghệ Thông tin")
            
            print("Buoc 3.5: Bam nut Du lieu...")
            page.get_by_role("button", name="Dữ liệu").click()
            
            page.wait_for_selector("tr", timeout=20000)
            print(f"Dang tim kiem {TARGET_NAME} trong danh sach...")

            # Buoc 4: Lan chuot tim hang du lieu
            target_locator = page.get_by_text(TARGET_NAME, exact=True)
            found = False
            for i in range(15):
                if target_locator.count() > 0 and target_locator.first.is_visible():
                    print(f"Da thay hang du lieu o lan cuon thu {i}")
                    found = True
                    break
                page.mouse.wheel(0, 1000)
                time.sleep(1)

            if not found:
                print(f"Loi: Khong tim thay {TARGET_NAME}")
                return

            # Khoa muc tieu vao hang (row)
            target_row = page.get_by_role("row").filter(has_text=TARGET_NAME).first
            target_row.scroll_into_view_if_needed()
            
            program_name = target_row.locator("td").nth(3).inner_text().strip()
            print(f"Da khoa muc tieu: {program_name}")

            # BUOC 5: MO KINH LUP (Dung locator quet rong)
            print("Buoc 5: Dang mo bang chi tiet mon hoc...")
            
            # Chien thuat: Tim tat ca icon co hinh kinh lup trong hang do
            # Thuong thi no la input[type="image"] hoac img co src chua chu 'search'
            magnifier = target_row.locator("input[src*='search'], img[src*='search'], input[src*='Search'], img[src*='Search']").first
            
            if magnifier.count() > 0:
                print("Da tim thay bieu tuong kinh lup. Dang bam...")
                magnifier.click(force=True)
            else:
                # Neu van khong thay, thu bam vao phan tu co the click cuoi cung trong hang
                print("Khong tim thay theo ten anh, thu bam vao phan tu cuoi cung cua hang...")
                last_btn = target_row.locator("input, img, a").last
                if last_btn.count() > 0:
                    last_btn.click(force=True)
                else:
                    print("Loi: Khong tim thay bat ky nut bam nao trong hang nay.")
                    page.screenshot(path="debug_magnifier_not_found.png")
                    return
            
            # Buoc 6: Trich xuat du lieu
            print("Buoc 6: Dang rut ruot du lieu mon hoc...")
            time.sleep(5) # Doi popup load hoan toan

            # Lay tat ca hang TR tren trang (bao gom ca trong popup)
            all_rows = page.locator("tr").all()
            courses = []
            
            for row in all_rows:
                try:
                    r_cells = row.locator("td").all()
                    if len(r_cells) >= 6:
                        semester = r_cells[1].inner_text().strip()
                        if semester.isdigit():
                            courses.append({
                                "semester": int(semester),
                                "course_code": r_cells[4].inner_text().strip(),
                                "course_name": r_cells[2].inner_text().strip(),
                                "credits": r_cells[5].inner_text().strip()
                            })
                except:
                    continue

            # Buoc 7: Luu file
            if courses:
                safe_name = TARGET_NAME.replace(" ", "_").replace("/", "_")
                output_file = f"data/curriculum_{safe_name}.json"
                
                final_data = {
                    "program": program_name,
                    "total_courses": len(courses),
                    "courses": courses
                }
                
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=4)
                print(f"THANH CONG: Da lay duoc {len(courses)} mon hoc vao {output_file}")
            else:
                print("Loi: Khong tim thay mon hoc nao trong bang chi tiet.")

        except Exception as e:
            print(f"Loi he thong: {e}")
            page.screenshot(path="debug_error.png")
            print("Da chup anh debug_error.png de ban kiem tra.")
        finally:
            browser.close()

if __name__ == "__main__":
    crawl_dut_academic_advisor()