import requests,json,datetime,csv

if __name__=='__main__':
  date=datetime.datetime.now();
  # ~ date_str=date.strftime('%d/%m/%Y')
  date_str=date.strftime('%Y-%m-%d')
 
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
  print('api call status code: ', resp.status_code)
  
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
    print(info)
    a.close()
  else:
    print('could not get data from https://api.gbncovidtracker.in/hospitals')
