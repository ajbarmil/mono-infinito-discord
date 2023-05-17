#!/usr/bin/env python
#! -*- encoding: utf8 -*-
# 3.- Mono Library

import pickle
import random
import re
import sys
from typing import List, Optional, TextIO

## Nombres: ALEJANDRO JOAQUÍN BARCELÓ MILKOVA

########################################################################
########################################################################
###                                                                  ###
###  Todos los métodos y funciones que se añadan deben documentarse  ###
###                                                                  ###
########################################################################
########################################################################


def convert_to_lm_dict(d: dict):
    for k in d:
        l = sorted(((y, x) for x, y in d[k].items()), reverse=True)
        d[k] = (sum(x for x, _ in l), l)


class Monkey():

    def __init__(self):
        self.r1 = re.compile('[.;?!]')
        self.r2 = re.compile('[^\w<@>:]+')
        self.info = {}

    def get_n(self):
        return self.info.get('n', 0)

    def index_sentence(self, sentence:str):
        n = self.info['n']

        if(sentence!=""): # no nos interesa analizar frases vacías
            for i in range(2, n+1): # para cada valor de n
                sentence2 = "$ "*(i-1) + sentence + " $" # se añaden n-1 $ al principio de la frase y un $ al final

                sensplit = sentence2.split(" ") # obtenemos las palabras que forman la frase
                for word_i in range(len(sensplit)): # por cada palabra en la frase
                    if(word_i+1 >= i): # solo se empezarán a añadir n-gramas cuando se haya iterado por al menos n palabras en una frase
                        temptuple = [] # haremos la tupla a partir de una lista, que es más fácil de modificar
                        for word_j in range(word_i-i+1, word_i): # sin incluir word_i, que es la palabra actual
                            temptuple.append(sensplit[word_j]) # vamos añadiendo las palabras anteriores a la palabra actual
                        temptuple = tuple(temptuple) # convertimos la lista en una tupla
                        try:
                            self.info['lm'][i][temptuple] # intentamos acceder a la entrada de la tupla para ver si existe
                            try: # se suma 1 al contador de la palabra en caso de que exista
                                self.info['lm'][i][temptuple][sensplit[word_i]] += 1
                            except: # si no existe, simplemente se inicializa
                                self.info['lm'][i][temptuple][sensplit[word_i]] = 1
                        except:
                            self.info['lm'][i][temptuple] = {} # si no existe la entrada, se inicializa junto con el n-grama que se ha intentado añadir
                            self.info['lm'][i][temptuple][sensplit[word_i]] = 1


    def compute_lm(self, filenames:List[str], lm_name:str, n:int):
        self.info = {'name': lm_name, 'filenames': filenames, 'n': n, 'lm': {}}
        for i in range(2, n+1):
            self.info['lm'][i] = {}
        for filename in filenames:
            analysisoff = False # variable para dejar de analizar en caso de encontrarse con varias líneas vacías consecutivas
            frase = "" # aquí iremos almacenando las frases a indexar
            for line in open(filename, encoding='utf-8'):
                lesplit = re.split(self.r1, line) # obtenemos una lista que fragmenta la línea en trozos pertenecientes a frases distintas
                if (line == "\n"): # si la línea está vacía (es solo un salto de línea), eso quiere decir que ha habido dos saltos de línea
                    self.index_sentence(re.sub(self.r2, " ", frase.lower()).strip()) # por lo que añadimos la frase que teníamos...
                    if(not analysisoff):
                        frase = "" # ...y empezamos una nueva a no ser que la anterior línea fuera una línea vacía
                        analysisoff = True # se detiene el análisis para siguientes líneas vacías
                    continue
                else: # si la línea no está vacía, se retoma el análisis en caso de haber sido detenido
                    analysisoff = False

                frase += " " + lesplit[0].strip() # en caso contrario, simplemente se añade el primer elemento de la lista a la frase actual
                for elem in range(len(lesplit)): # y por cada elemento de la lista que no sea el primero, se indexa la frase anterior y se empieza una nueva frase
                    if (elem != 0):
                        self.index_sentence(re.sub(self.r2, " ", frase.lower()).strip()) # cabe destacar que se retira cualquier espacio sobrante al principio de la frase
                        frase = lesplit[elem]

            self.index_sentence(re.sub(self.r2, " ", frase.lower()).strip()) # se añade la última frase, que de otra forma quedaría suelta y sin añadir

        #print(self.info['lm'][3]) # (comando para testear)
        for i in range(2, n+1):
            convert_to_lm_dict(self.info['lm'][i])
        #print(self.info['lm'][3]) # (comando para testear)

    def load_lm(self, filename:str):
        with open(filename, "rb") as fh:
            self.info = pickle.load(fh)

    def save_lm(self, filename:str):
        with open(filename, "wb") as fh:
            pickle.dump(self.info, fh)

    def save_info(self, filename:str):
        with open(filename, "w", encoding='utf-8', newline='\n') as fh:
            self.print_info(fh=fh)

    def show_info(self):
        self.print_info(fh=sys.stdout)

    def print_info(self, fh:TextIO):
        print("#" * 20, file=fh)
        print("#" + "INFO".center(18) + "#", file=fh)
        print("#" * 20, file=fh)
        print(f"language model name: {self.info['name']}", file=fh)
        print(f'filenames used to learn the language model: {self.info["filenames"]}', file=fh)
        print("#" * 20, file=fh)
        print(file=fh)
        for i in range(2, self.info['n']+1):
            print("#" * 20, file=fh)
            print("#" + f'{i}-GRAMS'.center(18) + "#", file=fh)
            print("#" * 20, file=fh)
            for prev in sorted(self.info['lm'][i].keys()):
                wl = self.info['lm'][i][prev]
                print(f"'{' '.join(prev)}'\t=>\t{wl[0]}\t=>\t{', '.join(['%s:%s' % (x[1], x[0]) for x in wl[1]])}" , file=fh)


    def generate_sentences(self, n:Optional[int], nsentences:int=10, prefix:Optional[str]=None):
        if(n is None): # si no se ha especificado una n, se asigna el valor máximo de esta
            n = self.info['n']
        if(prefix is None): # si no se ha especificado un prefijo, se empieza con una tupla de n-1 $
            ini = ["$"]*(n-1)
            prefix = "" # aquí pongo esto para facilitar la escritura de mi código más adelante
        else: # en caso contrario...
            if(len(prefix.split(" "))>=n): # en los casos donde el prefijo tenga una longitud mayor que n-1...
                ini = prefix.split(" ")[-(n-1):] # ...se empieza el proceso con una tupla de las últimas n-1 palabras del prefijo
            else: # en caso contrario, se rellena con dólares al principio de la tupla inicial
                ini = ["$"]*((n-1)-len(prefix.split(" ")))+prefix.split(" ")
        ini = tuple(ini) # convertimos la lista que hemos preparado en una tupla

        tobreak = False # flag para poder salir de un doble bucle
        for i in range(nsentences): # vamos a generar nsentences frases
            frase = prefix # la frase empieza por el prefijo (por eso se especifica como "" cuando no hay prefijo, para empezar la frase vacía)
            curr = ini # utilizaremos curr para referirnos a la tupla siendo tratada en cada iteración del siguiente bucle
            for i in range(50-len(prefix.split(" "))): # como mucho, las frases deben durar 50 palabras más o menos
                try:
                    new_word = self.info['lm'][n][curr] # seleccionamos los valores asociados a la tupla actual
                    lottery = random.randint(1, new_word[0]) # elegimos un número entre 1 y el número total de veces que han aparecido todas las palabras que siguen la tupla actual
                    counter = 0 # un contador útil para poder elegir una palabra aleatoria
                    for item in new_word[1]: # por cada palabra que puede suceder la tupla
                        if(lottery <= item[0]+counter): # si el número aleatorio no supera el cúmulo de los números de veces de las palabras por las que
                            new_word = item[1] # se ha pasado, se elige la palabra actual como nueva palabra y se sale del bucle
                            break
                        counter += item[0] # en caso contrario, se añade el número de la palabra actual para ir acumulando los números

                    if(new_word == "$"): # si la nueva palabra es $, se termina la frase y se sale del bucle
                        break
                    else: # en caso contrario, se añade la nueva palabra a la frase
                        frase += " " + new_word

                    # modificamos la tupla para obtener una nueva tupla actual que contenga la nueva palabra
                    curr = list(curr)
                    curr.pop(0) # quitando, evidentemente, la primera palabra de la tupla anterior
                    curr.append(new_word)
                    curr = tuple(curr)

                except: # si no se ha encontrado el prefijo, es porque dicho prefijo no existe
                    print("prefix not found!")
                    tobreak = True # se pone esta flag a true...
                    break
            if(tobreak): # ...y de esta forma, se puede salir fácilmente de los dos bucles
                break
            #print(frase.strip()) # finalmente, se muestra la frase sin espacios que puedan sobrar
            return(frase.strip())


if __name__ == "__main__":
    print("Este fichero es una librería, no se puede ejecutar directamente")


