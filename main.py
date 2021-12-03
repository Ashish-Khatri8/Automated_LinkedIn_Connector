# Import required modules.
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.relative_locator import locate_with

# Download and extract the chrome web driver in the same folder.
chrome_web_driver = "./chromedriver_linux64/chromedriver"


class AutomatedConnector:
    def __init__(self, username, password, title, pages):
        """Initializes the connector bot."""
        self.username = username
        self.password = password
        self.title = title
        self.pages = pages
        self.connection_requests_sent = 0
        self.all_links = []
        self.message = ""
        self.driver = webdriver.Chrome(service=Service(chrome_web_driver))
        self.driver.maximize_window()

    def login(self):
        """Logins with the user's id and password."""
        self.driver.get(url="https://www.linkedin.com/login")
        login = self.driver.find_element(By.ID, "username")
        login.send_keys(self.username)
        password = self.driver.find_element(By.ID, "password")
        password.send_keys(self.password)
        password.send_keys(Keys.ENTER)
        sleep(2)

    def get_all_profile_links(self):
        """
        Collects and stores links of all people profiles for the given 
        number of pages.
        """
        search = self.driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
        search.send_keys(self.title)
        search.send_keys(Keys.ENTER)
        sleep(2)
        try:
            see_people = self.driver.find_element(By.XPATH,
                                    "/html/body/div[6]/div[3]/div/div[2]/section/div/nav/div/ul/li[1]/button")
            see_people.send_keys(Keys.ENTER)
        except NoSuchElementException:
            print("Not Found")
            self.driver.quit()
        sleep(2)

        for page in range(self.pages):
            first_person = self.driver.find_element(By.XPATH,
                                "/html/body/div[6]/div[3]/div/div[2]/div/div[1]/main/div/"
                                "div/div[2]/ul/li[1]/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a")
            previous_person = first_person
            self.all_links.append(first_person.get_attribute("href"))
            for profile_num in range(9):
                current_person = self.driver.find_element(locate_with(By.TAG_NAME, "a").below(previous_person))
                self.all_links.append(current_person.get_attribute("href"))
                if profile_num != 8:
                    previous_person = current_person

            if page != self.pages-1:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                sleep(2)
                next_page = self.driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
                next_page.send_keys(Keys.ENTER)
                sleep(3)

        self.driver.get("https://www.linkedin.com/feed/")
        sleep(3)
        print(f"Links collected: {len(self.all_links)}")

    def read_message_template(self):
        """
        Loads the message_template.txt file and reads the message.
        """
        with open(file="message_template.txt", mode="r") as file:
            for line in file:
                self.message += line
        self.message = self.message.rstrip()

    def send_connection_requests(self):
        """
        Sends connection requests to all profile links collected.
        """
        self.driver.switch_to.new_window('tab')
        for link in self.all_links:
            if link.split("/")[3] != "in":
                continue
            else:
                name = link.split("/")[4].split("-")[0].title()
                personalized_message = self.message.replace("{name}", name)
                self.driver.get(link)
                sleep(2)

                try:
                    connect_button = self.driver.find_element(By.CLASS_NAME, "artdeco-button--primary")
                    if connect_button.get_attribute("aria-label").split()[0] == "Follow":
                        raise NoSuchElementException
                except NoSuchElementException:
                    try:
                        more = self.driver.find_element(By.CSS_SELECTOR,
                                                ".pvs-profile-actions .artdeco-dropdown__trigger--placement-bottom")
                        more.send_keys(Keys.ENTER)
                        connect_button = self.driver.find_element(By.CSS_SELECTOR, 'li[2] div')
                    except InvalidSelectorException:
                        continue
                connect_button.send_keys(Keys.ENTER)
                add_note = self.driver.find_element(By.CLASS_NAME, "artdeco-button--secondary")
                add_note.send_keys(Keys.ENTER)
                message_box = self.driver.find_element(By.NAME, "message")
                message_box.send_keys(personalized_message)
                sleep(5)
                # SEND
                send_button = self.driver.find_element(By.CLASS_NAME, "artdeco-button--primary")
                send_button.send_keys(Keys.ENTER)
                self.connection_requests_sent += 1
        return self.connection_requests_sent

    def terminate(self):
        """Closes the automated window."""
        self.driver.quit()


if __name__ == "__main__":
    # Get user input.
    inp_username = input("\nEnter your LinkedIn username/ e-mail:\t")
    inp_password = input("Enter your LinkedIn password:\t")
    inp_title = input("Enter the Institution/ Company name:\t")
    inp_pages = int(input("Enter number of pages:\t"))

    connect = AutomatedConnector(inp_username, inp_password, inp_title, inp_pages)
    connect.login()
    connect.get_all_profile_links()
    connect.read_message_template()
    req_sent = connect.send_connection_requests()
    connect.terminate()
    print(f"Connection requests sent: {req_sent}")
