# python
from urllib.parse import urlparse
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.config import Config
from bs4 import BeautifulSoup
from selenium import webdriver
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException
import requests
import time
import json
import sqlite3

# Set the size of the application window
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')


class ScraperApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Create input field for url
        self.create_input_field(layout)

        return layout

    def create_input_field(self, layout):
        # Create a label for the URL
        layout.add_widget(Label(text='Enter URL:'))

        # Create a text input for the url
        text_input = TextInput(hint_text='Enter URL')
        layout.add_widget(text_input)

        self.user_agent_spinner = Spinner(
            text='Choose User Agent',
            values=(
            'Default',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0'),
            disabled=True
        )
        layout.add_widget(self.user_agent_spinner)

        # Create a spinner to select scrape method
        scrape_method_spinner = Spinner(
            text='Choose Scrape Method',
            values=('Requests + BeautifulSoup', 'Selenium'),
        )
        scrape_method_spinner.bind(text=self.enable_user_agent_selection)
        layout.add_widget(scrape_method_spinner)

        # Create a spinner to select output type
        output_type_spinner = Spinner(
            text='Choose Output Type',
            values=('Json', 'SQLite'),
        )
        layout.add_widget(output_type_spinner)

        # Create a text input for output file name (for JSON type only)
        self.output_file_input = TextInput(hint_text='Enter output file name', disabled=True)
        layout.add_widget(self.output_file_input)
        output_type_spinner.bind(text=self.enable_filename_input)

        # Create a scrape button
        scrape_button = Button(text='Scrape')
        scrape_button.bind(
            on_press=lambda instance: self.scrape(scrape_method_spinner.text, self.output_file_input.text,
                                                  output_type_spinner.text, instance))
        layout.add_widget(scrape_button)

        # Create an output label for the scraping results with initial text as 'Results will be displayed here'
        output_label = Label(text='Results will be displayed here.')
        layout.add_widget(output_label)

    def enable_user_agent_selection(self, instance, value):
        if value == 'Requests + BeautifulSoup':
            self.user_agent_spinner.disabled = False
        else:
            self.user_agent_spinner.disabled = True

    def enable_filename_input(self, instance, value):
        if value.lower() == 'json':
            self.output_file_input.disabled = False
        else:
            self.output_file_input.disabled = True

    def is_valid_url(self, url):
        # Checks whether `url` is a valid URL.
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def scrape(self, scrape_method, output_file, output_type, instance):
        url = instance.parent.children[6].text
        user_agent = self.user_agent_spinner.text if not self.user_agent_spinner.disabled else None
        if not self.is_valid_url(url):
            instance.parent.children[0].text = f'Invalid URL: {url}'
            return
        if scrape_method == 'Requests + BeautifulSoup':
            self.scrape_with_bs(url, user_agent, output_file, output_type, instance)
        elif scrape_method == 'Selenium':
            self.scrape_with_selenium(url, output_type, instance)
        else:
            instance.parent.children[0].text = 'Invalid scraping method selected.'

    def scrape_with_bs(self, url, user_agent, output_file, output_type, instance):
        headers = {"User-Agent": user_agent} if user_agent != "Default" else {"User-Agent": "python-requests/2.25.0"}
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises a HTTPError if the response status is not 200
            soup = BeautifulSoup(response.content, 'html.parser')
            end_time = time.time()
            execution_time = end_time - start_time
            output = {
                'page_size': len(soup.prettify()),
                'execution_time': execution_time,
            }
            instance.parent.children[
                0].text = f'Page Size: {output["page_size"]} bytes, Time: {output["execution_time"]} seconds'
            self.save_output(output, output_file, output_type)
        except RequestException as e:
            instance.parent.children[0].text = str(e)

    def scrape_with_selenium(self, url, output_type, instance):
        try:
            start_time = time.time()
            driver = webdriver.Firefox()
            driver.get(url)
            page_source = driver.page_source
            driver.quit()
            end_time = time.time()
            execution_time = end_time - start_time
            output = {
                'page_size': len(page_source),
                'execution_time': execution_time,
            }
            instance.parent.children[
                0].text = f'Page Size: {output["page_size"]} bytes, Time: {output["execution_time"]} seconds'
            self.save_output(output, "", output_type)
        except WebDriverException as e:
            instance.parent.children[0].text = str(e)

    def save_output(self, output, output_file, output_type):
        if output_type == 'Json':
            output_file = f"{output_file}.json" if output_file else "output.json"
            with open(output_file, 'w') as f:
                json.dump(output, f)
        elif output_type == 'SQLite':
            conn = sqlite3.connect('output.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS output
                         (page_size int, execution_time real)''')
            c.execute("INSERT INTO output VALUES (?, ?)",
                      (output['page_size'], output['execution_time']))
            conn.commit()
            conn.close()


if __name__ == '__main__':
    ScraperApp().run()
