from django.http import JsonResponse
from .models import Subject, AttendanceDetail
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import json
import time


def scrape_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)
    driver.get('https://mserp.kiet.edu')
    username_field = wait.until(EC.presence_of_element_located((By.ID, "txt_username")))
    password_field = wait.until(EC.presence_of_element_located((By.ID, "txt_password")))
    captcha = wait.until(EC.presence_of_element_located((By.ID, "hdncaptcha")))
    captcha_input = wait.until(EC.presence_of_element_located((By.ID, "txtcaptcha")))
    username_field.send_keys(username)
    password_field.send_keys(password)
    captcha_input.send_keys(captcha.get_attribute("value"))

    wait.until(EC.element_to_be_clickable((By.ID, "btnLogin"))).click()
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "ACADEMIC"))).click()
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Student Related"))).click()
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Student Complete Detail"))).click()
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Attendance Details"))).click()
    table_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-responsive")))
    driver.execute_script("""
        var element = arguments[0];
        element.style.height = 'auto';
        element.style.maxHeight = 'none';
        element.style.overflow = 'visible';
        element.style.position = 'static';
    """, table_div)
    
    table = wait.until(EC.presence_of_element_located((By.ID, "divAttendanceDetails")))
    driver.execute_script("arguments[0].scrollIntoView(true);", table)
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    total_subjects = len(rows)
    print(total_subjects)
    
    for i in range(total_subjects):
        table = wait.until(EC.presence_of_element_located((By.ID, "divAttendanceDetails")))
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        current_row = rows[i]
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", current_row)
        cells = current_row.find_elements(By.TAG_NAME, "td")
        code = cells[0].text
        name = cells[1].text
        total_classes = cells[3].text
        total_present = cells[4].text
        percentage = cells[5].text
        subject = Subject.objects.create(
            code=code,
            name=name,
            total_classes=total_classes,
            total_present=total_present,
            attendance_percentage=percentage
        )
        detail_link = current_row.find_element(By.CSS_SELECTOR, "td:first-child a")
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", detail_link)
        driver.execute_script("arguments[0].click();", detail_link)
        modal = wait.until(EC.visibility_of_element_located((By.ID, "myModalCourse")))
        modal_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#myModalCourse table.table")))
        detail_rows = modal_table.find_elements(By.CSS_SELECTOR, "tr:not(:first-child)")
        for detail_row in detail_rows:
            detail_cells = detail_row.find_elements(By.TAG_NAME, "td")  
            if len(detail_cells) >= 4:
                date_text = detail_cells[1].text
                if date_text:
                    AttendanceDetail.objects.create(
                        subject=subject,
                        date=datetime.strptime(date_text, '%d-%m-%Y').date(),
                        slot=detail_cells[2].text,
                        status=detail_cells[3].text
                    )
        close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#myModalCourse .modal-header button")))
        driver.execute_script("arguments[0].click();", close_button)
        wait.until(EC.invisibility_of_element_located((By.ID, "myModalCourse")))
        time.sleep(1)
    driver.quit()
    return JsonResponse({'status': 'success'})

def get_attendance(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    subjects = Subject.objects.all()
    data = [{
        'code': subject.code,
        'name': subject.name,
        'total_classes': subject.total_classes,
        'total_present': subject.total_present,
        'attendance_percentage': subject.attendance_percentage,
        'attendance_details': [{
            'date': detail.date.strftime('%d-%m-%Y'),
            'slot': detail.slot,
            'status': detail.status
        } for detail in AttendanceDetail.objects.filter(subject=subject)]
    } for subject in subjects]

    return JsonResponse({'subjects': data})