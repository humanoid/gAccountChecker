import pandas as pd
from selenium import webdriver
import sys
import os
pcr_export = sys.argv[1] if len(sys.argv) > 1 else ''
try:
    pd.read_csv(pcr_export, delimiter=',', header=0, dtype=str)
    print("Using passed file ({}).".format(os.path.basename(pcr_export)))
except Exception as FileNotFoundError:
    file_not_found_error = "Please enter a valid file path."
    print(file_not_found_error)
    while True:
        pcr_export = input("Enter file path to PCR export: ").replace('"', "")
        try:
            pd.read_csv(pcr_export, delimiter=',', header=0, dtype=str)
            print("Using inputted file.\nProcessing...")
            break
        except FileNotFoundError:
            print(file_not_found_error)
            continue
        except KeyboardInterrupt:
            sys.exit()
print("Processing...")
file_out = os.path.join(os.path.dirname(os.path.realpath(pcr_export)), os.path.splitext(pcr_export)[0] + ' - Google PCR Import.txt')
pcr_export = pd.read_csv(pcr_export, delimiter=',', dtype=str)
emails_df = pd.DataFrame()
emails_df['lookup_household_id'] = pcr_export['Household Id']
results = {}
emails_init_size = len(results)
print("Launching Chrome...")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
if int(browser.capabilities['version'].split('.')[0]) >= 60:
    print("You are running Chrome v60+. Chrome is therefore running headless.")
print("Itterating through records...")
for index, row in emails_df.iterrows():
    for email_name in pcr_export.columns:
        if isinstance(pcr_export[email_name][index], str) and 'Type' not in email_name and 'Email' in email_name:
            print(pcr_export[email_name].iloc[index], end=" ")
            browser.get('https://accounts.google.com/signin/recovery/lookup')
            email = browser.find_element_by_xpath('//*[@id="identifier"]')
            next_button = browser.find_element_by_xpath('//*[@id="next"]')
            email.send_keys(pcr_export[email_name].iloc[index])
            next_button.click()
            try:
                error = browser.find_element_by_xpath(
                    '//*[@id="identifierError"]')
                print('does not have a Google Account')
            except:
                emails_df.set_value(index, "{}{} Type".format(email_name, '1' if not email_name[-1].isdigit() else '').replace(' ', '_'), 'Google')
                print("has a Google Account")
print("Exporting results to CSV...")
emails_df.to_csv(file_out, sep="\t", index=False)
print("Closing Chrome...")
browser.quit()
print("All done! View file at {}".format(file_out))
