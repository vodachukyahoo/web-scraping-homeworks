import json
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def write_json(data, filename='jobs_with_urls.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_job_with_link(driver, result, site_url):
    driver.get(site_url)

    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ais-Hits')))
    jobs = driver.find_elements(By.CLASS_NAME, 'ais-Hits-item')

    for job in jobs:
        title = job.find_element(By.TAG_NAME, 'h3').text
        url = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
        result.append({'title': title, 'url': url})


def parse_jobs():
    site = 'https://jobs.marksandspencer.com/job-search'
    result = []
    page_counter = 0
    driver = Chrome()

    while page_counter < 2:
        try:
            get_job_with_link(driver, result, site)
            site = driver.find_element(By.XPATH,
                                            '/html/body/div[2]/main/section/'
                                            'div/div[3]/div[2]/div[2]/div[2]/div/ul/li[9]/a').get_attribute('href')
            page_counter += 1
        except Exception as e:
            print(e)
            # Next page button doesn't exist or not clickable
            break

    driver.quit()

    write_json(result)


if __name__ == '__main__':
    parse_jobs()
