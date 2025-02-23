from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import json
import pandas as pd

# Initialize Chrome options
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a GUI

# Initialize the Chrome driver
driver = webdriver.Chrome()

query = "it-jobs"
base_url = f"https://www.naukri.com/{query}?src=gnbjobs_homepage_srch"
driver.get(base_url)

# Lists to store data
all_data = []

page = 1
while True:
    time.sleep(5)  # Wait for the page to load

    # Get the page source and parse it with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Find all job titles
    titles = soup.select("div.sjw__tuple div.row1 a.title")
    titles_list = [title.getText().strip() for title in titles]

    # Find Company Names
    company_names_list = []
    row2_divs = soup.select("div.sjw__tuple div.row2")
    for row2 in row2_divs:
        comp_name = row2.select_one("a.comp-name")
        comp_namex = row2.select_one("span.comp-name")
        if comp_name:
            company_names_list.append(comp_name.get_text().strip())
        elif comp_namex:
            company_names_list.append(comp_namex.get_text().strip())
        else:
            company_names_list.append("Data Not Found")

    # Find ratings
    ratings = []
    ratings_availability = soup.select("div.sjw__tuple div.row2")
    for rating in ratings_availability:
        rating_check = rating.select_one("a.rating span.main-2")
        rating_checkx = rating.select_one("span.rating span.main-2")
        if rating_check:
            ratings.append(rating_check.getText().strip())
        elif rating_checkx:
            ratings.append(rating_check.getText().strip())
        else:
            ratings.append("No Ratings Available")

    # Find experience requirements
    experiences = []
    experience = soup.select("div.sjw__tuple div.row3 div.job-details span.exp-wrap")
    for exp in experience:
        expx = exp.select_one("span.exp span.expwdth")
        expy = exp.select_one("span.exp")
        if expx:
            experiences.append(expx.getText().strip())
        elif expy:
            experiences.append(expy.getText().strip())
        else:
            experiences.append("Not Disclosed")

    # Find salaries
    salaries = []
    salaries_all = soup.select("div.sjw__tuple div.row3 span.sal-wrap span.sal")
    for salary in salaries_all:
        salx = salary.select_one("span.sal span")
        if salx:
            salaries.append(salx.getText().strip())
        else:
            salaries.append(salary.getText().strip())

    locations = []
    locations_all = soup.select("div.sjw__tuple div.row3")

    for location in locations_all:
        locx = location.select_one("span.locWdth")
        locy = location.select_one(("span.location"))
        if locx:
            locations.append(locx.getText().strip())
        elif locy:
            locations.append(locy.getText().strip())
        else:
            locations.append("No Location Available")

    job_descriptions = []
    all_job_desc = soup.select("div.sjw__tuple div.row4")

    for job_desc in all_job_desc:
        job = job_desc.select_one("span.job-desc")
        if job:
            job_descriptions.append(job.getText().strip())
        else:
            job_descriptions.append(job.getText().strip())

    updation_times = []
    all_updates = soup.select("div.sjw__tuple div.row6")

    for update_day in all_updates:
        update = update_day.select_one("span.job-post-day")
        if update:
            updation_times.append(update.getText().strip())
        else:
            updation_times.append("No Data Available")

    # Collect data for the current page
    page_data = []
    for title, company, ratingx, experiencex, salaryx, locationx, descx, updationTimex in zip(titles_list,
                                                                                              company_names_list,
                                                                                              ratings, experiences,
                                                                                              salaries, locations,
                                                                                              job_descriptions,
                                                                                              updation_times):
        job_data = {
            "Job Title": title,
            "Company Name": company,
            "Ratings": ratingx,
            "Experience Required": experiencex,
            "Salary": salaryx,
            "Location": locationx,
            "Job Description": descx,
            "Updated": updationTimex
        }
        page_data.append(job_data)
        all_data.append(job_data)

    print(f"Page {page} data collected")

    # Find and click the "Next" link
    try:
        pagination_div = driver.find_element(By.CSS_SELECTOR, "div.styles_pagination__oIvXh")
        next_links = pagination_div.find_elements(By.CSS_SELECTOR, "a.styles_btn-secondary__2AsIP")

        if len(next_links) > 1:
            next_link = next_links[1]
            if next_link.is_displayed() and next_link.is_enabled():
                driver.execute_script("arguments[0].click();", next_link)
                page += 1
                time.sleep(3)
                if page==2:
                    break;
            else:
                print("No 'Next' link found or link not clickable. Ending pagination.")
                break
        else:
            print("No 'Next' link found. Ending pagination.")
            break
    except Exception as e:
        print(f"Error during pagination: {e}")
        break

# Close the driver
driver.quit()

# Save data to CSV
csv_file = "job_data.csv"
keys = all_data[0].keys()
with open(csv_file, "w", newline="", encoding="utf-8") as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_data)

# Save data to Excel
excel_file = "job_data.xlsx"
df = pd.DataFrame(all_data)
df.to_excel(excel_file, index=False)

# Save data to JSON
json_file = "job_data.json"
with open(json_file, "w", encoding="utf-8") as json_output_file:
    json.dump(all_data, json_output_file, ensure_ascii=False, indent=4)

print("Data saved to CSV, Excel, and JSON files.")
