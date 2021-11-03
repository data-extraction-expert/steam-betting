import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import threading
import functools

###########
# User Config
###########
accounts_amount = 1  # any integer
sleep_amount = 180  # any integer
browser = "Firefox"  # Chrome or Firefox
headless_method = True  # True or False


############
# Main Class
############
class SteamDoubleBet:
    def __init__(self):
        self.bet_flag = list()
        self.error_ocurred = False
        self.all_joined = False
        self._times = 0
        self.remain_time_flag = False
        if not os.path.exists(f"logs"):
            os.mkdir("logs")
        self.log_file = f"logs/log_{time.time()}.log"

    def log(self, text):
        with open(self.log_file, "a") as log_file:
            log_file.write(text + "\n")

    def set_driver(self):

        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/80.0.3987.132 Safari/537.36"
        )

        if browser == "Chrome":
            caps = DesiredCapabilities.CHROME
            caps["pageLoadStrategy"] = "normal"
            # /* normal */
            chrome_options = webdriver.ChromeOptions()
            if headless_method:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(f"user-agent={user_agent}")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--log-level=3")
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options,
                desired_capabilities=caps,
            )
        elif browser == "Firefox":
            caps = DesiredCapabilities.FIREFOX
            caps["pageLoadStrategy"] = "normal"
            firefox_options = webdriver.FirefoxOptions()
            if headless_method:
                firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")
            firefox_options.add_argument("--start-maximized")
            firefox_options.add_argument("--log-level=3")
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(),
                options=firefox_options,
                desired_capabilities=caps,
            )

        driver.set_window_size(1024, 960)
        return driver

    def perform(self, index, account):
        try:
            # parse account
            account = account.strip()
            _username = account.split(":")[0]
            _password = account.split(":")[1]
            _color = account.split(":")[2]
            _color = "red" if _color == "R" else "black"

            ################
            # Create Driver
            ################
            driver = self.set_driver()
            driver.get("https://easyskins.com/game/double")
            login = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath(
                    '//header[@class="site-header"]//div[contains(@class, "button-yello")]'
                )
            )

            ################
            # Login
            ################
            driver.get(
                "https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.return_to=http%3A%2F%2Fauth.csgoskins.link%2Freturn&openid.realm=http%3A%2F%2Fauth.csgoskins.link%2F"
            )

            username = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath(
                    '//input[@id="steamAccountName"]'
                )
            )
            username.send_keys(_username)

            password = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath(
                    '//input[@id="steamPassword"]'
                )
            )
            password.send_keys(_password)

            login = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath('//input[@id="imageLogin"]')
            )
            driver.execute_script("arguments[0].click();", login)
            time.sleep(5)

            driver.get("http://auth.csgoskins.link/auth")

            re_login = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath('//input[@id="imageLogin"]')
            )
            driver.execute_script("arguments[0].click();", re_login)

            logout = WebDriverWait(driver, sleep_amount).until(
                lambda driver: driver.find_element_by_xpath(
                    '//div[@class="auth-block"]//span'
                )
            )

            ################
            # Balance
            ################
            balance = (
                WebDriverWait(driver, sleep_amount)
                .until(
                    lambda driver: driver.find_element_by_xpath(
                        '//div[contains(@class, "user-balance")]//span[@class="coins-value"]'
                    )
                )
                .text
            )

            if int(balance):
                print(f"Process-{index}: Account: {_username} / Balance: {balance}")
                balance = 10
                coin = WebDriverWait(driver, sleep_amount).until(
                    lambda driver: driver.find_element_by_xpath(
                        '//input[contains(@class, "coins-input")]'
                    )
                )
                coin.send_keys(Keys.CONTROL + "a")
                coin.send_keys(Keys.DELETE)
                coin.send_keys(balance)

                while True:
                    try:
                        if self.error_ocurred:
                            print(
                                f"Process-{index} => Error Occured on Other Processes. Exiting Process.."
                            )
                            break

                        ################
                        # Bet
                        ################
                        remain_time = (
                            WebDriverWait(driver, sleep_amount)
                            .until(
                                lambda driver: driver.find_element_by_xpath(
                                    f"//div[@class='countdown-timer']/span[@class='seconds']"
                                )
                            )
                            .text.strip()
                        )
                        if int(remain_time) > 20:
                            self.bet_flag[index] = True
                            if all(self.bet_flag):
                                if not self.all_joined:
                                    self.all_joined = True
                                    print("Joined All processes..")

                                bet = WebDriverWait(driver, sleep_amount).until(
                                    lambda driver: driver.find_element_by_xpath(
                                        f"//ul[contains(@class, 'place-bet-buttons-list')]/li[contains(@class, '{_color}')]"
                                    )
                                )
                                if "disabled" not in bet.get_attribute("class"):
                                    print(
                                        f"Process-{index} => Account: {_username} / Bet {balance} to '{_color}'-option"
                                    )
                                    driver.execute_script("arguments[0].click();", bet)
                                    break
                                else:
                                    time.sleep(0.5)
                                    continue
                            else:
                                time.sleep(0.5)
                                continue
                        else:
                            time.sleep(1)
                            continue

                    except KeyboardInterrupt:
                        print(
                            f"Process-{index} => Exiting Process by Keyboard Interrupt..."
                        )
                        break
                    except:
                        traceback.print_exc()
                        self.error_ocurred = True
                        break

                ################
                # Logout
                ################
                time.sleep(3)
                driver.execute_script("arguments[0].click();", logout)

            else:
                self.bet_flag[index] = True
                print(f"Process-{index} => Account: {_username} / No Balance")
                self.log(f"Account: {_username} / No Balance")
        except TimeoutException:
            print(
                f"Process-{index} => Timeout Error Occured, Increase sleep time amount."
            )
            self.error_ocurred = True
        except NoSuchElementException:
            print(
                f"Process-{index} => Can not Load Page Fully, Increase sleep time amount."
            )
            self.error_ocurred = True
        except:
            traceback.print_exc()
            self.error_ocurred = True
        finally:
            driver.quit()
            print(f"Process-{index} => Exited Process.")

    def start(self):
        try:
            with open("accounts.txt", "r", encoding="utf-8") as accounts_file:
                self.accounts = accounts_file.readlines()

            while True:
                try:
                    # init all flags
                    self.bet_flag = list()
                    self.all_joined = False
                    self.error_ocurred = False
                    self.remain_time_flag = False
                    self._times += 1

                    acc_start_num = (self._times - 1) * accounts_amount
                    acc_end_num = self._times * accounts_amount
                    if acc_start_num > len(self.accounts):
                        break

                    threads = list()
                    accounts = self.accounts[acc_start_num:acc_end_num]
                    for index, account in enumerate(accounts):
                        thread = threading.Thread(
                            target=functools.partial(self.perform, index, account)
                        )
                        thread.start()
                        threads.append(thread)
                        self.bet_flag.append(False)
                        time.sleep(5)

                    for t in threads:
                        t.join()
                except KeyboardInterrupt:
                    print("Exiting...")
                    break
                except:
                    traceback.print_exc()
                    break
        finally:
            pass


tester = SteamDoubleBet()
tester.start()
