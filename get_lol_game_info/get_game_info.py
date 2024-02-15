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
        except:
            pass
    return Tournaments_list

def get_Tournaments_allLink(season_button_ID_list): #輸入賽季ID>取得該賽季所有比賽資訊連結
    Tournaments_allList=[]
    for i in range(len(season_button_ID_list)):
        Tournaments_allList = Tournaments_allList + get_Tournaments_link(season_button_ID_list[i])
    return Tournaments_allList
def get_gamelist1Tournament(TournamentURL):
    driver_path = 'C:\chromedriver-win64\chromedriver.exe'
    driver = webdriver.Chrome(executable_path=driver_path) # 請提供您的 ChromeDriver 路徑
    driver.get(TournamentURL)

    text_to_wait_for = "Worlds Main Event 2023  "
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
    gamelist1page_td=gamelist1page_soup.find_all('td')
    gamelist1page_soup = BeautifulSoup(new_page_html1, 'html.parser')
    gamelist1page_td=gamelist1page_soup.find_all('td')

    gamelist1page_lst=[]
    for i in range(len(gamelist1page_td)):
        try:
            y = gamelist1page_td[i].find('a')['href']
            numbers = re.findall(r'\d+', y)
            gamelist1page_lst.append(numbers[0])
        except:
            pass
    
    return gamelist1page_lst
def get_gamelistAllTournament(Tournaments_allLink):
    gamelistAllTournament=[]
    for i in range(len(Tournaments_allLink)):
        gamelistAllTournament=gamelistAllTournament+get_gamelist1Tournament(Tournaments_allLink[i])
    return gamelistAllTournament
def get_gameDfAllTournament(Tournaments_allLink):
    allGameDf = pd.DataFrame(columns=['game_ID','Tournamets'])
    for i in range(len(Tournaments_allLink)):
        gamelist = get_gamelist1Tournament(Tournaments_allLink[i])
        gameDf=pd.DataFrame(data=gamelist,columns=['game_ID'])
        gameDf['Tournamets'] = (Tournaments_allLink[i].split('/'))[4]
        allGameDf= pd.concat([allGameDf,gameDf])
    return allGameDf


def team_lose_win(team_soup):
    team_Text = team_soup[0].getText()
    team_sp = team_Text.split(' - ')
    team_name = (team_sp[0].split('\n'))[1]
    team_result = team_sp[1]
    return [team_name,team_result]
def soupToList(soup,trReduce,tdReduce):
    table=soup.find_all("tr")
    datai=[]
    for i in range(len(table)+trReduce):
        dataj=[]
        for j in range(len(table[1].find_all("td"))+tdReduce):
            dataj.append((table[i-trReduce].find_all("td"))[j-tdReduce].getText())
        datai.append(dataj)
    return datai
def get_computation_data(computation_ID):

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
    gameDfT2['TEAM'] = team_list
    gameDfT2['WIN_LOSE'] = win_lose_list
    gameDfT2['game_ID'] = computation_ID
    return gameDfT2

def get_computation_all_data(computation_ID_list):
    all_gameinfo_df = get_computation_data(computation_ID_list[0])
    for i in range(len(computation_ID_list)-1):
        gameinfo_df = get_computation_data(computation_ID_list[i+1])
        all_gameinfo_df = pd.concat([all_gameinfo_df,gameinfo_df])
    return all_gameinfo_df


def get_all_lol_game_info(season_list, csvname):
    Tournaments_allLink_list=get_Tournaments_allLink(season_list)
    GameID_df = get_gameDfAllTournament(Tournaments_allLink_list)
    GameID_list=GameID_df['game_ID'].to_list()
    all_game_info=get_computation_all_data(GameID_list)

    all_game_info.to_csv('{}'.format(csvname))

def get_lol_game_info():
    json_file = "setting.json"
    with open(json_file, 'r') as file:
        json_dict = json.load(file)

    season_list=json_dict['season_list']
    csvname=json_dict['csvname']
    get_all_lol_game_info(season_list, csvname)

if __name__ == "__main__":
    
    get_lol_game_info()