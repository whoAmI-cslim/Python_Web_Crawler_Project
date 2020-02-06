### General imports ###
import sys
import os
import requests 
import json
from bs4 import BeautifulSoup 
import pandas as pd
import time
#from tqdm import tqdm ### I still have to figure this one out ###

### Username and Password import ###
from secrets2 import USRName, Passwd

### Selenium imports ###
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

### Kill firefox processes ###
os.system("pkill firefox")
time.sleep(2)

### Start browser ###
global browser

browser = webdriver.Firefox(executable_path='geckodriver')

### Yahoo Finance Login Op ###
def yahoo_login(url):
    browser.get(url)

    emailElem = browser.find_element_by_id('login-username')
    emailElem.send_keys(USRName)

    loginbtn=browser.find_element_by_id("login-signin")
    loginbtn.click()

    passwordElem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "login-passwd")))
    passwordElem.send_keys(Passwd)

    submitBtn=browser.find_element_by_id("login-signin")
    submitBtn.click()
    time.sleep(2)

### Update yahoo finance screener data every 5 seconds ###
def organize_data():
    
    global Symbols
    global Names
    global Prices
    global Change
    global ChangePercent
    global Volume
    global PERatio
    global Week52Low
    global Week52High
    
    Symbols = []
    Names = []
    Prices = []
    Change = []
    ChangePercent = []
    Volume = []
    AvgVolume = []
    PERatio = []
    Week52Low = []
    Week52High = []
    
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.findAll('table', {"class" : 'W(100%)'})    
   
    ### Get Symbol, Stock Name, Stock Price, Change, Change % Volume, Avg Volume, and PE Ratio ###
    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:     
            col_val = row.find_all('td')
            col_val = [cell.text.strip() for cell in col_val]
            Symbols.append(col_val[0])
            Names.append(col_val[1])
            Prices.append(col_val[2])
            Change.append(col_val[3])
            ChangePercent.append(col_val[4])
            Volume.append(col_val[5])
            AvgVolume.append(col_val[6])
            PERatio.append(col_val[7])
      
    ### get 52 week high and 52 week low for specific symbols###
    for i in range(0, (len(Symbols))):
        symbol = Symbols[i]
        url = ("https://finance.yahoo.com/quote/" + symbol + "?p=" + symbol)
        browser.execute_script("window.open('','_blank')")
        time.sleep(1)
        browser.switch_to.window(browser.window_handles[1])
        browser.get(url)
        val = browser.find_element_by_xpath('//*[@id="quote-summary"]/div[1]/table/tbody/tr[6]/td[2]').text
        valparts = val.split('-')
        Week52Low.append(valparts[0])
        Week52High.append(valparts[1])
        time.sleep(1)
        browser.close()
        browser.switch_to.window(browser.window_handles[0])

        
    ### display all data in pandas ###   
    df = pd.DataFrame(
        {'Symbol': Symbols,
        'Names': Names,
        'Prices': Prices,
        'Change': Change,
        'Change Percentage': ChangePercent, 
        'Volume': Volume,
        'Average Volume (3 months)': AvgVolume,
        'PE Ratio (TTM)': PERatio,
        '52 Week Low': Week52Low,
        '52 Week High': Week52High})
    
    ### turn panda data into json ###
    df.to_json('data.json')
         
 ### main section ###

def main():
    yahoo_login('https://finance.yahoo.com/screener/bbbf9769-a26a-4813-a13c-d227a336a693')# you can give it an url as parameter
    #update and organize data 5 times, with 5 second intervals
#    for i in range(1, 5): ### use this and below for iteration as required ###
#    print("updating data") ### see above ###
    organize_data() ### make sure to indent this properly if you remove the comments above ###
    time.sleep(5) ### same as above ###
    print ("Complete") ### same as above ###
    browser.quit() 

if __name__ == "__main__":
    main()

### end of program ###

### Just incase I need this later. This pulls the column headers for the original data table ###

#    column_head = []
#    flat_list = []
    
#    for table in tables:
#        table_headers = table.find('thead')
#        headers = table_headers.find_all('th')
 
#        for header in headers:  
#            col_head = header.find_all('span')
#            col_head = [cell.text.strip() for cell in col_head]
#            column_head.append(col_head)
            
#    for sublist in column_head:
#        for item in sublist:
#            flat_list.append(item)
    