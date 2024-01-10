import time
import requests 
import shutil 
import os
import re
from pathlib import Path
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException


VISUAL = False
MAIL = input("patreon account mail")
MDP = input("patreon account password")
CREATOR = input("patreon creator you wanna download (name in url)")


def load_more(_driver):         ###try to click the "load more" return true if succesful, fals if no button is find
    try:
        element = _driver.find_element(By.XPATH, "//div[@data-tag='post-stream-container']//button[@class='sc-pVTFL coHwNo']")          ###find button "load more"
    except (NoSuchElementException, StaleElementReferenceException) :           ###  if element not find, mean that no more post to loads
        return False
        
    while True :
        time.sleep(1)        
        try:
            element.click()
        except ElementClickInterceptedException :       ### retry if element is non clickable bc the site hasn't loaded
            pass
        finally:
            break
        
    return True 


driver = webdriver.Chrome()
driver.set_window_position(2900, 100)
driver.set_window_size(900, 900) 
driver.get('https://www.patreon.com/login')
driver.implicitly_wait(5)


element = driver.find_element(By.XPATH, "//input[@type='email']")
element.send_keys(MAIL, Keys.ENTER)                                             ###enter mail

element = driver.find_element(By.XPATH, "//input[@type='password']")
element.send_keys(MDP, Keys.ENTER)                                              ###enter password

time.sleep(5) 

driver.get('https://www.patreon.com/apple_nettle/posts')        ###go to creator page

try:
   os.mkdir(str(Path.home() / "Downloads")+"//apple_nettle")
except Exception as ex:
    print("emergency",type(ex), ex.args)

while load_more(driver):       ###load all poste
    pass

postes=[]
elements = driver.find_elements(By.XPATH, "//div[@data-tag='post-stream-container']//ul[@class='sc-cVAmsi sc-zkptco-2 bdNeqr kRZjh']//li")          ###find all post

for el in elements: 
    post_title = el.find_element(By.XPATH, ".//span[@data-tag='post-title']//a").text 
    post_time = el.find_element(By.XPATH, ".//a[@data-tag='post-published-at']").text 
    
    post_title = re.sub(r'[<>:"\\/|?*]', ' ',post_title)    ### remove forbiden character   
    
    post_time_cut = post_time.split()
    if int(post_time_cut[1]) < 10:
        post_time_cut[1] = post_time_cut[1][:-1]
        post_time_cut[0] = post_time_cut[0][:3]
        post_time_cut[3] = post_time_cut[0][:4]
        post_time = post_time_cut[0] + " 0" + str(int(post_time_cut[1])) + ", " + post_time_cut[2]   ### make sur to have same lengt time everytime
    
    path = str(Path.home() / "Downloads") + "//apple_nettle//" + "(" + post_time + ")" + post_title  
    
    try:
        os.mkdir(path)          ### creat the creator directory
    except Exception as ex:
        print("emergency",type(ex), ex.args)    
    
    try:
        nb_image = (int)(el.find_element(By.XPATH, ".//div[@data-tag='chip-container']//span").text)            ###get the numer of image in the slideshow
    except:
        nb_image = 1
    
    el.find_element(By.XPATH, ".//img").click()
    
    for i in range(nb_image):           ###get the image in each post slideshow
        
        url = driver.find_element(By.XPATH, "//div[@data-target='lightbox-content']//img").get_attribute("src")
        
        if VISUAL :             ### if visual wanted, show each image being downloaded 
            original_window = driver.current_window_handle
            driver.switch_to.new_window('tab')
            driver.get(url)        
        
        res = requests.get(url, stream = True)          #download the image
        
        with open( ( path + "//" + (str)(i) + ".png"),'wb') as f:
            shutil.copyfileobj(res.raw, f)
            
        if VISUAL :             ### if visual wanted, show each image being downloaded 
            driver.close()
            driver.switch_to.window(original_window)       
        
        if nb_image > 1:
            driver.find_element(By.XPATH, "//button[@data-tag='nextImage']").click()            ###if more than one image int the slideshow, scol between them
         
    driver.find_element(By.XPATH, "//button[@data-tag='close']").click()    
    
    
    postes.append({'title': post_title, 'timee': post_time, 'number':nb_image})
    
print(*postes, sep='\n')

