from selenium import webdriver;
import os,requests,time,bs4,datetime,csv;
from PIL import Image
import json

if __name__=='__main__':
  
  date=datetime.datetime.now();date_str=date.strftime('%d_%m_%Y')
  
  # ~ for city in ['bengaluru','chennai']:
  for city in ['chennai']:
    if city=='bengaluru':
      #BENGALURU
      options = webdriver.ChromeOptions();
      options.add_argument('--ignore-certificate-errors');
      options.add_argument('--disable-gpu');
      options.add_argument("--headless")
      options.add_argument("--window-size=1366,768")
      driver=webdriver.Chrome(chrome_options=options)  
      driver.get('https://apps.bbmpgov.in/Covid19/en/bedstatus.php')
      driver.get('https://www.powerbi.com/view?r=eyJrIjoiOTcyM2JkNTQtYzA5ZS00MWI4LWIxN2UtZjY1NjFhYmFjZDBjIiwidCI6ImQ1ZmE3M2I0LTE1MzgtNGRjZi1hZGIwLTA3NGEzNzg4MmRkNiJ9')
      time.sleep(10)
      date=datetime.datetime.now();date_str=date.strftime('%d_%m_%Y')
      if not os.path.exists('images/'+date_str+'.png'):
        driver.save_screenshot('images/'+date_str+'.png')
        img=Image.open('images/'+date_str+'.png')
        img.save('images/'+date_str+'.webp')
        print('saved screenshot of bengaluru beds availability dashboard to %s' %('images/'+date_str+'.webp'))
      else:
        print('Image: %s already existed. Skipping!!' %('images/'+date_str+'.png'))
    elif city=='chennai':
      #CHENNAI
      import requests
      from requests.structures import CaseInsensitiveDict
      
      url = "https://tncovidbeds.tnega.org/api/hospitals"
      
      headers = CaseInsensitiveDict()
      headers["authority"] = "tncovidbeds.tnega.org"
      #headers["sec-ch-ua"] = "" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96""
      headers["dnt"] = "1"
      headers["sec-ch-ua-mobile"] = "?0"
      headers["user-agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
      headers["content-type"] = "application/json;charset=UTF-8"
      headers["accept"] = "application/json, text/plain, */*"
      headers["token"] = "null"
      #headers["sec-ch-ua-platform"] = ""Linux""
      headers["sec-ch-ua-platform"] = "Linux"
      headers["origin"] = "https://tncovidbeds.tnega.org"
      headers["sec-fetch-site"] = "same-origin"
      headers["sec-fetch-mode"] = "cors"
      headers["sec-fetch-dest"] = "empty"
      headers["accept-language"] = "en-US,en;q=0.9"
      #headers["cookie"] = "_ga=GA1.2.1493856265.1640076462; _gid=GA1.2.514620938.1640076462; _gat=1"
      
      data = '{"searchString":"","sortCondition":{"Name":1},"pageNumber":1,"pageLimit":200,"SortValue":"Availability","ShowIfVacantOnly":"","Districts":["5ea0abd2d43ec2250a483a40"],"BrowserId":"6f4dfda2b7835796132d69d0e8525127","IsGovernmentHospital":true,"IsPrivateHospital":true,"FacilityTypes":["CHO"]}'
      
      
      resp = requests.post(url, headers=headers, data=data)
      
      print(resp.status_code)
      y=json.loads(resp.content.decode('unicode_escape').replace('\n',''))
      tot_o2_beds=0;tot_non_o2_beds=0;tot_icu_beds=0;
      occupied_o2_beds=0;occupied_non_o2_beds=0;occupied_icu_beds=0;
      vacant_o2_beds=0;vacant_non_o2_beds=0;vacant_icu_beds=0;
      
      for i in y['result']:
        tot_o2_beds+=i['CovidBedDetails']['AllotedO2Beds']
        tot_non_o2_beds+=i['CovidBedDetails']['AllotedNonO2Beds']
        tot_icu_beds+=i['CovidBedDetails']['AllotedICUBeds']
        occupied_o2_beds+=i['CovidBedDetails']['OccupancyO2Beds']
        occupied_non_o2_beds+=i['CovidBedDetails']['OccupancyNonO2Beds']
        occupied_icu_beds+=i['CovidBedDetails']['OccupancyICUBeds']
        vacant_o2_beds+=i['CovidBedDetails']['VaccantO2Beds']
        vacant_non_o2_beds+=i['CovidBedDetails']['VaccantNonO2Beds']
        vacant_icu_beds+=i['CovidBedDetails']['VaccantICUBeds']
      print('In Chennai, on %s\nO2: %d/%d occupied\nNon-O2 %d/%d occupied\nICU: %d/%d occupied' %(date_str,occupied_o2_beds,tot_o2_beds,occupied_non_o2_beds,tot_non_o2_beds,occupied_icu_beds,tot_icu_beds))
      
      
      a=open('data.chennai.csv');r=csv.reader(a);info=[i for i in r];a.close()
      dates=list(set([i[0] for i in info[1:]]));dates.sort()
      
      if date_str in dates: 
        # ~ dont_update_data_csv=True
        print('----------\n\nData for %s already exists in csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
      else:
        #write to file
        info=', '.join((date_str,str(tot_o2_beds),str(tot_non_o2_beds),str(tot_icu_beds),str(occupied_o2_beds),str(occupied_non_o2_beds),str(occupied_icu_beds)))        
        a=open('data.chennai.csv','a');a.write(info);a.close()
        print('Appended to data.chennai.csv: '+info)        
  
