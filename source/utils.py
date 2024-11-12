from bs4 import BeautifulSoup as BS
import requests as rq
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


# Creem un diccionari que té per claus els noms dels indicadors, i per valors els links corresponents.
def get_list_of_nav():
    # Retorna un diccionari amb tots els enllaços dels topics que volem buscar
    url = 'https://datosmacro.expansion.com'
    page = smart_get_request(url)
    data = BS(page.content, features="html.parser")
    nav = data.find(id='block-bstb5-dm-topmenu').find_all('li')
    list_of_nav = {elements.a.string: elements.a['href'] for elements in nav}
    return list_of_nav


# Funció que obté les dades de les taules de la web utilitzant la funció get_table_data.
def generate_result_table(country_links, list_headers_table=[0, 1, 2], list_header_table=[0, 1, 2],
                          link_definition=lambda x: x):
    df_result = pd.DataFrame()
    for country, link in country_links.items():
        link = link_definition(link)
        country_data = get_table_data(link, list_headers_table, list_header_table)
        if country_data.empty:
            continue
        # filtrem per l'any 2023 per tindre dades cotades
        country_data = country_data[country_data['Fecha'].str.contains('2023', na=False)]
        country_data['Pais'] = country
        # Agreguem totes les dades resultants
        df_result = pd.concat([df_result, country_data], ignore_index=True)
    return df_result


# Funció que retorna l'SMI utilitzant la funció generate_result_table.
# Retorna un dataframe amb el resultat.
def get_smi_yearly_data():
    url_smi = get_list_of_nav()['Salario SMI']  # Seleccionem el link del diccionari.
    country_links_smi = get_country_links(url_smi)
    df_result = generate_result_table(country_links_smi, link_definition=lambda x: url_smi + '/' + x.split('/')[
        2])  # Obtenim les dades de la taula.
    df_result['SMI'] = pd.to_numeric(df_result['SMI'].str.replace('$', '',
                                                                  regex=False)
                                     # Netegem el dataframe perquè sigui consistent amb totes les dades.
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
    df_result = df_result.groupby(['Pais', 'Fecha']).mean()

    return df_result


# Funció que retorna el dèficit utilitzant la funció generate_result_table.
# Retorna un dataframe amb el resultat.
def get_deficit_yearly_data():
    country_links_deficit = get_country_links(get_list_of_nav()['Déficit'])
    df_result = generate_result_table(country_links_deficit, [0, 1, 3], [0, 1, 3])
    df_result['Déficit (%PIB)'] = pd.to_numeric(df_result['Déficit (%PIB)'].str.replace(',', '.', regex=False)
                                                .str.replace('%', '', regex=False))
    df_result['Déficit (M.€)'] = pd.to_numeric(df_result['Déficit (M.€)'].str.replace('.', '', regex=False)
                                               .str.replace(',', '.', regex=False))
    df_result.rename(columns={'Déficit (%PIB)': 'Dèficit PIB', 'Déficit (M.€)': 'Dèficit'}, inplace=True)
    return df_result


# Funció que retorna el deute utilitzant la funció generate_result_table.
# Retorna un dataframe amb el resultat.
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


# Funció que retorna la EPA utilitzant la funció generate_result_table.
# Retorna un dataframe amb el resultat.
def get_epa_yearly_data():
    country_links_epa = get_country_links(get_list_of_nav()['EPA'])
    df_result = generate_result_table(country_links_epa, [0, 1, 2, 3], [0, 1, 2, 3])
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
    # Agafem la mitjana de les dades per poder equiparar-les amb altres camps
    df_result = df_result.groupby(['Pais', 'Fecha']).mean()
    return df_result


# Funció que retorna el PIB utilitzant la funció generate_result_table.
# Retorna un dataframe amb el resultat.
def get_pib_yearly_data():
    country_links_epa = get_country_links(get_list_of_nav()['PIB'])
    df_result = generate_result_table(country_links_epa, [0, 1, 3], [0, 1, 3])
    df_result['Var. PIB (%)'] = pd.to_numeric(df_result['Var. PIB (%)'].str.replace(',', '.', regex=False)
                                              .str.replace('%', '', regex=False))
    df_result['PIB anual'] = pd.to_numeric(df_result['PIB anual'].str.replace('.', '', regex=False)
                                           .str.replace('M€', '', regex=False).str.replace('\u00A0', '', regex=False))
    return df_result


# Funció que retorna l'atur. Aquesta la fem amb selenium (en part), per a complementar la pràctica amb una altra tecnologia.
# PER A LES FUNCIONS QUE USEN SELENIUM, CAL FIREFOX INSTAL·LAT.
def get_atur_yearly_data():
    url = 'https://datosmacro.expansion.com/paro?anio=2023'  # Link d'on recopilarem la informació. Fem del 2023 per ser consistents amb la resta de dades.
    driver = webdriver.Firefox()  # Activem el navegador
    driver.get(url)
    driver.maximize_window()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID,
                                                                'ue-accept-notice-button'))).click()  # Acceptem les cookies. Busquem el botó pel seu ID i fem click amb .click().
    dates = driver.find_elements(By.XPATH,
                                 '''//td[contains(@class, 'fecha')]''')  # Busquem els valors de la taula que corresponen a la data, pel seu XPATH. Ens fixem en el HTML i veiem que són els td amb classe que conté 'fecha'.
    anys = [date.get_attribute('innerHTML').split(' ')[1] for date in
            dates]  # Seleccionem el text interior de l'HTML, i fem split(' ')[1] per quedar-nos amb l'any.
    anys_df = pd.DataFrame({'Fecha': anys})  # Generem el dataframe amb els anys.
    atur_df = get_table_data(url, [0, 1], [0, 1])  # Usem la funció get_table_data per obtenir les dades de l'atur.
    atur_df['Países'] = atur_df['Países'].str.replace(' [+]', '')  # Netegem les dades.
    atur_df['Tasa de desempleo'] = atur_df['Tasa de desempleo'].str.replace('%', '')
    atur_df = atur_df.rename(columns={'Países': 'Pais', 'Tasa de desempleo': 'Atur'})
    df_result = pd.concat([atur_df, anys_df], join='inner', axis=1)  # Ajuntem els dos dataframes.
    driver.close()
    return df_result


# Funció que retorna l'IPC utilitzant selenium (tota).
def get_ipc_data():
    url = get_list_of_nav()['IPC']  # Link d'on trobem la informació
    driver = webdriver.Firefox()
    driver.get(url)
    driver.maximize_window()
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'ue-accept-notice-button'))).click()  # Acceptem cookies.
    countries = driver.find_elements(By.XPATH,
                                     '''//a[contains(@href, '/ipc-paises/')]''')  # Busquem el link on es troba l'IPC de cada pais.
    urls_pre = [country.get_attribute('href') for country in
                countries]  # Seleccionem l'atribut href per a obtenir el link.
    urls = [j for j in urls_pre if
            not 'comunidades' in j]  # Descartem els links de les comunitats autònomes d'Espanya per ser consistents.
    df_result = pd.DataFrame(
        columns=['Pais', 'Fecha', 'IPC Anual General'])  # Creem un dataframe amb les columnes desitjades.
    k = 0
    for url in urls:  # Per a cada link de cada pais.
        driver.get(url)  # Anem al link.
        try:
            ipc_1 = driver.find_element(By.XPATH,
                                        '''/html/body/div[3]/div[1]/div/div[2]/div/div/main/section/div[6]/div/article/div/div[6]/div/div[2]/table/tbody/tr[1]/td[2]''')  # Busquem l'IPC corresponent a l'últim any disponible pel seu XPATH complet.
            ipc_g = ipc_1.get_attribute('innerHTML').split('%')[0].replace(',',
                                                                           '.')  # Seleccionem el valor que es l'innerHTML, i netegem les dades.
            country = driver.find_elements(By.XPATH,
                                           '''//div[contains(@class, 'tabletit')]''')  # Busquem el nom del pais que es troba al títol de la taula.
            ctry = country[2].get_attribute('innerHTML').split(':')[
                0]  # Seleccionem el valor que és l'innerHTML, i netegem les dades.
            year = driver.find_elements(By.XPATH,
                                        '''//th[contains(@class, 'header')]''')  # Busquem l'any que és a la header de la taula.
            yr = year[5].get_attribute('innerHTML').split('&nbsp;')[
                1]  # Seleccionem el valor que és l'innerHTML, i netegem les dades.
            df_result.loc[k] = [ctry, yr, ipc_g]  # Ho afegim al dataframe en la fila k.
            k = k + 1  # Ens movem a la pròxima fila.
        except NoSuchElementException:  # Per a alguns paisos, els XPATHs són diferent, i ho fem així:
            ipc_1 = driver.find_element(By.XPATH,
                                        '''/html/body/div[3]/div[1]/div/div[2]/div/div/main/section/div[6]/div/article/div/div[5]/div/div[2]/table/tbody/tr[1]/td[2]''')
            ipc_g = ipc_1.get_attribute('innerHTML').split('%')[0].replace(',', '.')
            country = driver.find_elements(By.XPATH, '''//div[contains(@class, 'tabletit')]''')
            ctry = country[2].get_attribute('innerHTML').split(':')[0]
            year = driver.find_elements(By.XPATH, '''//th[contains(@class, 'header')]''')
            yr = year[5].get_attribute('innerHTML').split('&nbsp;')[1]
            df_result.loc[k] = [ctry, yr, ipc_g]
            k = k + 1
        except:
            print(f'Error in url {url}')
    driver.close()
    return df_result


# Amb aquesta funció obtenim els codis de dos caràcters dels països presents a la web.
# Ho fem a través de selenium.
def get_codes():
    url = 'https://datosmacro.expansion.com'
    driver = webdriver.Firefox()
    driver.get(url)
    driver.maximize_window()
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, 'ue-accept-notice-button'))).click()  # Acceptem les cookies.
    countries = driver.find_elements(By.XPATH,
                                     '''//a[contains(@onclick, 'gaFlg')]''')  # Busquem els elements que contenen els noms dels paisos segons el seu XPATH.
    codes = driver.find_elements(By.XPATH,
                                 '''//span[contains(@class, 'sprflag')]''')  # Busquem els elements que contenen els codis segons el seu XPATH.
    col1 = [country.get_attribute('title') for country in
            countries]  # Seleccionem el nom dels paisos, que és el títol de l'element.
    col2 = [code.get_attribute('class')[-3:-1] for code in codes]  # Descartem la part de la class que no és el codi.
    df_result = pd.DataFrame({'Pais': col1, 'Codi': col2})  # Ho guardem en un dataframe.
    driver.close()
    return df_result


# Funció per tal de descarregar les banderes en format svg.
# D'aquesta forma fem scrapping també d'imatges, no només de text.
def get_flags(countries, time_out=15):  # Utilitzarem els codis obtinguts en la funció get_codes.
    for j in range(countries.shape[0]):  # Per a cada codi:
        k = countries.iat[j, 0]  # Seleccionem el nom del pais.
        v = countries.iat[j, 1]  # I el codi.
        url = 'https://datosmacro.expansion.com/img/flagsvg/' + v + '.svg'  # Construim el link on es guarden les imatges, segons el codi.
        with open('../dataset/flags/' + k + '.svg', 'wb') as f:  # Desem la imatge a la carpeta amb el nom del país.
            flag = smart_get_request(url, timeout_seconds=time_out)
            f.write(flag.content)


# Funció a la qual s'especifica quina URL a buscar i busca, en la taula que contingui més informació, en unes columnes
# especificades, quin son tots els seus continguts.
def get_table_data(url_to_search: str, list_headers_table: list, list_columns_table: list) \
        -> pd.DataFrame:
    try:
        smi_page = smart_get_request(url_to_search)
        data = BS(smi_page.content, features="html.parser")
        tables = data.find_all('table')
        table = [table for table in tables if len(table.find_all('tr')) > 5][0]
        headers = [column.string for column in table.thead.find_all('th')]
        header_filtered = [headers[index] for index in list_headers_table]
        data = []
        for row in table.tbody.find_all('tr'):
            row_data = [cell.string for index_cell, cell in enumerate(row.find_all('td')) if
                        index_cell in list_columns_table]
            data.append(row_data)
        df = pd.DataFrame(data, columns=header_filtered)
        return df
    except Exception as e:
        print("Error in url {}: {}".format(url_to_search, e))
        return pd.DataFrame()


# Funció que retorna, dins d'un tòpic, llista de països amb el seu enllaç pel detall
def get_country_links(url):
    smi_page = smart_get_request(url)
    data = BS(smi_page.content, features="html.parser")
    table = data.find('table').tbody.find_all('tr')
    list_of_countries = {row.td.string.replace(' [+]', ''): row.td.a['href'] for row in table}
    return list_of_countries


# Aquesta funció ens servirà per a obtenir el request i definir els headers, i així dissimular el robot.
# També li afegim un possible timeout.
def smart_get_request(url, timeout_seconds=15):
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
    except rq.exceptions.Timeout:  # Si hi ha algun error en el request, retornem la informació.
        print("Request a {} ha trigat massa en resoldre".format(url))
        pass
    except rq.exceptions.RequestException:
        print("Request a {} no s'ha pogut resoldre".format(url))
        pass
    return r
