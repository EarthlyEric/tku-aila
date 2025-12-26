import io
import re
import rarfile
from bs4 import BeautifulSoup

class ACADProcessor:
    def unpack_file(self, file_bytes: bytes) -> list[bytes]:
        extracted_contents = []
        ignore_filenames = ['CLASS/data/INDEX.htm', 'CLASS/data/UPNEW.htm']
    
        with rarfile.RarFile(io.BytesIO(file_bytes)) as rf:
            for member in rf.infolist():
                if member.filename.startswith('CLASS/data') and not member.isdir() and member.filename not in ignore_filenames:
                    
                    with rf.open(member) as extracted_file:
                        extracted_contents.append(extracted_file.read())

        return extracted_contents
    
    def html_parser(self, html_bytes: bytes) -> list[dict]:
        html_content = html_bytes.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html_content, "html.parser")
        
        courses = []
        
        tables = soup.find_all('table')
        target_table = None
        
        for tbl in tables:
            if tbl.find(string=re.compile("系別")) or tbl.find(string=re.compile("上課時間")):
                target_table = tbl
                break
        
        if not target_table:
            return courses
        
        current_dept_info = "Unknown"
    
        rows = target_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
        
            text_content = row.get_text(strip=True)
            
            if "系別(Department)" in text_content:
                if "：" in text_content:
                    current_dept_info = text_content.split("：")[-1].strip()
                continue

            if "開課" in text_content and "序號" in text_content:
                continue
            
            if len(cells) >= 14:
                def get_cell_text(index):
                    if index < len(cells):
                        return cells[index].get_text(" ", strip=True)
                    return ""

                course_name_cell = cells[10]
                course_name_full = course_name_cell.get_text(" ", strip=True)
            
                course_data = {
                    "department": current_dept_info, # 系別
                    "grade": get_cell_text(0),     # 年級
                    "serial_no": get_cell_text(1), # 開課序號
                    "course_id": get_cell_text(2), # 科目編號
                    "specialty": get_cell_text(3), # 專業別
                    "semester": get_cell_text(4),  # 學期序
                    "class_type": get_cell_text(5),     # 班別
                    "group_type": get_cell_text(6),     # 分組別
                    "required_elective_type": get_cell_text(7),      # 必選修 (Required/Elective)
                    "credits": get_cell_text(8),   # 學分數
                    "group_type": get_cell_text(9), # 群別
                    "course_name": course_name_full, # 科目名稱
                    "people_limit": get_cell_text(11),    # 人數設限
                    "instructor": get_cell_text(12), # 授課教師
                    "time_place": get_cell_text(13) if len(cells) > 14 else ","+ get_cell_text(14), # 星期/節次/教室 1
                }
                course_data['serial_no'] = course_data['serial_no'].replace("　", "")
                courses.append(course_data)
        return courses
    
    def generate_database(self, html_bytes_list: list[bytes]):
        pass
    
