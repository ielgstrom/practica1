from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as BS
import requests as rq
import pandas as pd

def return_js_page(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")  # Disable GPU (optional)
        chrome_options.add_argument("--no-sandbox")  # Overcome some security limitations
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver_service = Service("/usr/local/bin/chromedriver")  # Update with your ChromeDriver path if needed
        driver = webdriver.Chrome(service=driver_service, options = chrome_options)
        driver.get(url)
        result = driver.page_source
        driver.quit()
        return BS(result, features="html.parser")
    except Exception as e:
        print(e)
        return ""

def get_list_of_nav():

  url = 'https://datosmacro.expansion.com'
  page = smart_get_request(url)
  nav = page.find(id='block-bstb5-dm-topmenu').find_all('li') #BUSQUEM TOTS ELS CAPÇALS
  list_of_nav = {elements.a.string : elements.a['href'] for elements in nav} #FER UN OBJECTE AMB CADA LINK DELS CAPÇALS
  return list_of_nav


#IDEA: per cada pestanya que escollim, executem la funcio get_country_links per buscar l'historic de cada país i buscar les seves dades

def get_smi_yearly_data(): # Va a la pantalla de SMI, i per cada link de pais, hi entra i guarda totes les dades que va trobant en un sol df
    contry_links_smi = get_country_links(get_list_of_nav()['Salario SMI'])
    df_result = pd.DataFrame()
    for country, link in contry_links_smi.items():
        formatted_link = get_list_of_nav()['Salario SMI'] + '/' + link.split('/')[2]
        country_data = get_table_data(formatted_link, [0,1,2], [0,1,2])
        #Busquem en el link formatejat, aquells titualr de columna 0, 1, 2 amb rows de contingut 0,1,2
        country_data['Pais'] = country
        df_result = pd.concat([df_result, country_data],ignore_index=True)
    df_result['SMI'] = pd.to_numeric(df_result['SMI'].str.replace('$', '',regex=False)
                                     .str.replace('.','', regex=False)
                                     .str.replace(',','.',regex=False)
                                     .str.replace(' ', '', regex=False)
                                    .str.replace('\u00A0', '', regex=False))
    df_result['SMI Mon. Local'] = pd.to_numeric(df_result['SMI Mon. Local']
                                    .str.replace('.','', regex=False)
                                     .str.replace(',','.',regex=False)
                                     .str.replace(' ', '', regex=False)
                                    .str.replace('\u00A0', '', regex=False))
    df_result['Fecha'] = df_result['Fecha'].str.replace(r'[^0-9.]', '', regex=True)
    print(df_result)

    df_result = df_result.groupby(['Pais', 'Fecha']).mean()

    return df_result

def get_debt_yearly_data():
  df_result = pd.DataFrame()
  contry_links_debt = get_country_links(get_list_of_nav()['Deuda'])
  for element,link in contry_links_debt.items():
    country_data = get_table_data(link, [0,1,2], [0,1,2])
    country_data['Pais'] = element
    df_result = pd.concat([df_result, country_data],ignore_index=True)
  return df_result

def get_epa_yearly_data(): ##Hauria d'agafar les dades d'una taula que no s'ha executat, ja que s'executa per JS.
  df_result = pd.DataFrame()
  contry_links_debt = get_country_links(get_list_of_nav()['EPA'])
  for element,link in contry_links_debt.items():
    country_data = get_table_data(link, [0,1,2,3], [0,1,2,3],True)
    country_data['Pais'] = element
    df_result = pd.concat([df_result, country_data],ignore_index=True)
    break
  return df_result


def get_table_data(url_to_search: str, list_headers_table: list, list_columns_table:list, load_js:bool = False) -> pd.DataFrame:
    #Retorna un df amb les dades de una taula segons la pestanya indicada.
# També es marca quins dels headers de la taula es volen aixi com les columnes les quals pertanyes (poden no ser els mateixos)
  try:
    if not load_js:
      smi_page = smart_get_request(url_to_search)
    else:
      smi_page = return_js_page(url_to_search)
    tables = smi_page.find_all('table')
    table = [table for table in tables if len(table.find_all('tr')) > 5][0]
    headers = [column.string for column in table.thead.find_all('th')]
    header_filtered = [headers[index] for index in list_headers_table]
    data = []
    for row in table.tbody.find_all('tr'):
        row_data = [cell.string for index_cell, cell in enumerate(row.find_all('td')) if index_cell in list_columns_table]
        data.append(row_data)
    df = pd.DataFrame(data, columns=header_filtered)
    return df
  except:
    print("Error in url {}".format(url_to_search))
    return pd.DataFrame()

def get_country_links(url): #retorna per cada pais (en un tab específic) el seu corresponent enllaç per mes informació
# Es a dir
  smi_page = smart_get_request(url)
  table = smi_page.find('table').tbody.find_all('tr')
  #print(table.tbody.tr.td.a['href'])
  list_of_countries = {row.td.string.replace(' [+]','') : row.td.a['href'] for row in table}
  return list_of_countries

def smart_get_request(url, timeout_seconds = 15):
  headers = {
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
  */*;q=0.8",
  "Accept-Encoding": "gzip, deflate, sdch, br",
  "Accept-Language": "en-US,en;q=0.8",
  "Cache-Control": "no-cache",
  "dnt": "1",
  "Pragma": "no-cache",
  "Upgrade-Insecure-Requests": "1",
  "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/5\
  37.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
  }
  try:
    r = rq.get(url, headers=headers, timeout = timeout_seconds)
    data = BS(r.content, features="html.parser")
  except rq.exceptions.RequestException:
    print("Request a {} no s'ha pogut resoldre".format(url))
    pass
  except rq.exceptions.Timeout:
    print("Request a {} ha trigat massa en resoldre".format(url))
    pass

  return data
