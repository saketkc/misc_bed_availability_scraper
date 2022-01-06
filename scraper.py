from selenium import webdriver;
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from tabula import read_pdf


import os,requests,time,bs4,datetime,csv;
from PIL import Image
import json,time
from bs4 import BeautifulSoup

# ~ global_proxy='socks4://157.119.201.231:1080'
# ~ global_proxy='socks4://103.88.221.194:46450'
global_proxy='socks4://49.206.195.204:5678'

def tamil_nadu_bulletin_parser(bulletin='',return_page_range=False,clip_bulletin=False,return_date=False,dump_clippings=False,return_beds_page=False,return_district_tpr_page=False):
  cmd='pdftotext  -layout "'+bulletin+'" tmp.txt';os.system(cmd)
  # ~ b=[i for i in open('tmp.txt').readlines() if i]
  b=[i for i in open('tmp.txt',encoding='utf-8',errors='ignore').readlines() if i]
  idx=0;page_count=1;page_range=[];got_start=False
  bulletin_date=''
  bd=[i for i in b if 'edia bulletin' in i.lower()]
  bulletin_date_string='';bulletin_date=''
  if bd:
    bulletin_date=bd[0].split('lletin')[1].strip().replace('-','.').replace('/','.')
    bulletin_date_string=bulletin_date
    bulletin_date=datetime.datetime.strptime(bulletin_date,'%d.%m.%Y')
  if return_date: return bulletin_date
    
  for i in b:
    if '\x0c' in i: page_count+=1    
    if return_beds_page and ('BED VACANCY DETAILS'.lower() in i.lower()) : return page_count
    
def tamil_nadu_parse_hospitalizations(bulletin='',use_converted_txt=False,verbose=False):
  date_str=tamil_nadu_bulletin_parser(bulletin,return_date=True).strftime('%Y-%m-%d')
  beds_page=tamil_nadu_bulletin_parser(bulletin,return_beds_page=True)   
  if not use_converted_txt:       
    #hospitalization page
    os.system('pdftotext -layout -f %d -l %d %s tmp.txt' %(beds_page,beds_page,bulletin))
    b=[i.strip() for i in open('tmp.txt').readlines() if i.strip()]
  else: #if forcing, use tmp2.txt
    b=[i.strip() for i in open('tmp2.txt').readlines() if i.strip()]
  start_idx=[i for i in range(len(b)) if 'Ariyalur' in b[i]][0]
  end_idx=[i for i in range(len(b)) if 'Virudhunagar' in b[i]][0]
  bb=b[start_idx:end_idx+2][:-1]
  last_line=[i for i in range(len(b)) if 'grand' in b[i].lower() and 'total' in b[i].lower()][0]
  if len(b[last_line].split())>3: last_line=b[last_line]
  else: last_line='Grand Total '+b[last_line+1]
  data={}
  for i in bb:
    try:
      district,tot_o2,tot_nono2,tot_icu,occ_o2,occ_nono2,occ_icu,vac_o2,vac_nono2,vac_icu,vac_net=i.split()[1:]
    except:
      print('unable to parse hosp page details for line: '+i+'in bulletin: '+bulletin+'\nRreutnring')
      return (i,bb)
    data[district]=[tot_o2,tot_nono2,tot_icu,occ_o2,occ_nono2,occ_icu]
  tot_o2,tot_nono2,tot_icu,occ_o2,occ_nono2,occ_icu,vac_o2,vac_nono2,vac_icu,vac_net=last_line.split()[2:]
  data['All']=[tot_o2,tot_nono2,tot_icu,occ_o2,occ_nono2,occ_icu]
  # ~ if verbose: pprint.pprint(data)
  #CCC page
  os.system('pdftotext -layout -f %d -l %d %s tmp.txt' %(beds_page+1,beds_page+1,bulletin))
  b=[i.strip() for i in open('tmp.txt').readlines() if i.strip()]
  start_idx=[i for i in range(len(b)) if 'Ariyalur' in b[i]][0]
  end_idx=[i for i in range(len(b)) if 'Virudhunagar' in b[i]][0]
  bb=b[start_idx:end_idx+2][:-1]
  last_line=[i for i in range(len(b)) if 'grand' in b[i].lower() and 'total' in b[i].lower()][0]
  if len(b[last_line].split())>4: last_line=b[last_line];
  else: last_line='Grand Total '+b[last_line+1]
  for i in bb:
    district,tot_ccc,occ_ccc,vac_ccc=i.split()[1:]
    data[district].extend([tot_ccc,occ_ccc])
  # ~ print(last_line)
  tot_ccc,occ_ccc,vac_ccc=last_line.split()[2:]
  data['All'].extend([tot_ccc,occ_ccc])
  if verbose: pprint.pprint(data)
  data2=[]
  for district in data:
    if not district=='All':
      x=data[district]
      data2.append([date_str,district,x[0],x[1],x[2],x[6],x[3],x[4],x[5],x[7]])
  x=data['All'];data2.append([date_str,'All',x[0],x[1],x[2],x[6],x[3],x[4],x[5],x[7]])
  a=open('hosp.csv','a')
  w=csv.writer(a)
  for i in data2: w.writerow(i)
  a.close()
  return (data2,date_str)
  
def tamil_nadu_auto_parse_latest_bulletin():
  print('Downloading TN bulletin portal webpage')
  x=os.popen('curl -# -k https://stopcorona.tn.gov.in/daily-bulletin/').read()
  soup=BeautifulSoup(x,'html.parser');  x=soup('div',attrs={'class':'information'})
  if not x:    print('could not find information div in TN bulletin portal!!');    return
  latest_bulletin_url=x[0]('li')[0]('a')[0]['href'].replace('http://','https://')
  cmd='wget --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "'+latest_bulletin_url+'"'
  print(cmd);os.system(cmd)
  pdf=[i for i in os.listdir('.') if i.endswith('.pdf')];
  if pdf: pdf=pdf[0]
  data,bulletin_date=tamil_nadu_parse_hospitalizations(pdf)
  #check if data for date already exists in csv. if not, then add
  a=open('tamil_nadu.csv');r=csv.reader(a);info=[i for i in r];a.close()
  dates=list(set([i[0] for i in info[1:] if len(i)>0]));dates.sort()
  if bulletin_date not in dates:  os.system('cat hosp.csv >> tamil_nadu.csv && rm -v hosp.csv '+pdf)
  else: print('data for '+bulletin_date+' already existed in tamil_nadu.csv. Only printing, not writing');[print(i) for i in data]
 
def gurugram_bulletin_parser(bulletin=''):
  os.system('pdftotext -layout "'+bulletin+'" t.txt')
  b=[i.strip() for i in open('t.txt').readlines() if i.strip()]
 
  x=[i for i in b if 'Dated' in i]
  if not x: print('could not get date in '+bulletin);return  
  x=x[0].split('Dated')[-1].strip().split()[-1]
  x=x.replace('-','/').replace('/04/10/2021','04/10/2021')
  date=datetime.datetime.strptime(x,'%d/%m/%Y').strftime('%Y-%m-%d')

 
  x=[i for i in b if 'found Negative' in i]
  x2=[i for i in b if 'found Positive' in i]
  if not x: print('could not get tests in '+bulletin);return
  tot_tests_to_date=int(x[0].split()[-1].strip())+int(x2[0].split()[-1].strip())
 
  x=[i for i in b if 'New Cases' in i]
  if not x: print('could not get new cases in '+bulletin);return
  cases=int(x[0].split()[-1].strip())
  
  # ~ tpr='%.2f' %(100*(float(cases)/tests));tpr=float(tpr)
  
  x=[i for i in b if '(DCH )' in i]
  if not x: #some 2021 bulletins report combined value
    x=[i for i in b if '(DCH +DCHC)' in i]
    if not x: print('could not get DHC occupancy in '+bulletin);return
    dhc_dchc_occupied=int(x[0].split()[-1].strip())
  else:
    dhc_dchc_occupied=int(x[0].split()[-1].strip())  
    x=[i for i in b if '(DCHC)' in i]
    if not x: print('could not get DCHC occupancy in '+bulletin);return
    # ~ dchc_occupied=int(x[0].split()[-1].strip())
    dhc_dchc_occupied+=int(x[0].split()[-1].strip())
  
  x=[i for i in b if '(DCCC)' in i]
  if not x: print('could not get DCCC occupancy in '+bulletin);return
  dccc_occupied=int(x[0].split()[-1].strip())
  
  x=[i for i in b if 'Home Isolation' in i]
  if not x: print('could not get Home isolation numbers in '+bulletin);return
  home_isolation=int(x[0].split()[-1].strip())
  
  # ~ return (date,cases,tot_tests_to_date,dhc_occupied,dchc_occupied,dccc_occupied,home_isolation)
  return (date,cases,tot_tests_to_date,dhc_dchc_occupied,dccc_occupied,home_isolation)
  
def gurugram_auto_parse_latest_bulletin():
  print('Downloading gurugram bulletin portal webpage')
  x=os.popen('curl -# -k https://gurugram.gov.in/health-bulletin/').read()
  soup=BeautifulSoup(x,'html.parser');x=soup('div',attrs={'class':'status-publish'})
  if not len(x)>0: print('cold not find div from gurugram bulletin portal!!');return
  latest_bulletin_url=x[0]('li')[0]('a')[0]['href']
  cmd='wget --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "'+latest_bulletin_url+'"'
  print(cmd);os.system(cmd)
  pdf=[i for i in os.listdir('.') if i.endswith('.pdf')];
  if pdf: pdf=pdf[0]
  row=gurugram_bulletin_parser(pdf);bulletin_date=row[0]
  
  #check if data for date already exists in csv. if not, then add
  a=open('gurugram.csv');r=csv.reader(a);info=[i for i in r];a.close()
  dates=list(set([i[0] for i in info[1:] if len(i)>0]));dates.sort()
  if bulletin_date not in dates:  a=open('gurugram.csv','a');w=csv.writer(a);w.writerow(row);a.close()
  else: print('data for '+bulletin_date+' already existed in gurugram.csv. Only printing, not writing');print(row)
  os.system('rm -v "'+pdf+'"')

def mumbai_bulletin_auto_parser(bulletin='',proxy=global_proxy):  
  if not bulletin: #download latest bulletin
    # ~ cmd='wget --no-check-certificate --user-agent "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "https://stopcoronavirus.mcgm.gov.in/assets/docs/Dashboard.pdf"'
    cmd='curl -# --max-time 30  -O -# -k -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "https://stopcoronavirus.mcgm.gov.in/assets/docs/Dashboard.pdf"'
    print(cmd);os.system(cmd)
    if os.path.exists('Dashboard.pdf'): bulletin='Dashboard.pdf'
 
  max_tries=100;tries=0
  if os.path.exists(bulletin): 
    print('todays bulletin already exists.nothing to download')
  else:
    while (not os.path.exists(bulletin)) and (tries<max_tries):    
      cmd='curl -#  -O  -k -x "'+proxy+'" "https://stopcoronavirus.mcgm.gov.in/assets/docs/Dashboard.pdf"'
      print(cmd);    os.system(cmd)
      if os.path.exists('Dashboard.pdf'): bulletin='Dashboard.pdf' #download through proxy worked

      os.system('ls -a *.pdf')
      tries+=1
    if os.path.exists('Dashboard.pdf'): bulletin='Dashboard.pdf' #download through proxy worked
      
  #get date
  cmd='pdftotext -x 10 -y 150 -W 200 -H 200 -layout -f 1 -l 1  "'+bulletin+'" t.txt';os.system(cmd)
  b=[i.strip().replace(',','') for i in open('t.txt').readlines() if i.strip()]

  date=[i.replace(',','') for i in b if '2021' in i or '2022' in i]
  if not date: print('could not get date from '+bulletin)
  else: date=datetime.datetime.strptime(date[0],'%b %d %Y');date_str=date.strftime('%Y-%m-%d')
  
  #get cases,tests,symp etc
  cmd='pdftotext -x 0 -y 100 -W 220 -H 320 -layout -f 2 -l 2 "'+bulletin+'" t.txt';os.system(cmd)
  b=[i.strip().replace(',','') for i in open('t.txt').readlines() if i.strip()]
  
  cases=[i for i in b if 'positive' in i.lower()]
  if not cases: print('could not get cases from '+bulletin)
  else: cases=int(cases[0].split()[-1].strip())
  
  active=[i for i in b if 'active' in i.lower()]
  if not active: print('could not get actives from '+bulletin)
  else: active=int(active[0].split()[-1].strip())
  
  asymp=[i for i in b if 'Asymptomatic' in i]
  if not asymp: print('could not get asymp from '+bulletin)
  else: asymp=int(asymp[0].split()[-1].strip())
  
  symp=[i for i in b if 'Symptomatic' in i]
  if not symp: print('could not get symp from '+bulletin)
  else: symp=int(symp[0].split()[-1].strip())
  
  critical=[i for i in b if 'critical' in i.lower()]
  if not critical: print('could not get criticals from '+bulletin)
  else: critical=int(critical[0].split()[-1].strip())
  
  tests=[i for i in b if 'tests' in i.lower()]
  if not tests: print('could not get tests from '+bulletin)
  else: tests=int(tests[0].split()[-1].strip())
  
  #get hospital occupancy
  cmd='pdftotext -x 340 -y 100 -W 95 -H 340 -layout -f 2 -l 2 "'+bulletin+'" t.txt';os.system(cmd)
  b=[i.strip().replace(',','') for i in open('t.txt').readlines() if i.strip()]
  
  if not ('2021' in b[0] or '2022' in b[0]): #means date wasn't at top, parsed wrong
    print('could not parse occupancy numbers')
  else:
    try:
      bc,bo,ba,dc,do,da,oc,oo,oa,ic,io,ia,vc,vo,va=b[1:]
    except:
      print('failed to get occupancy split')
      return b
    gen_beds_cap=int(bc);gen_beds_occupancy=int(bo)
    o2_cap=int(oc);o2_occupancy=int(oo)
    icu_cap=int(ic);icu_occupancy=int(io)
    vent_cap=int(vc);vent_occupancy=int(vo)
 
  row=(date_str,cases,tests,o2_cap,icu_cap,vent_cap,o2_occupancy,icu_occupancy,vent_occupancy,gen_beds_cap,gen_beds_occupancy,active,symp,asymp,critical)
  # ~ a=open('tmp.csv','a');w=csv.writer(a);w.writerow(row);a.close()
  
   #check if data for date already exists in csv. if not, then add
  a=open('mumbai.csv');r=csv.reader(a);info=[i for i in r];a.close()
  dates=list(set([i[0] for i in info[1:] if len(i)>0]));dates.sort()
  print('Mumbai data:')
  if date_str not in dates:  a=open('mumbai.csv','a');w=csv.writer(a);w.writerow(row);a.close()
  else: print('data for '+date_str+' already existed in mumbai.csv. Only printing, not writing');
  print(row)
  
  os.system('rm -v "'+bulletin+'"')
  # ~ return b
  return row

if __name__=='__main__':
  
  date=datetime.datetime.now();date_str=date.strftime('%Y-%m-%d')
  
  for city in ['bengaluru','hp','mp','chennai','pune','delhi','gbn','gurugram','tn','mumbai','chandigarh','uttarakhand','kerala','ap','telangana']:
  # ~ for city in ['bengaluru']:
    print('running scraper for: '+city)
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
      #get date from bulletin
      os.system('pdftotext -layout -f 1 -l 1 BLR_'+str(date_str)+'.pdf t.txt')
      b=[i.strip() for i in open('t.txt').readlines() if i.strip()]
      date_line=[i for i in b if 'WAR ROOM'.lower() in i.lower()]
      if not date_line: print('could not get date from bengaluru buletin BLR_'+str(date_str)+'.pdf !!');sys.exit(1)
      bulletin_date=datetime.datetime.strptime(date_line[0].split('/')[-2].strip(),'%d.%m.%Y').strftime('%Y-%m-%d')
  
      # print(text)
      tables = read_pdf("BLR_"+str(date_str)+".pdf", pages=12,silent=True)
      df=tables[0]
      
      results=[]
      results.append(df.iloc[14][-2].split())
      results.append(df.iloc[14][-3].split())
      # ~ print(results)

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
      
      info=', '.join((bulletin_date,str(general_available),str(general_admitted),str(hdu_available),str(hdu_admitted),str(icu_available),str(icu_admitted),str(ventilator_available),str(ventilator_admitted)))        
      
      os.system('rm -v BLR_'+str(date_str)+'.pdf')
      if bulletin_date in dates: 
        # ~ dont_update_data_csv=True
        print('----------\n\nData for %s already exists in data.bengaluru.csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
        print('bengaluru: '+str(info))
      else:
        #write to file
        
        a=open('data.bengaluru.csv','a');a.write(info+'\n');a.close()
        print('Appended to data.bengaluru.csv: '+info) 
        
    # ~ if city=='bengaluru':
      # ~ #BENGALURU
      # ~ options=webdriver.ChromeOptions();
      # ~ options.add_argument('--ignore-certificate-errors');
      # ~ options.add_argument('--disable-gpu');
      # ~ options.add_argument("--headless")
      # ~ options.add_argument("--window-size=1366,768")
      # ~ driver=webdriver.Chrome(chrome_options=options)  
      # ~ driver.get('https://apps.bbmpgov.in/Covid19/en/bedstatus.php')
      # ~ driver.get('https://www.powerbi.com/view?r=eyJrIjoiOTcyM2JkNTQtYzA5ZS00MWI4LWIxN2UtZjY1NjFhYmFjZDBjIiwidCI6ImQ1ZmE3M2I0LTE1MzgtNGRjZi1hZGIwLTA3NGEzNzg4MmRkNiJ9')
      # ~ driver.get('20.186.65.100/view?r=eyJrIjoiOTcyM2JkNTQtYzA5ZS00MWI4LWIxN2UtZjY1NjFhYmFjZDBjIiwidCI6ImQ1ZmE3M2I0LTE1MzgtNGRjZi1hZGIwLTA3NGEzNzg4MmRkNiJ9')
      # ~ time.sleep(10)
      # ~ date=datetime.datetime.now();date_str=date.strftime('%d_%m_%Y')
      # ~ if not os.path.exists('images/'+date_str+'.png'):
        # ~ driver.save_screenshot('images/'+date_str+'.png')
        # ~ img=Image.open('images/'+date_str+'.png')
        # ~ img.save('images/'+date_str+'.webp')
        # ~ print('saved screenshot of bengaluru beds availability dashboard to %s' %('images/'+date_str+'.webp'))
      # ~ else:
        # ~ print('Image: %s already existed. Skipping!!' %('images/'+date_str+'.png'))
    elif city=='tn':
      tamil_nadu_auto_parse_latest_bulletin()
    elif city=='gurugram':
      gurugram_auto_parse_latest_bulletin()
    elif city=='mumbai':
      mumbai_bulletin_auto_parser()
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
            print('----------\n\nData for %s already exists in data.delhi.csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
      
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
      x=os.popen('curl -# -k https://divcommpunecovid.com/ccsbeddashboard/hsr').read()      
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
    elif city=='ap':
      br=webdriver.PhantomJS();br.get('http://dashboard.covid19.ap.gov.in/ims/hospbed_reports//');time.sleep(3)
      x=br.page_source;      soup=BeautifulSoup(x,'html.parser');
      xyz,number_of_hospitals,tot_icu,occupied_icu,vacant_icu,tot_o2,occupied_o2,vacant_o2,tot_normal,occupied_normal,vacant_normal,tot_vent,occupied_vent,vacant_vent,=[i.text for i in soup('tr')[-1]('td')]
      row=(date_str,tot_normal,tot_o2,tot_icu,tot_vent,occupied_normal,occupied_o2,occupied_icu,occupied_vent)
      print(city+':')
      print(row)
    elif city=='telangana':
      x=os.popen('curl -# -k http://164.100.112.24/SpringMVC/Hospital_Beds_Statistic_Bulletin_citizen.htm').read()
      soup=BeautifulSoup(x,'html.parser')
      try:
        xyz,tot_normal,occupied_normal,vacant_normal,tot_o2,occupied_o2,vacant_o2,tot_icu,occupied_icu,vacant_icu,a1,a2,a3=[i.text for i in soup('tr')[-1]('th')]
      except:
        print('could not unpack '+str([i.text for i in soup('tr')[-1]('th')]))
      row=(date_str,tot_normal,tot_o2,tot_icu,occupied_normal,occupied_o2,occupied_icu)
      print(city+':')
      print(row)
    elif city=='kerala':
      x=os.popen('curl -# -k https://covid19jagratha.kerala.nic.in/home/addHospitalDashBoard').read()
      soup=BeautifulSoup(x,'html.parser');
      
      n=soup('div',attrs={'class':'box'})[1]
      occupied_normal,tot_normal=n('p')[0].text.replace(n('label')[0].text,'').strip().split('/')
      
      n=soup('div',attrs={'class':'box'})[2]
      occupied_icu,tot_icu=n('p')[0].text.replace(n('label')[0].text,'').strip().split('/')
      
      n=soup('div',attrs={'class':'box'})[3]
      occupied_vent,tot_vent=n('p')[0].text.replace(n('label')[0].text,'').strip().split('/')
      
      n=soup('div',attrs={'class':'box'})[4]
      occupied_o2,tot_o2=n('p')[0].text.replace(n('label')[0].text,'').strip().split('/')
      row=(date_str,tot_normal,tot_o2,tot_icu,tot_vent,occupied_normal,occupied_o2,occupied_icu,occupied_vent)
      print(city+':')
      print(row)
      
    elif city=='uttarakhand':
      x=os.popen('curl -# -k https://covid19.uk.gov.in/bedssummary.aspx').read()
      soup=BeautifulSoup(x,'html.parser');
      
      n=soup('div',attrs={'id':'ContentPlaceHolder1_divIsolation'})[0]
      xz1,tot_normal,xz2,vacant_normal=[i.text for i in n('span')];
      occupied_normal=int(tot_normal)-int(vacant_normal)
      
      n=soup('div',attrs={'id':'ContentPlaceHolder1_divOx2'})[0]
      xz1,tot_o2,xz2,vacant_o2=[i.text for i in n('span')];
      occupied_o2=int(tot_o2)-int(vacant_o2)
      
      n=soup('div',attrs={'id':'ContentPlaceHolder1_divICU'})[0]
      xz1,tot_icu,xz2,vacant_icu=[i.text for i in n('span')];
      occupied_icu=int(tot_icu)-int(vacant_icu)
      
      n=soup('div',attrs={'id':'ContentPlaceHolder1_div1'})[0]
      xz1,tot_vent,xz2,vacant_vent=[i.text for i in n('span')];
      occupied_vent=int(tot_vent)-int(vacant_vent)
      
      row=(date_str,tot_normal,tot_o2,tot_icu,tot_vent,occupied_normal,occupied_o2,occupied_icu,occupied_vent)
      print(city+':')
      print(row)
      
    elif city=='chandigarh':
      x=os.popen('curl -# -k http://chdcovid19.in/chdcovidbed19/index.php/home/stats').read()
      soup=BeautifulSoup(x,'html.parser');
      table=soup('table')[0]
      
      # ~ toc=tvc=tic=tnc=0
      # ~ too=tvo=tio=tno=0
      # ~ for row in table('tr')[2:]:
        # ~ hospital_name,hosp_type,updated_on,oc,oa,ov,nc,no,nv,ic,io,iv,vc,vo,vv=[i.text for i in  row('td')]
        # ~ toc+=int(oc);        tvc+=int(vc);        tic+=int(ic);        tnc+=int(nc)
        # ~ too+=int(oo);        tvo+=int(vo);        tio+=int(io);        tno+=int(no)
      
      try: xyz,toc,too,toa,tnc,tno,tna,tic,tio,tia,tvc,tvo,tva=[i.text for i in  table('tr')[-1]('td')]
      except:
        print('could not unpack chandigarh values!\n'+str(table('tr')[-1]('td')))
      row=(date_str,tnc,toc,tic,tvc,tno,too,tio,tvo)
      print(city+' : '+str(row))
    elif city=='hp':
      x=os.popen('curl -# -k https://covidcapacity.hp.gov.in/index.php').read()
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
      x=os.popen('curl -# -k http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-dashboard/').read()
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
        print('----------\n\nData for %s already exists in data.chennai.csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
      else:
        #write to file
        info=', '.join((date_str,str(tot_o2_beds),str(tot_non_o2_beds),str(tot_icu_beds),str(occupied_o2_beds),str(occupied_non_o2_beds),str(occupied_icu_beds)))        
        a=open('data.chennai.csv','a');a.write(info+'\n');a.close()
        print('Appended to data.chennai.csv: '+info)        
    
    #generic writer for most cities
    if city in ['mp','hp','pune','chandigarh','uttarakhand','kerala','ap','telangana']:
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
  
