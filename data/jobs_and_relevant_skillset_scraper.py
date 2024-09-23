from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv

def get_jobs_and_skills(driver):
    jobs_and_skills = []
    # find all job titles under the dropdown "Select a job title"
    # then get the `.autocomplete-list-item` elements from within this job title dropdown
    job_titles_script = """
    var jobDropdown = Array.from(document.querySelectorAll('.select')).find(el => el.textContent.includes('Select a job title'));
    if (!jobDropdown) return [];
    return Array.from(jobDropdown.querySelectorAll('.autocomplete-list-item'))
        .map(e => e.textContent.trim())
        .filter(text => text !== '');
    """
    # retrieve job titles
    job_titles = driver.execute_script(job_titles_script)
    
    for job in job_titles:
        # javascript to select specific job
        select_job_script = f"""
        var jobDropdown = Array.from(document.querySelectorAll('.select')).find(el => el.textContent.includes('Select a job title'));
        if (!jobDropdown) return false;
        var elements = jobDropdown.querySelectorAll('.autocomplete-list-item');
        for (var i = 0; i < elements.length; i++) {{
            if (elements[i].textContent.trim() === '{job}') {{
                elements[i].click();
                return true;
            }}
        }}
        return false;
        """
        job_selected = driver.execute_script(select_job_script)
        
        if not job_selected:
            print(f"Could not select job: {job}")
            continue
        # wait for page to load
        time.sleep(2)
        
        # javascript to retrieve skills for the selected job 
        skills_script = """
        return Array.from(document.querySelectorAll('.list.list--right .skill-name'))
            .map(e => e.textContent.trim())
            .filter(text => text !== '');
        """
        skills = driver.execute_script(skills_script)
        
        jobs_and_skills.append((job, skills))
    
    return jobs_and_skills

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://linkedin.github.io/future-of-skills/")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".autocomplete-list-item"))
    )

    # retrieve job and skill data
    data = get_jobs_and_skills(driver)

    with open('all_jobs_and_skills.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Job Title", "Skills"])
        for job, skills in data:
            writer.writerow([job, ', '.join(skills)])

    print("Data has been written to all_jobs_and_skills.csv")

except TimeoutException:
    print("Timed out waiting for page to load")
except NoSuchElementException:
    print("Could not find expected elements on the page")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    driver.quit()