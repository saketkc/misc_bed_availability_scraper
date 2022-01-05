from selenium import webdriver;
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium import webdriver
# ~ from webdriver_manager.chrome import ChromeDriverManager


import os,requests,time,bs4,datetime,csv;
from PIL import Image
import json

if __name__=='__main__':
  
  date=datetime.datetime.now();date_str=date.strftime('%Y-%m-%d')
  
  # ~ for city in ['gbn']:
  for city in ['bengaluru']:
    if city=='bengaluru':
      #BENGALURU
      options=webdriver.ChromeOptions();
      options.add_argument('--ignore-certificate-errors');
      options.add_argument('--disable-gpu');
      options.add_argument("--headless")
      options.add_argument("--window-size=1366,768")
      options.add_argument("user-data-dir=/home/ani/.config/google-chrome/Default") #Path to your chrome profile
      options.add_experimental_option("excludeSwitches", ["enable-automation"])
      options.add_experimental_option('useAutomationExtension', False)
      # ~ driver=webdriver.Chrome(ChromeDriverManager().install(),options=options) 
      driver=webdriver.Chrome(options=options) 
      driver.get('https://www.powerbi.com/view?r=eyJrIjoiOTcyM2JkNTQtYzA5ZS00MWI4LWIxN2UtZjY1NjFhYmFjZDBjIiwidCI6ImQ1ZmE3M2I0LTE1MzgtNGRjZi1hZGIwLTA3NGEzNzg4MmRkNiJ9')
      time.sleep(30)
      # ~ print(driver.page_source)
      # WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME,"iframe")))
      # print("---n---")
      # print(driver.page_source)
      parent = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
      # parent = driver.find_element(By.TAG_NAME,'body')
      # ~ print("HERE!!#@@##$!#$")
      
      v = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,'visualContainerHost')))
      # v = parent.find_element(By.CLASS_NAME,'visualContainerHost')
      v = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME,'multiRowCard')))
      # v =  v.find_elements(By.CLASS_NAME,'multiRowCard')
      results = []
      for e in v:
        cards = e.find_elements(By.CLASS_NAME,'card')
        for c in cards:
          label = c.get_attribute('aria-label')
          label = label.replace('.','')
          res = [int(i) for i in label.split() if i.isdigit()]
          results.append([res[1],res[3]])

      print(results)
      general_available = results[0][1]
      general_admitted = results[0][0]

      hdu_available = results[1][1]
      hdu_admitted = results[1][0]

      icu_available = results[2][1]
      icu_admitted = results[2][0]

      ventilator_available = results[3][1]
      ventilator_admitted = results[3][0]


      a=open('data.bengaluru.csv');r=csv.reader(a);info=[i for i in r];a.close()
      dates=list(set([i[0] for i in info[1:]]));dates.sort()
      
      if date_str in dates: 
        # ~ dont_update_data_csv=True
        print('----------\n\nData for %s already exists in csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
      else:
        #write to file
        info=', '.join((date_str,str(general_available),str(general_admitted),str(hdu_available),str(hdu_admitted),str(icu_available),str(icu_admitted),str(ventilator_available),str(ventilator_admitted)))        
        a=open('data.bengaluru.csv','a');a.write(info+'\n');a.close()
        print('Appended to data.bengaluru.csv: '+info) 
