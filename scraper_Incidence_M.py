import os 
import json, time, datetime
import pandas as pd
import numpy as np 
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
pd.options.display.max_colwidth=50

########################################################################################
# Scraper
########################################################################################
def scraper_Mortality_YearSex (local_driver_path, html_dict, sex_input_by_user, year_input_by_user, target_disease_list):
    chrome_driver = webdriver.Chrome(local_driver_path)
    chrome_driver.get("https://www3.ha.org.hk/cancereg/allages.asp")

    print(f"Scraping data for year={year_input_by_user}......")
    
    # Step 1: Select data type, demographics and year range
    step1_console=chrome_driver.find_element(By.XPATH, html_dict["step1"])
    data_button=step1_console.find_element(By.XPATH, html_dict["incidence"])
    age_botton=step1_console.find_element(By.XPATH, html_dict["age_interval"])
    male_button=step1_console.find_element(By.XPATH, html_dict["male"])
    female_button=step1_console.find_element(By.XPATH, html_dict["female"])
    yr_box1=Select(chrome_driver.find_element(By.XPATH, html_dict["yr_x"]))
    yr_box2=Select(chrome_driver.find_element(By.XPATH, html_dict["yr_y"]))

    data_button.click(), age_botton.click()
    if sex_input_by_user == "m": male_button.click()
    if sex_input_by_user == "f": female_button.click()
    yr_box1.select_by_visible_text(year_input_by_user)
    yr_box2.select_by_visible_text(year_input_by_user)

    print("Checkbox status-> Incidence/Mortality:", data_button.get_attribute("value")=="1", data_button.get_attribute("value")=="2")
    print("Checkbox status-> Male/Female:", male_button.is_selected(), female_button.is_selected())
    print("Checkbox status-> Age interval:", age_botton.get_attribute("value")=="2")
    
    # Step 2: Select one or more cancer types listed below
    step2_console=chrome_driver.find_element(By.XPATH, html_dict["step2"])
    disease_codes=[i.get_attribute("name") for i in step2_console.find_elements(By.TAG_NAME, "input")]
    for i in target_disease_list:
        disease_button=step2_console.find_element(By.NAME, i)
        disease_button.click()
        print(f"Checkbox status-> {i}: {disease_button.is_selected()}")

    # Step 3 & 4: Select the standard population , Select the output format
    chrome_driver.find_element(By.XPATH, html_dict["step3"]).click()
    chrome_driver.find_element(By.XPATH, html_dict["step4"]).click()
    chrome_driver.find_element(By.XPATH, html_dict["execute"]).click()
    
    print(f"Redirecting to requested table......")
    print(f"Collecting data......")

    # Copying the requested table
    WebDriverWait(chrome_driver, 20).until(EC.number_of_windows_to_be(2))
    result_page=chrome_driver.window_handles[1]
    chrome_driver.switch_to.window(result_page)

    chrome_driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    tb1=chrome_driver.find_element(By.XPATH, '//*[@id="mi55lucky"]/div[1]')
    tb1_header=[i.text for i in tb1.find_elements(By.TAG_NAME, "th")]
    tb1_data=[i.text for i in tb1.find_elements(By.TAG_NAME, "td")]
    tb1_row_num=len(tb1_data[0::len(tb1_header)])
    tb1_data_cut=np.array_split(tb1_data, tb1_row_num)

    tb2=chrome_driver.find_element(By.XPATH, '//*[@id="mi55lucky"]/div[2]')
    tb2_header=[i.text for i in tb2.find_elements(By.TAG_NAME, "th")]
    tb2_data=[i.text for i in tb2.find_elements(By.TAG_NAME, "td")]
    tb2_row_num=len(tb2_data[0::len(tb2_header)])
    tb2_data_cut=np.array_split(tb2_data, tb2_row_num)

    df1=pd.DataFrame(data=tb1_data_cut, columns=tb1_header)
    df2=pd.DataFrame(data=tb2_data_cut, columns=tb2_header)
    df=df1.append(df2)

    chrome_driver.quit()
    print(f"Done scraping data for year={year_input_by_user}!!!")

    return df

########################################################################################
# Variables
########################################################################################
web_elements = {
    "step1": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]',
    "incidence": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[1]/input[1]',
    "mortality": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[1]/input[2]',
    "male": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[2]/input[2]',
    "female": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[2]/input[3]',
    "age_interval": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/table/tbody/tr[2]/td[2]/input',
    "yr_x": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[3]/label[1]/select',
    "yr_y": '//*[@id="content"]/div/div/div[2]/form/fieldset[1]/p[3]/label[2]/select',
    "step2": '//*[@id="content"]/div/div/div[2]/form/fieldset[2]', 
    "step3": '//*[@id="content"]/div/div/div[2]/form/fieldset[3]/p/input[1]',
    "step4": '//*[@id="content"]/div/div/div[2]/form/fieldset[4]/p/input[2]',
    "execute": '//*[@id="content"]/div/div/div[2]/form/div/input[1]'
}
gender="m"
output_folder=r"C:\Users\Yikun\OneDrive - The University Of Hong Kong\Documents\GitHub\hk_cancer_reg\data_inci"

########################################################################################
# Run
########################################################################################
for i in range(2003,2022):
    data=scraper_Mortality_YearSex(
    local_driver_path=r"C:\Users\Yikun\OneDrive - The University Of Hong Kong\Documents\GitHub\hk_cancer_reg\chromedriver.exe",
    html_dict = web_elements, year_input_by_user=str(i), 
    sex_input_by_user=gender, target_disease_list=["999"]
)
    os.chdir(output_folder)
    data.to_csv(f"Mort_{i}_{gender}.csv")