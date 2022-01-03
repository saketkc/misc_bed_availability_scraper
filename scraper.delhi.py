import requests,json,datetime,csv

if __name__=='__main__':
  date=datetime.datetime.now();
  # ~ date_str=date.strftime('%d/%m/%Y')
  date_str=date.strftime('%Y-%m-%d')
 
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
    #write to file
    a=open('data.delhi.csv','a')
    if not dont_update_data_csv:
      a.write(info+'\n')
    print(info)
    a.close()
  else:
    print('could not get data from https://coronabeds.jantasamvad.org/covid-info.js')

