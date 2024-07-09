import re
import html
import requests
import json
from pprint import pprint
import sqlite3


def get_content():
    response = requests.get('https://www.lejobadequat.com/emplois')
    html = response.text
    # print(f"PAGE CONTENT:\n {content}")
    return html


def get_vacancies(content):
    title_pattern = r'<h3 class="jobCard_title">(.*?)</h3>'
    url_pattern = r'<a href="(.*?)" title="Consulter l\'offre d\'emploi .+?" class="jobCard_link"'

    job_titles = [html.unescape(title) for title in re.findall(title_pattern, content)]

    job_urls = re.findall(url_pattern, content)
    # Create a dictionary with titles as keys and URLs as values
    job_dict = dict(zip(job_titles, job_urls))

    # print(f"job_titles:\n {job_titles}")
    # print(f"job_urls:\n {job_urls}")
    # print(f"job_dict:\n {job_dict}")
    return job_dict


def write_json(data):
    filename = 'vacancies.json'
    pprint(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def save_to_db(data):
    conn = sqlite3.connect("vacancies.db")

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies
        (id INTEGER PRIMARY KEY,
         title TEXT NOT NULL,
         url TEXT NOT NULL);
        ''')

    for title, url in data.items():
        # Check if the data already exists in the table
        cursor.execute("SELECT * FROM vacancies WHERE title = ? AND url = ?", (title, url))
        data = cursor.fetchone()

        # If data does not exist, then insert it
        if data is None:
            cursor.execute("INSERT INTO vacancies (title, url) VALUES (?, ?)", (title, url))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    content = get_content()
    job_titles = get_vacancies(content)
    # print(f"Job Titles:\n {job_titles}")
    # Write Jobs results to Json
    write_json(data=job_titles)
    # Write Jobs results to SQLite
    save_to_db(data=job_titles)

