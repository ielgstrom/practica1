import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
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
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        driver.get(url)
        result = driver.page_source
        driver.quit()
        return bs(result, features="html.parser")
    except Exception as e:
        print(e)
        return ""


def get_list_of_nav() -> dict[str:str]:
    url = 'https://datosmacro.expansion.com'
    page = smart_get_request(url)
    nav = page.find(id='block-bstb5-dm-topmenu').find_all('li')
    # Es busca el llistat dels diferents elements a navegar
    list_of_nav = {elements.a.string: elements.a['href'] for elements in nav}
    return list_of_nav


def generate_result_table(country_links, list_headers_table=[0, 1, 2], list_header_table=[0, 1, 2],
                          link_definition=lambda x: x) -> pd.DataFrame:
    df_result = pd.DataFrame()
    # Per cada país d'una caracteristica, es fa un bucle amb el pais i el enllaç del detall
    for country, link in country_links.items():
        # Es determina quin enllaç es el que s'ha de navegar
        link = link_definition(link)
        country_data = get_table_data(link, list_headers_table, list_header_table)
        if country_data.empty:
            continue
        # Filtrem per la data escollida per aquest projecte, 2023
        country_data = country_data[country_data['Fecha'].str.contains('2023', na=False)]
        country_data['Pais'] = country
        df_result = pd.concat([df_result, country_data], ignore_index=True)
    return df_result


def get_smi_yearly_data() -> pd.DataFrame:
    url_smi = get_list_of_nav()['Salario SMI']
    country_links_smi = get_country_links(url_smi)
    df_result = generate_result_table(country_links_smi, link_definition=lambda x: url_smi + '/' + x.split('/')[2])
    df_result['SMI'] = pd.to_numeric(df_result['SMI'].str.replace('$', '', regex=False)
                                     .str.replace('.', '', regex=False)
                                     .str.replace(',', '.', regex=False)
                                     .str.replace(' ', '', regex=False)
                                     .str.replace('\u00A0', '', regex=False))
    df_result['SMI'] = df_result['SMI'].round(2)
    df_result['SMI Mon. Local'] = pd.to_numeric(df_result['SMI Mon. Local']
                                                .str.replace('.', '', regex=False)
                                                .str.replace(',', '.', regex=False)
                                                .str.replace(' ', '', regex=False)
                                                .str.replace('\u00A0', '', regex=False))
    df_result['SMI Mon. Local'] = df_result['SMI Mon. Local'].round(2)
    df_result['Fecha'] = df_result['Fecha'].str.replace(r'[^0-9.]', '', regex=True)
    # S'amitjana el resultats en cas que hi hagi diversos resultats per any
    df_result = df_result.groupby(['Pais', 'Fecha']).mean()

    return df_result


def get_deficit_yearly_data() -> pd.DataFrame:
    country_links_deficit = get_country_links(get_list_of_nav()['Déficit'])
    df_result = generate_result_table(country_links_deficit, [0, 1, 3], [0, 1, 3])
    df_result['Déficit (%PIB)'] = pd.to_numeric(df_result['Déficit (%PIB)'].str.replace(',', '.', regex=False)
                                                .str.replace('%', '', regex=False))
    df_result['Déficit (M.€)'] = pd.to_numeric(df_result['Déficit (M.€)'].str.replace('.', '', regex=False)
                                               .str.replace(',', '.', regex=False))
    df_result.rename(columns={'Déficit (%PIB)': 'Dèficit PIB', 'Déficit (M.€)': 'Dèficit'}, inplace=True)
    return df_result


def get_debt_yearly_data():
    country_links_debt = get_country_links(get_list_of_nav()['Deuda'])
    df_result = generate_result_table(country_links_debt, [0, 1, 3, 4], [0, 1, 3, 4])
    df_result['Deuda total (M.€)'] = pd.to_numeric(df_result['Deuda total (M.€)'].str.replace('.', '', regex=False))
    df_result['Deuda (%PIB)'] = pd.to_numeric(df_result['Deuda (%PIB)'].str.replace(',', '.', regex=False)
                                              .str.replace('%', '', regex=False))
    df_result['Deuda Per Cápita'] = pd.to_numeric(df_result['Deuda Per Cápita'].str.replace('.', '', regex=False)
                                                  .str.replace('€', '', regex=False)
                                                  .str.replace('\u00A0', '', regex=False))
    df_result.rename(columns={'Deuda total (M.€)': 'Deute Total', 'Deuda (%PIB)': 'Deute PIB',
                              'Deuda Per Cápita': 'Deute Per Capita'}, inplace=True)
    return df_result


def get_epa_yearly_data() -> pd.DataFrame:
    # Es consegueix la llista de paisos de la pestanya 'EPA'
    country_links_epa = get_country_links(get_list_of_nav()['EPA'])
    df_result = generate_result_table(country_links_epa, [0, 1, 2, 3], [0, 1, 2, 3])
    # Es generen els resultats i es parsejen com corresponen
    df_result['Fecha'] = df_result['Fecha'].str.replace(r'[^0-9.]', '', regex=True)
    df_result['Parados'] = pd.to_numeric(df_result['Parados']
                                         .str.replace('.', '', regex=False)
                                         .str.replace('K', '', regex=False))
    df_result['Empleados'] = pd.to_numeric(df_result['Empleados']
                                           .str.replace('.', '', regex=False)
                                           .str.replace('K', '', regex=False))
    df_result['Activos'] = pd.to_numeric(df_result['Activos']
                                         .str.replace('.', '', regex=False)
                                         .str.replace('K', '', regex=False))
    df_result = df_result.groupby(['Pais', 'Fecha']).mean()
    return df_result


def get_table_data(url_to_search: str, list_headers_table: list, list_columns_table: list, load_js: bool = False) \
        -> pd.DataFrame:
    try:
        if not load_js:
            smi_page = smart_get_request(url_to_search)
        else:
            smi_page = return_js_page(url_to_search)
        tables = smi_page.find_all('table')
        # Es busca la taula que contingui més informació de la pantalla
        table = [table for table in tables if len(table.find_all('tr')) > 5][0]
        headers = [column.string for column in table.thead.find_all('th')]
        # Es busquen els headers de la taula dins d'una llista especificada
        header_filtered = [headers[index] for index in list_headers_table]
        data = []
        for row in table.tbody.find_all('tr'):
            # Per cada fila de la taula, s'afageixen els resultats del df
            row_data = [cell.string for index_cell, cell in enumerate(row.find_all('td')) if
                        index_cell in list_columns_table]
            data.append(row_data)
        df = pd.DataFrame(data, columns=header_filtered)
        return df
    except Exception as e:
        print("Error in url {}: {}".format(url_to_search, e))
        return pd.DataFrame()


def get_country_links(url) -> dict[str, str]:
    # S'obté un diccionari d'una pestanya, amb tots els països mencionats i l'url a la que redirigeixen
    smi_page = smart_get_request(url)
    table = smi_page.find('table').tbody.find_all('tr')
    list_of_countries = {row.td.string.replace(' [+]', ''): row.td.a['href'] for row in table}
    return list_of_countries


def smart_get_request(url: str, timeout_seconds: int = 15):
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
        r = rq.get(url, headers=headers, timeout=timeout_seconds)
        data = bs(r.content, features="html.parser")
    except rq.exceptions.Timeout:
        print("Request a {} ha trigat massa en resoldre".format(url))
        pass
    except rq.exceptions.RequestException:
        print("Request a {} no s'ha pogut resoldre".format(url))
    pass
    return data
