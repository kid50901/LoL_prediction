from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import urllib
import urllib.request
from urllib.request import urlopen
import pandas as pd
import numpy as np 
import sys
import json
import logging
from datetime import datetime
current_time = datetime.now()
formatted_time = current_time.strftime("%Y_%m_%d_%H%M%S")
logging.basicConfig(filename='.\log\debug_{}.log'.format(formatted_time), level=logging.DEBUG)

def soupToList(soup,trReduce,tdReduce):
    table=soup.find_all("tr")
    datai=[]
    for i in range(len(table)+trReduce):
        dataj=[]
        for j in range(len(table[i-trReduce].find_all("td"))+tdReduce):
            dataj.append((table[i-trReduce].find_all("td"))[j-tdReduce].getText())
        datai.append(dataj)
    return datai
def get_Tournaments_link(season_button_ID): 
    driver_path = 'C:\chromedriver-win64\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driver_path)
    url = "https://gol.gg/tournament/list/"
    driver.get(url)
    # 這裡可能需要等待頁面載入完成
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "result_tab")))
    button = driver.find_element(By.ID, season_button_ID)
    button.click()

    # 再次等待頁面載入完成
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "result_tab")))

    # 取得新頁面的 HTML 內容
    new_page_html = driver.page_source
    soup = BeautifulSoup(new_page_html, 'html.parser')
    driver.quit()
    
    result_tab=soup.find('div', id='result_tab')
    result_tab_td=result_tab.find_all('td')
    #result_tab_td[1].find('a')['href']
    Tournaments_list = []
    for i in range(len(result_tab_td)):
        try:
            x=result_tab_td[i].find('a')['href']
            #print(x)
            Tournaments_url='https://gol.gg/tournament/tournament-matchlist/{}'.format(x[19:])
            Tournaments_list.append(Tournaments_url)
            logging.info("[get_Tournameinfo] Tournament URL = {}".format(Tournaments_url))
        except:
            pass
    return Tournaments_list

def get_Tournaments_allLink(season_button_ID_list): #輸入賽季ID>取得該賽季所有比賽資訊連結
    Tournaments_allList=[]
    for i in range(len(season_button_ID_list)):
        logging.info("[get_Tournameinfo] season ID = {}".format(season_button_ID_list[i]))
        Tournaments_allList = Tournaments_allList + get_Tournaments_link(season_button_ID_list[i])
    return Tournaments_allList
#def get_gamelist1Tournament(TournamentURL):
    #driver_path = 'C:\chromedriver-win64\chromedriver.exe'
    #driver = webdriver.Chrome(executable_path=driver_path) # 請提供您的 ChromeDriver 路徑
    #driver.get(TournamentURL)

    #text_to_wait_for = "Worlds Main Event 2023  "
    #element_locator = (By.XPATH, f"//*[contains(text(), '{text_to_wait_for}')]")
    #try:
        #element = WebDriverWait(driver, 10).until(
            #EC.text_to_be_present_in_element(element_locator, text_to_wait_for)
        #)
        #print(f"Element with text '{text_to_wait_for}' is present on the page.")
        # 在这里可以进一步操作该元素
    #except :
        #print(f"Timed out waiting for element with text '{text_to_wait_for}' to appear on the page")

    #new_page_html1 = driver.page_source

    # 使用 Beautiful Soup 解析新頁面的內容
    #gamelist1page_soup = BeautifulSoup(new_page_html1, 'html.parser')
    #gamelist1page_td=gamelist1page_soup.find_all('td')
    #gamelist1page_soup = BeautifulSoup(new_page_html1, 'html.parser')
    #gamelist1page_td=gamelist1page_soup.find_all('td')

    #gamelist1page_lst=[]
    #for i in range(len(gamelist1page_td)):
        #try:
            #y = gamelist1page_td[i].find('a')['href']
            #numbers = re.findall(r'\d+', y)
            #gamelist1page_lst.append(numbers[0])
        #except:
            #pass
    
    #return gamelist1page_lst

def get_gamelist1Tournament(TournamentURL):
    logging.info("[get game ID] Find all ID in this Tournament URL {}".format(TournamentURL))
    driver_path = 'C:\chromedriver-win64\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driver_path) # 請提供您的 ChromeDriver 路徑
    driver.get(TournamentURL)

    text_to_wait_for = "Tournament data"
    element_locator = (By.XPATH, f"//*[contains(text(), '{text_to_wait_for}')]")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element(element_locator, text_to_wait_for)
        )
        print(f"Element with text '{text_to_wait_for}' is present on the page.")
        # 在这里可以进一步操作该元素
    except :
        print(f"Timed out waiting for element with text '{text_to_wait_for}' to appear on the page")

    new_page_html1 = driver.page_source

    # 使用 Beautiful Soup 解析新頁面的內容
    gamelist1page_soup = BeautifulSoup(new_page_html1, 'html.parser')
    table=gamelist1page_soup.find_all("tr")
    game_ID_list=[]
    game_patch_list=[]
    game_date_list=[]
    
    for i in range(len(table)-1):
        try:
            y = (table[i+1].find_all("td"))[0].find('a')['href']
            numbers = re.findall(r'\d+', y)
            game_ID_list.append(numbers[0])

            game_patch= (table[i+1].find_all("td"))[5].getText()
            game_patch_list.append(game_patch)

            game_date=(table[i+1].find_all("td"))[6].getText()
            game_date_list.append(game_date)

            game_qty_str = (table[i+1].find_all("td"))[2].getText()
            #print(game_qty_str)
            game_qty = re.findall(r'\d+', game_qty_str)
            try :
                game_qty_sum=int(game_qty[0])+int(game_qty[1])
            except:
                game_qty_sum=0
            

            game_ID_int=int(numbers[0])
            if game_qty_sum == 5 :
                game_ID_list.extend([str(game_ID_int+1),str(game_ID_int+2),str(game_ID_int+3),str(game_ID_int+4)])
                game_patch_list.extend([game_patch,game_patch,game_patch,game_patch])
                game_date_list.extend([game_date,game_date,game_date,game_date])
            elif game_qty_sum == 4 :
                game_ID_list.extend([str(game_ID_int+1),str(game_ID_int+2),str(game_ID_int+3)])
                game_patch_list.extend([game_patch,game_patch,game_patch])
                game_date_list.extend([game_date,game_date,game_date])
            elif game_qty_sum == 3 :
                game_ID_list.extend([str(game_ID_int+1),str(game_ID_int+2)])
                game_patch_list.extend([game_patch,game_patch])
                game_date_list.extend([game_date,game_date])
            elif game_qty_sum == 2 :
                game_ID_list.extend([str(game_ID_int+1)])
                game_patch_list.extend([game_patch])
                game_date_list.extend([game_date])
            #else : 
                #pass
        except:
            pass
    
    return [game_ID_list,game_patch_list,game_date_list]

def get_gameDfAllTournament(Tournaments_allLink):
    allGameDf = pd.DataFrame(columns=['game_ID','Tournamets','game_patch','game_date'])
    for i in range(len(Tournaments_allLink)):
        gamelist = get_gamelist1Tournament(Tournaments_allLink[i])
        gameDf=pd.DataFrame(data=gamelist[0],columns=['game_ID'])
        gameDf['Tournamets'] = (Tournaments_allLink[i].split('/'))[5]
        gameDf['game_patch'] = gamelist[1]
        gameDf['game_date'] = gamelist[2]
        allGameDf= pd.concat([allGameDf,gameDf])
    return allGameDf


def team_lose_win(team_soup):
    team_Text = team_soup[0].getText()
    team_sp = team_Text.split(' - ')
    team_name = (team_sp[0].split('\n'))[1]
    team_result = team_sp[1]
    return [team_name,team_result]

def get_computation_data(computation_ID,Tournamets,Patch,Date):
    #################################################
    headers="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    urpage="https://gol.gg/game/stats/{}/page-fullstats/".format(computation_ID)
    url=urllib.request.Request(urpage,headers={"user-Agent":headers})
    page = urlopen(url)
    soup=BeautifulSoup(page,"html.parser")
    gameList=soupToList(soup,-1,0)

    gameDf=pd.DataFrame(gameList)
    gameDfT = gameDf.T

    gameAry=np.array(gameList)
    gameAryT=gameAry.T 
    gameAryT[0]
    gameDfT.columns = gameAryT[0]
    filterFrist=(gameDfT['Player']!='Player')
    gameDfT1=gameDfT[filterFrist]

    table=soup.find_all("tr")
    hero=(table[0]).find_all('th')
    heroList=[]
    for i in range(len(hero)-1):
        heroList.append(hero[i+1].find('img')['alt'])
    heroDf=pd.DataFrame(data=heroList,columns=['hero'])

    gameDfT1.reset_index(drop=True,inplace=True)
    gameDfT2=pd.concat([heroDf,gameDfT1],axis=1)

    ######################################################
    headers="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    urpage="https://gol.gg/game/stats/{}/page-game/".format(computation_ID)
    url=urllib.request.Request(urpage,headers={"user-Agent":headers})
    page = urlopen(url)
    page_game_soup=BeautifulSoup(page,"html.parser")

    blue_team_soup = page_game_soup.find_all("div",class_='col-12 blue-line-header')
    red_team_soup = page_game_soup.find_all("div",class_='col-12 red-line-header')
    blue_team_data = team_lose_win(blue_team_soup)
    red_team_data = team_lose_win(red_team_soup)

    ########################################################
    team_list=[blue_team_data[0],blue_team_data[0],blue_team_data[0],blue_team_data[0],blue_team_data[0],red_team_data[0],red_team_data[0],red_team_data[0],red_team_data[0],red_team_data[0]]
    win_lose_list=[blue_team_data[1],blue_team_data[1],blue_team_data[1],blue_team_data[1],blue_team_data[1],red_team_data[1],red_team_data[1],red_team_data[1],red_team_data[1],red_team_data[1]]
    
    try : 
        gameDfT2['TEAM'] = team_list
        gameDfT2['WIN_LOSE'] = win_lose_list
    except Exception as e:
        # 捕获异常并记录到日志文件
        logging.exception("[get game information] ERROR data game ID {}: %s".format(computation_ID), e)
        gameDfT2['TEAM'] = "unknow"
        gameDfT2['WIN_LOSE'] = "unknow"
    gameDfT2['game_ID'] = computation_ID
    gameDfT2['Tournamets'] = Tournamets
    gameDfT2['Patch'] = Patch
    gameDfT2['Date'] = Date
    return gameDfT2

def get_computation_all_data(computation_ID_list,Tournamets_list,Patch_list,Date_list):
    all_gameinfo_df = get_computation_data(computation_ID_list[0],Tournamets_list[0],Patch_list[0],Date_list[0])
    for i in range(len(computation_ID_list)-1):
        logging.info("[get game information] get game ID {} information".format(computation_ID_list[i+1]))
        try:
            gameinfo_df = get_computation_data(computation_ID_list[i+1],Tournamets_list[i+1],Patch_list[i+1],Date_list[i+1])
            all_gameinfo_df = pd.concat([all_gameinfo_df,gameinfo_df])
        except:
            logging.debug("[get game information fail] get game ID {} found get some error".format(computation_ID_list[i+1]))
            pass
    return all_gameinfo_df


def get_all_lol_game_info(season_list, csvname):
    logging.info('-Step 1 : get Tournaments URL-------------------------------------------------')
    Tournaments_allLink_list=get_Tournaments_allLink(season_list)
    logging.info('-Step 2 : get game ID-------------------------------------------------')
    GameID_df = get_gameDfAllTournament(Tournaments_allLink_list)
    GameID_list=GameID_df['game_ID'].to_list()
    GameTournamets_list=GameID_df['Tournamets'].to_list()
    GamePatch_list=GameID_df['game_patch'].to_list()
    GameDate_list=GameID_df['game_date'].to_list()
    logging.info('-Step 3 : get game information-------------------------------------------------')
    all_game_info=get_computation_all_data(GameID_list,GameTournamets_list,GamePatch_list,GameDate_list)
    logging.info('-Step 4 : keep at csv-------------------------------------------------')
    all_game_info.to_csv('{}'.format(csvname))

def get_all_lol_game_info(season_list):
    for i in range(len(season_list)):
        logging.info('-Step 1 : get Tournaments URL-------------------------------------------------')
        Tournaments_allLink_list=get_Tournaments_allLink([season_list[i]])
        logging.info('-Step 2 : get game ID-------------------------------------------------')
        GameID_df = get_gameDfAllTournament(Tournaments_allLink_list)
        GameID_list=GameID_df['game_ID'].to_list()
        GameTournamets_list=GameID_df['Tournamets'].to_list()
        GamePatch_list=GameID_df['game_patch'].to_list()
        GameDate_list=GameID_df['game_date'].to_list()
        logging.info('-Step 3 : get game information-------------------------------------------------')
        all_game_info=get_computation_all_data(GameID_list,GameTournamets_list,GamePatch_list,GameDate_list)
        logging.info('-Step 4 : keep at csv-------------------------------------------------')
        all_game_info.to_csv('{}.csv'.format(season_list[i]))

def get_lol_game_info():
    json_file = "setting.json"
    with open(json_file, 'r') as file:
        json_dict = json.load(file)

    season_list=json_dict['season_list']
    csvname=json_dict['csvname']
    get_all_lol_game_info(season_list)

if __name__ == "__main__":
    
    get_lol_game_info()