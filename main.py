 # -*- coding: utf8 -*-
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import re
import os
import csv
import traceback
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys

from time import sleep
from bs4 import BeautifulSoup as bs

def create_driver(headless=True):
	print('create_driver()')
	chrome_options = webdriver.ChromeOptions()
	if headless:
		chrome_options.add_argument("--headless")
	chrome_options.add_argument("--log-level=3")
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36')
	chrome_options.add_argument('--disable-blink-features=AutomationControlled')
	#chrome_options.add_argument('--proxy-server='+proxy)

	chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
	chrome_options.add_experimental_option('useAutomationExtension', False)
	chrome_options.add_argument("--disable-blink-features")
	chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
	chrome_options.add_experimental_option("prefs", { 
	"profile.default_content_setting_values.media_stream_mic": 1, 
	"profile.default_content_setting_values.media_stream_camera": 1,
	"profile.default_content_setting_values.geolocation": 1, 
	"profile.default_content_setting_values.notifications": 1,
	"profile.default_content_settings.geolocation": 1,
	"profile.default_content_settings.popups": 0
  })
	
	caps = DesiredCapabilities().CHROME

	caps["pageLoadStrategy"] = "none"	
	
	driver = webdriver.Chrome(desired_capabilities=caps,chrome_options=chrome_options)	

	driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
 "source": """
	  const newProto = navigator.__proto__
	  delete newProto.webdriver
	  navigator.__proto__ = newProto		
	  """
})
	driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
		
	driver.implicitly_wait(10)

	params = {
	"latitude": 55.5815245,
	"longitude": 36.825144,
	"accuracy": 100
	}
	driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
	driver.refresh()
	
	return driver


def get_sites():
	with open('sites.txt','r',encoding='utf-8-sig') as file:
		return file.read().splitlines()

def sort_data():
	with open('not sort.txt','r',encoding='utf-8-sig') as file:
		data = file.read().splitlines()

	with open('sites.txt','a+',encoding='utf-8-sig') as file:
		for el in data:
			file.write(el.split()[0]+'\n')

def csv_pack(name,params,mode='a+'):	
	with open(name + '.csv',mode,newline='',encoding='utf-8-sig') as file:
		writer = csv.writer(file,delimiter=';')
		writer.writerow(params)


def check_if_news():
	sites = get_sites()
	driver = create_driver()

	for site in sites:
		try:
			if not 'https://' in site:
				site = 'https://'+site
			print(site)
			driver.get(site)
			sleep(2)
			for i in range(15):
				soup = bs(driver.page_source,'html.parser')
				links = len(soup.findAll('a'))

				all_dates = re.findall('2006|2007|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020|2021|2022|2023|2024',soup.text)
				dates = len(all_dates)

				if dates > 0:
					all_dates = list(filter(lambda x: x!='',all_dates))
					all_dates = list(map(lambda x: int(x),all_dates))
					
					last_date = str(max(all_dates))
				else:
					last_date = ''

				if_news_in_text = 'news' in soup.text.lower()
				
				print('Cайт',links,dates,if_news_in_text)
				
				if links > 5:
					sleep(2)
					print('Загружен')
					break
				sleep(1)

			csv_pack('result',[site,links,dates,if_news_in_text,last_date])
		except:
			traceback.print_exc()
			continue

#sort_data()
if not os.path.exists('result.csv'):
	csv_pack('result',['Сайт',"Кол-во ссылок","Кол-во дат","Если слово news в тексте","Последний указаный год"],'w')
check_if_news()
