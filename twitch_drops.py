from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
from time import localtime, strftime
from random import randrange

chrome_options = Options()
chrome_options.headless = False
chrome_options.add_argument("user-data-dir=C:\\Users\\" + os.getlogin() + "\\AppData\\Local\\Google\\Chrome\\User Data")
driver = webdriver.Chrome(os.path.dirname(__file__) + '\\chromedriver.exe', options=chrome_options)
home = ''
urls_list = []
twitch_base = 'https://www.twitch.tv'
twitch_inventory = '/drops/inventory'
twitch_campaigns = '/drops/campaigns'
time.sleep(2)


def find_goto_window(url):
    # Go to tab if already exists, if not create tab then go to.
    global urls_list
    if url in urls_list:
        for w in driver.window_handles:
            driver.switch_to.window(w)
            current_url = driver.current_url
            if url == current_url:
                break
    if url not in urls_list:
        driver.execute_script("window.open('" + url + "');")
        urls_list.append(url)
        find_goto_window(url)


def check_status(url):
    try:
        driver.implicitly_wait(3)
        status = driver.find_element_by_tag_name('div[class="ScChannelStatusTextIndicator-sc-1f5ghgf-0 dVmkcd tw-channel-status-text-indicator"]')
        print(status.text)
        return True
    except:
        print('Channel Offline, Closing Window.')
        driver.close()
        urls_list.remove(url)
        return False


def close_window(url):
    # Close input URL and return to home page
    global urls_list
    if url in urls_list:
        for w in driver.window_handles:
            driver.switch_to.window(w)
            current_url = driver.current_url
            if url == current_url:
                driver.close()
                urls_list.remove(url)
                find_goto_window(home)


def start():
    global home, urls_list
    for u in urls_list:
        if u != home:
            close_window(u)
    driver.get(twitch_base + twitch_inventory)
    print('Checking Items Already Claimed on Twitch & Claiming any Completed.')
    ready_to_claim = driver.find_elements_by_tag_name('button[data-test-selector="DropsCampaignInProgressRewardPresentation-claim-button"]')
    for c in ready_to_claim:
        try:
            c.click()
            time.sleep(2)
        except:
            pass
    if len(ready_to_claim) > 0:
        driver.refresh()
    time.sleep(3)
    driver.implicitly_wait(10)
    claimed = driver.find_elements_by_tag_name('p[data-test-selector="awarded-drop__drop-name"]')
    claimed_items = []
    for item in claimed:
        claimed_items.append(item.text.lower())
    time.sleep(5)
    # Check Drops Campaigns
    print('Checking Current Drop Campaigns')
    driver.get(twitch_base + twitch_campaigns)
    home = driver.current_url
    urls_list.append(home)
    driver.implicitly_wait(8)
    # Find each drop campaign currently active
    current_campaigns = driver.find_elements_by_tag_name('div[class="tw-border-b"]')
    # Loop through each currently active campaign
    for c in current_campaigns:
        time.sleep(2)
        c.click()
        connected = False
        try:
            # Check for connected text in information, else drop wont activate, no point continuing
            if c.find_element_by_tag_name('span[class="ScPill-sc-1cbrhuy-0 kDgWbl tw-pill tw-semibold tw-upcase"]').text.lower() == 'connected':
                connected = True
        except:
            print('Game Account Not Connected.')
            pass
        if connected:
            print('Checking for Items Still Required.')
            # Details for selected campaign
            details = c.find_elements_by_tag_name('div[class="tw-flex tw-mg-b-2"]')
            # Get names of all items in selected campaign
            items = details[0].find_elements_by_tag_name('div[class="tw-flex tw-flex-column tw-mg-t-2"]')
            # Loop through items individually and compare to items claimed list to determine if any are not earned/claimed
            items_still_needed = False
            for i in items:
                time.sleep(1)
                item_name = i.find_element_by_tag_name('p[class="tw-font-size-5 tw-semibold"]').text.lower()
                if item_name not in claimed_items:
                    items_still_needed = True
                    print(item_name + ' Still Required.')
                if item_name in claimed_items:
                    print(item_name + 'Already Claimed.')
            if items_still_needed:
                # Get channels where items can be earned for this campaign, Check to see if the campaigns are channel specific or game specific
                how_to = details[1].find_elements_by_tag_name('li')[0]
                channels = how_to.find_elements_by_tag_name('a')
                # If channels > 1 == drop is channel specific,
                if len(channels) > 1:
                    # go to channel/s and check for stream status if offline close window, try next if exists
                    print('Checking Specific Streamers for LIVE status')
                    channel_index = 1
                    while channel_index < len(channels):
                        time.sleep(2)
                        url = channels[channel_index].get_attribute('href')
                        username = channels[channel_index].text.replace('/', '')
                        time.sleep(1)
                        driver.execute_script("window.open('" + url + "');")
                        urls_list.append(url)
                        current_window = driver.current_url
                        find_goto_window(url)
                        live = check_status(url)
                        find_goto_window(current_window)
                        if live:
                            print(username + ' Status: LIVE')
                            break
                        if not live:
                            print(username + ' Status: OFFLINE')
                        channel_index += 1
                # else if channels == 1: drop is game specific
                # Go to game channel browser with drops enabled tag then select random stream in list
                else:
                    print('Randomly Selecting Streamer with Required Drops Enabled.')
                    time.sleep(2)
                    url = channels[0].get_attribute('href')
                    time.sleep(1)
                    driver.execute_script("window.open('" + url + "');")
                    urls_list.append(url)
                    current_window = driver.current_url
                    find_goto_window(url)
                    urls_list.remove(url)
                    time.sleep(2)
                    streams = driver.find_elements_by_tag_name('a[data-a-target="preview-card-image-link"]')
                    streams[randrange(len(streams))].click()
                    driver.implicitly_wait(3)
                    urls_list.append(driver.current_url)
                    find_goto_window(current_window)
                time.sleep(5)
            if not items_still_needed:
                print('Drop Campaign Already Complete.')
    # Stand down time before starting loop again.
    find_goto_window(home)
    urls_list.remove(home)
    print('Last Run Completed At ' + strftime("%H:%M", localtime()))
    print('Next Run Starting in 30 Minutes.')


start()
