import re
import urllib3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ACADDownloader:
    ACAD_URL = "https://esquery.tku.edu.tw/acad/"
    def __init__(self,):
        self.__session = requests.Session()
        self.__session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
    def __get_metadata_from_url(self, url: str) -> dict:
        pattern = r"upload/(\d{3})(\d{1})CLASS\.RAR"
        match = re.search(pattern, url)
        
        if match:
            year = match.group(1)
            semester = match.group(2)
            return {
                "year": year,
                "semester": semester
            }
        else:
            raise ValueError("URL does not match expected pattern for metadata extraction.")
        
    def __get_download_url(self):
        response = self.__session.get(self.ACAD_URL, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        frame_tag = soup.find('frame', attrs={'name': 'main'})
        
        frame_relative_url = frame_tag.get('src')
        frame_url = urljoin(self.ACAD_URL, frame_relative_url)
        frame_response = self.__session.get(frame_url, verify=False)
        frame_soup = BeautifulSoup(frame_response.text, "html.parser")
        
        target_link = frame_soup.find("a", string="下載離線閱讀程式")
        onclick_text = target_link.get('onclick')
        
        match = re.search(r"window\.open\s*\(\s*['\"]([^'\"]+)['\"]", onclick_text)
        popup_relative_url = match.group(1)
        popup_url = urljoin(frame_url, popup_relative_url)
        
        popup_response = self.__session.get(popup_url, verify=False)
        popup_soup = BeautifulSoup(popup_response.text, "html.parser")
        
        download_tag = popup_soup.find("a")
        if download_tag:
            download_href = download_tag['href']
            final_download_link = urljoin(popup_url, download_href)
            return final_download_link
            
    def download_file(self) -> dict:
        downloader_url = self.__get_download_url()
        
        if not downloader_url:
            raise Exception("Failed to retrieve download URL.")
            
        with self.__session.get(downloader_url, stream=True, verify=False) as r:
            r.raise_for_status()
            if r.content:
                return {
                    "file_bytes": r.content,
                    "metadata": self.__get_metadata_from_url(downloader_url)
                }
    
    def has_update(self, year: int, semester: int) -> bool:
        downloader_url = self.__get_download_url()
        metadata = self.__get_metadata_from_url(downloader_url)
        return (metadata['year'] != year) or (metadata['semester'] != semester)
