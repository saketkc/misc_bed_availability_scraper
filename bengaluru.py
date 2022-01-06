from bs4 import BeautifulSoup
from tabula import read_pdf

import os,requests,datetime,csv;
import json

if __name__=='__main__':
  
  date=datetime.datetime.now();date_str=date.strftime('%Y-%m-%d')
  
  for city in ['bengaluru']:
    if city=='bengaluru':
      #BENGALURU

      url = "https://apps.bbmpgov.in/Covid19/en/mediabulletin.php"

      response = requests.get(url)
      soup = BeautifulSoup(response.text, 'html.parser')
      links = soup.find_all('a')
        
      for link in links:
          if ('.pdf' in link.get('href', [])):
              print("Downloading pdf...")

              l = "https://apps.bbmpgov.in/Covid19/en/"+link.get('href').replace(" ","%20")
              print(l)
              response = requests.get(l)
              pdf = open("BLR_"+str(date_str)+".pdf", 'wb')
              pdf.write(response.content)
              pdf.close()
              break
  
      # print(text)
      tables = read_pdf("BLR_"+str(date_str)+".pdf", pages=12)
      df=tables[0]
      
      results=[]
      results.append(df.iloc[14][-2].split())
      results.append(df.iloc[14][-1].split())
      print(results)

      general_available = results[1][0]
      general_admitted = results[0][0]

      hdu_available = results[1][1]
      hdu_admitted = results[0][1]

      icu_available = results[1][2]
      icu_admitted = results[0][2]

      ventilator_available = results[1][3]
      ventilator_admitted = results[0][3]


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

    elif city=='gbn':
 #check if data for given date already exists in csv. Update only if data doesn't exist
      a=open('data.gbn.csv');r=csv.reader(a);info=[i for i in r];a.close()
      dates=list(set([i[0] for i in info[1:] if len(i)>0]));dates.sort()
      
      dont_update_data_csv=False
      if date_str in dates: 
        dont_update_data_csv=True
        print('----------\n\nData for %s already exists in csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
     
      #get data
      import requests
      from requests.structures import CaseInsensitiveDict
    
      url = "https://api.gbncovidtracker.in/hospitals"
      
      headers = CaseInsensitiveDict()
      headers["Connection"] = "keep-alive"
      headers["Accept"] = "application/json, text/plain, */*"
      headers["DNT"] = "1"
      headers["sec-ch-ua-mobile"] = "?0"
      headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
      headers["sec-ch-ua-platform"] = "Linux"
      headers["Origin"] = "https://gbncovidtracker.in"
      headers["Sec-Fetch-Site"] = "same-site"
      headers["Sec-Fetch-Mode"] = "cors"
      headers["Sec-Fetch-Dest"] = "empty"
      headers["Referer"] = "https://gbncovidtracker.in/"
      headers["Accept-Language"] = "en-US,en;q=0.9"
      
      
      resp = requests.get(url, headers=headers)
      # ~ print('api call status code: ', resp.status_code)
      
      y=resp.json()
      
      if y:
        tot_beds=0;tot_o2_beds=0;tot_ventilator_beds=0;
        occupied_beds=0;occupied_o2_beds=0;occupied_ventilator_beds=0;
        
        for i in y:
          tot_beds+=int(i['normal'])
          tot_o2_beds+=int(i['oxygen'])
          tot_ventilator_beds+=int(i['ventilator'])
          occupied_beds+=(int(i['normal'])-int(i['Vacant_normal']))
          occupied_o2_beds+=(int(i['oxygen'])-int(i['Vacant_oxygen']))
          occupied_ventilator_beds+=(int(i['ventilator'])-int(i['Vacant_ventilator']))
          
        
        # ~ for bed_type in ['beds', 'oxygen_beds', 'covid_icu_beds', 'ventilators', 'icu_beds_without_ventilator', 'noncovid_icu_beds']:
        info='%s,%d,%d,%d,%d,%d,%d\n' %(date_str,tot_beds,tot_o2_beds,tot_ventilator_beds,occupied_beds,occupied_o2_beds,occupied_ventilator_beds)
        
        #write to file
        a=open('data.gbn.csv','a')
        if not dont_update_data_csv:
          a.write(info+'\n')
        print('gbn: '+info)
        a.close()
      else:
        print('could not get data from https://api.gbncovidtracker.in/hospitals')
    
    elif city=='delhi':
      #check if data for given date already exists in csv. Update only if data doesn't exist
      a=open('data.delhi.csv');r=csv.reader(a);info=[i for i in r];a.close()
      dates=list(set([i[0] for i in info[1:]]));dates.sort()
      
      dont_update_data_csv=False
      if date_str in dates: 
            dont_update_data_csv=True
            print('----------\n\nData for %s already exists in csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
      
      #get data
      y=str(requests.get('https://coronabeds.jantasamvad.org/covid-info.js').content);
      if y:
            y=json.loads(y[y.find('{'):y.rfind('}')+1].replace('\\n','').replace("\\'",''))
            info=''
            
            # ~ for bed_type in ['beds', 'oxygen_beds', 'covid_icu_beds', 'ventilators', 'icu_beds_without_ventilator', 'noncovid_icu_beds']:
            # ~ info+='%s,%s,%d,%d,%d\n' %(date_str,bed_type,y[bed_type]['All']['total'],y[bed_type]['All']['occupied'],y[bed_type]['All']['vacant'])
            info+='%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' %(date_str,y['beds']['All']['total'],y['oxygen_beds']['All']['total'],y['covid_icu_beds']['All']['total'],y['ventilators']['All']['total'],y['icu_beds_without_ventilator']['All']['total'],y['noncovid_icu_beds']['All']['total'],y['beds']['All']['occupied'],y['oxygen_beds']['All']['occupied'],y['covid_icu_beds']['All']['occupied'],y['ventilators']['All']['occupied'],y['icu_beds_without_ventilator']['All']['occupied'],y['noncovid_icu_beds']['All']['occupied'])    
            print('delhi: '+info)

            #write to file            
            if not dont_update_data_csv: a=open('data.delhi.csv','a');a.write(info+'\n');a.close()
      else:
            print('could not get data from https://coronabeds.jantasamvad.org/covid-info.js')

    elif city=='pune':
      x=os.popen('curl -k https://divcommpunecovid.com/ccsbeddashboard/hsr').read()
      soup=BeautifulSoup(x,'html.parser');
      xx=soup('legend')[1].parent
      xx=xx('table')[0]
      tot_beds,vacant_beds,tot_normal,vacant_normal,tot_o2,vacant_o2,tot_icu,vacant_icu,tot_vent,vacant_vent=[i.text for i in xx('td') if i.text.isnumeric()]
      print(tot_beds,tot_normal,tot_o2,tot_icu,tot_vent,vacant_beds,vacant_normal,vacant_o2,vacant_icu,vacant_vent)
      occupied_normal=int(tot_normal)-int(vacant_normal)
      occupied_o2=int(tot_o2)-int(vacant_o2)
      occupied_icu=int(tot_icu)-int(vacant_icu)
      occupied_vent=int(tot_vent)-int(vacant_vent)
      row=(date_str,tot_normal,tot_o2,tot_icu,tot_vent,occupied_normal,occupied_o2,occupied_icu,occupied_vent)
      print(city+':')
      print(row)
    elif city=='hp':
      x=os.popen('curl -k https://covidcapacity.hp.gov.in/index.php').read()
      soup=BeautifulSoup(x,'html.parser');
      xx=soup('a',attrs={'id':'oxygenbedmodel'})[0]
      tot_o2=int(xx.parent.parent('td')[0].text)
      occupied_o2=int(xx.parent.parent('td')[1].text)
      xx=soup('a',attrs={'id':'icubedmodel'})[0]
      tot_icu=int(xx.parent.parent('td')[0].text)
      occupied_icu=int(xx.parent.parent('td')[1].text)
      xx=soup('a',attrs={'id':'Standardbedmodel'})[0]
      tot_normal=int(xx.parent.parent('td')[0].text)
      occupied_normal=int(xx.parent.parent('td')[1].text)
      row=(date_str,tot_normal,tot_o2,tot_icu,occupied_normal,occupied_o2,occupied_icu)
      print(city+':');print(row)
    elif city=='mp':
      x=os.popen('curl -k http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-dashboard/').read()
      soup=BeautifulSoup(x,'html.parser');
      xx=soup('a',attrs={'href':'http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-details'})
      tot_normal,occupied_normal,vacant_normal,tot_o2,occupied_o2,vacant_o2,tot_icu,occupied_icu,vacant_icu=[i.text for i in xx if i.text.isnumeric()]
      row=(date_str,tot_normal,tot_o2,tot_icu,occupied_normal,occupied_o2,occupied_icu)
      print(city+':');print(row)
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
        a=open('data.chennai.csv','a');a.write(info+'\n');a.close()
        print('Appended to data.chennai.csv: '+info)        
    if city in ['mp','hp','pune']:
      csv_fname='data.'+city+'.csv'
      a=open(csv_fname);r=csv.reader(a);info=[i for i in r];a.close()
      dates=list(set([i[0] for i in info[1:]]));dates.sort()
      
      if date_str in dates: 
        # ~ dont_update_data_csv=True
        print('----------\n\nData for %s already exists in %s!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str,csv_fname))
      else:
        #write to file
        a=open(csv_fname,'a');w=csv.writer(a);w.writerow(row);a.close()
        print('Appended to %s :%s' %(csv_fname,str(row)))        
  
