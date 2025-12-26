import io
import re
import time
import rarfile
import asyncio
import logging
from bs4 import BeautifulSoup
from tools.db import DBInitializer, DBSessionManager
from tools.db.models import Courses, Metadata

logger = logging.getLogger("tku-aila.acad.processing")

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
    
    def generate_database(self, html_bytes_list: list[bytes], metadata: dict):
        logger.info("Starting database generation...")
        start_time = time.time()
        DBInitializer().init_db()
        session_manager = DBSessionManager()
        
        with session_manager.get_session() as session:
            for html_bytes in html_bytes_list:
                courses = self.html_parser(html_bytes)
                
                for course in courses:
                    new_course = Courses(
                        department=course['department'],
                        grade=int(course['grade']) if course['grade'].isdigit() else None,
                        serial_no=course['serial_no'],
                        course_id=course['course_id'],
                        specialty=course['specialty'],
                        semester=int(course['semester']) if course['semester'].isdigit() else None,
                        class_type=course['class_type'],
                        group_type=course['group_type'],
                        required_elective_type=course['required_elective_type'],
                        credits=float(course['credits']) if hasattr(course, 'credits') else None, # 簡化檢查
                        course_name=course['course_name'],
                        people_limit=int(course['people_limit']) if course['people_limit'].isdigit() else None,
                        instructor=course['instructor'],
                        time_place=course['time_place']
                    )
                    session.add(new_course)
                
                session.commit()
            
            existing_metadata = session.get(Metadata, 1)
            if not existing_metadata:
                new_metadata = Metadata(id=1, year=metadata['year'], semester=metadata['semester'])
                session.add(new_metadata)
            else:
                existing_metadata.last_updated = int(time.time())
            session.commit()

        logger.info("Database generation completed. Time: %.2f seconds", time.time() - start_time)
