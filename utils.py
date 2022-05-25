import os
import pandas as pd
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import time, re
from timeit import default_timer as timer
import datetime


def get_chromedriver(chromedriver_path=None, use_proxy=False, user_agent=None,
                    PROXY_HOST=None, PROXY_PORT=None, PROXY_USER=None, PROXY_PASS=None):

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    chrome_options = webdriver.ChromeOptions()
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)
    if user_agent:
        chrome_options.add_argument('--user-agent=%s' % user_agent)
    driver = webdriver.Chrome(
        executable_path=chromedriver_path,
        chrome_options=chrome_options)
    return driver



def scrape_PEC(chromedriver_path=None, web_page=None, VAT_file=None, VAT_file_sep=None, OUT_file_sep=None):
    
    LOG_FILE = "log.txt"
    SMALL_TIME_SLEEP = 0.5
    start = timer()

    # read VAT list
    df_VAT = pd.read_csv(VAT_file, dtype = 'str', sep = VAT_file_sep)

    # create/reload log
    if os.path.exists(LOG_FILE):
        log = pd.read_table(LOG_FILE, delimiter = ';', dtype = 'str')
    else:
        log = pd.DataFrame(columns = ['VAT', 'PEC'])
        with open(LOG_FILE, 'a') as f:
            f.write('"VAT";"PEC"')
    
    # open browser and go to website
    print("Launching Chrome...", end ="")
    driver = get_chromedriver(chromedriver_path = chromedriver_path)
    driver.implicitly_wait(3)
    driver.get(web_page)
    print("OK", end ="\n\n")
    
    # loop VAT
    df_out = pd.DataFrame(columns = ['VAT', 'PEC'])
    tot_vat = df_VAT.shape[0]
    for vat_i, vat in enumerate(df_VAT.VAT.values):

        print("Querying VAT", str(vat_i+1), "/", str(tot_vat), end = "\r")
        if vat not in log.VAT.values:    # check if VAT already in log
            stop = 0
            while stop == 0:
                driver.find_element_by_id("partita_iva").click()
                driver.find_element_by_id("partita_iva").clear()
                driver.find_element_by_id("partita_iva").send_keys(vat)
                driver.find_element_by_id("button_calcola").click()
                time.sleep(SMALL_TIME_SLEEP)
                pec = driver.find_element_by_id('codice').get_attribute("textContent")
                if pec == '':
                    pec = 'not found'
                    stop = 1
                if pec != 'not found' and pec not in df_out.PEC.values:
                    stop = 1

            # update and save log
            log = log.append({'VAT': vat, 'PEC': pec}, ignore_index=True)
            with open(LOG_FILE, 'a') as f:
                f.write('\n"'+vat+'";"'+pec+'"')
        else:
            pec = log[log.VAT == vat].PEC.values[0]

        # update list
        df_out = df_out.append({'VAT': vat, 'PEC': pec}, ignore_index=True)

    # check for duplicated PEC
    check_PEC = df_out.PEC.value_counts().rename_axis('PEC').reset_index(name='counts')
    if check_PEC.counts.max() > 1:
        duplicated_PEC = check_PEC[check_PEC.counts > 1]
        duplicated_PEC.merge(df_out, on='PEC').sort_values(by=['PEC']).to_csv('duplicated_PEC.csv', sep=OUT_file_sep, index=False, quoting=1)
        print('\n\n ###### duplicated PEC found:', duplicated_PEC.shape[0], ' - saved in "duplicated_PEC.csv"\n')

    # display report of missing PEC
    print('\n\nVAT without PEC:', df_out[df_out.PEC == "not found"].shape[0])

    # save output
    df_out.to_csv('PEC_list.csv', sep=OUT_file_sep, index=False, quoting=1)
        
    # close browser
    driver.close()
    
    print('\n\nTotal elapsed time:', str(datetime.timedelta(seconds=round(timer()-start))))
    print('\n\nLog list saved in "' + LOG_FILE + '"')
    print('PEC list saved in "PEC_list.csv"')
