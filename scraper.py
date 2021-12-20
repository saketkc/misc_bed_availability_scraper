from selenium import webdriver;
import os,requests,time,bs4,datetime,csv
from PIL import Image


if __name__=='__main__':
  options = webdriver.ChromeOptions();
  options.add_argument('--ignore-certificate-errors');
  options.add_argument("--headless")
  options.add_argument("--window-size=1366,768")
  driver = webdriver.Chrome(chrome_options=options)  
  driver.get('https://apps.bbmpgov.in/Covid19/en/bedstatus.php')
  time.sleep(10)
  date=datetime.datetime.now();date_str=date.strftime('%d_%m_%Y')
  if not os.path.exists('images/'+date_str+'.png'):
    driver.save_screenshot('images/'+date_str+'.png')
    img=Image.open('images/'+date_str+'.png')
    img.save('images/'+date_str+'.webp')
    print('saved screenshot of bengaluru beds availability dashboard to %s' %('images/'+date_str+'.webp'))
  else:
    print('Image: %s already existed. Skipping!!' %('images/'+date_str+'.png'))
  # ~ driver.find_element_by_xpath('//a[@href="#state-data"]').click()
  # ~ time.sleep(3)
  # ~ htm=driver.page_source
  # ~ a=open('test.html','w');a.write(htm);a.close()
  
  # ~ #parse html file
  # ~ soup=bs4.BeautifulSoup(htm,'html.parser')
  # ~ t=soup('tbody')
  
  # ~ date=datetime.datetime.now();date_str=date.strftime('%d/%m/%Y')
  
  # ~ #check if data for given date already exists in csv. Update only if data doesn't exist
  # ~ a=open('data.csv');r=csv.reader(a);info=[i for i in r];a.close()
  # ~ dates=list(set([i[1] for i in info[1:]]));dates.sort()
  
  # ~ dont_update_data_csv=False
  # ~ if date_str in dates: 
    # ~ dont_update_data_csv=True
    # ~ print('----------\n\nData for %s already exists in csv!!\nOnly printing, not modifying csv!!\n\n----------\n\n' %(date_str))
  
  # ~ #actually parse the mohfw htm
  # ~ if t: 
    # ~ t=t[0]
    # ~ chunks=[];states=[i.lower() for i in list(state_code_to_name.values())]
    # ~ state_data={}
    
    
    # ~ a=open('data.csv','a')
    # ~ for idx in range(36):
      # ~ chunk=t('td')[8*idx:8*(idx+1)]
      # ~ state_name=chunk[1].text.strip()
      # ~ state_active=int(chunk[2].text.strip())
      # ~ state_recovered=int(chunk[4].text.strip())
      # ~ state_deaths=int(chunk[6].text.strip())
      # ~ state_cases=state_active+state_recovered+state_deaths
      # ~ info='%s,%s,%d,%d,%d,%d' %(state_name,date_str,state_cases,state_recovered,state_active,state_deaths)
      # ~ if not dont_update_data_csv:
        # ~ a.write(info+'\n' )
      # ~ print(info)
    # ~ a.close()
  # ~ else: 
    # ~ print('Could not find element containing state-wise cases data!!')
    
  
  # ~ url = 'https://transfer.sh/'
  # ~ file = {'{}'.format('test.html'): open('test.html', 'rb')}
  # ~ response = requests.post(url, files=file)
  # ~ download_link = response.content.decode('utf-8')
  # ~ print('link to test.html',download_link)
  
