# Pràctica 1

Aquesta és una pràctica feta per Andreu Quesada i Ignasi Elgström per l'assignatura de Tipologia i cicle de vida de les dades del Màster de Ciència de Dades de la UOC.

## Arxius
Aquest repositori comprèn els següents arxius i carpetes:
* Carpeta source amb el contingut del codi fet amb Python.
    * Arxiu utils.py amb totes les funcions necessaries per generar el contingut.
    * Arxiu main.py amb l'execució del web scarapping i generació del CSV resultant
   
* Carpeta dataset amb el contingut resultant del web scrapping.
  * CSV amb el resultat de les dades històriques dels països analitzats.
  * Carpeta flags amb el resultat de l'obtenció de les imatges obtingudes endurant l'execució del projecte.
* Arxiu requirements.txt amb totes les llibreries externes, amb la seva versió, instal·lades en aquest projecte.
* Arxiu .gitignore per no afegir en el repositori arxius no desitjats.

## Fer servir el repositori
S'ha de tindre instal·lat el navegador Firefox, ja que se'n fa ús d'aquest.

Per executar aquest projecte, s'han de fer quatre passos: 
1. Clonar el repositori en local: ```git clone https://github.com/ielgstrom/practica1.git```
2. Anar al directori del repositori local: ```cd <repositori local>``` 
3. Instal·lar les dependències: ```pip install -r requirements.txt```
4. Executar l'arxiu main.py sense cap paràmetre associat: ```python3 source/main.py```

## DOI de Zenodo

Es pot trobar el següent conjunt de dades amb el següent DOI: 10.5281/zenodo.14107653
