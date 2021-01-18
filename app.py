import shutil  # to save it locally
import requests  # to get image from the web
import requests
import json
import os
import urllib
import sys
import re
import argparse


DIR = "./test"
def clear(): return os.system('cls')


def search_file(dir):
    file_names = []
    for fichier in os.listdir(dir):
        file_names.append(fichier)
    return file_names


def getFilm(fichiers):

    for fichier in fichiers:

        # requete initial
        pre_payload = os.path.splitext(fichier)[0]  # retire l'extension
        # retire a partir de la date
        pre_payload = re.split("\\d{4}", pre_payload)
        pre_payload = pre_payload[0].replace(
            ".", " ")  # retire les eventuels points

        payload = {'api_key': 'a509cff919b82d4a2be6b8f3b999a90f',
                   'language': 'fr-FR', 'query': pre_payload}
        query = urllib.parse.urlencode(payload)
        #print("[*] La query est :", query)
        requete = requests.get(
            'https://api.themoviedb.org/3/search/movie?' + query)
        data = requete.json()
        films = data['results']

        if not films:
            print("[*] Aucun résultat")
            sys.exit()

        # parcours les resultats
        for film in reversed(films[:5]):

            titre = film["title"]
            if not film["release_date"]:
                sortie = "N/A"
            else:
                sortie = film["release_date"]
                sortie = sortie[:4]
            if not film["overview"]:
                resume = "N/A"
            else:
                resume = film["overview"]
            id = film["id"]
            made_title = titre + " (" + sortie + ")"

            # affichage des données
            for _ in range(len(made_title)+4):
                print("-", end="")
            print("")
            print("|", made_title, "|")
            for _ in range(len(made_title)+4):
                print("-", end="")
            print("")
            print(resume)
            print(id)

        # choix du bon ID
        id_choice = int(
            input("Quel est le bon ID ? (Defaut : " + str(id) + ")") or id)
        # requete data du films via id
        req_info = requests.get("https://api.themoviedb.org/3/movie/" + str(
            id_choice) + "?api_key=a509cff919b82d4a2be6b8f3b999a90f&language=fr-FR")
        data = req_info.json()

        # traitement des données
        titre = data["title"] + " (" + data["release_date"][:4] + ")"
        if ":" in titre:
            titre = titre.replace(":", "")
        # modification du fichier
        os.mkdir(DIR + "/" + titre)
        os.rename(DIR + "/" + fichier, DIR + "/" + titre +
                  "/" + titre + os.path.splitext(fichier)[1])

        # get poster image
        os.chdir(os.path.abspath(DIR + "/" + titre))  # change dir to movie dir
        poster = getImage(
            "https://image.tmdb.org/t/p/w500" + data["poster_path"])
        backdrop = getImage(
            "https://image.tmdb.org/t/p/original" + data["backdrop_path"])
        os.rename(poster, "poster.jpg")
        os.rename(backdrop, "backdrop.jpg")

        # print json to file
        jsonfile = open("tmdb.json", "w")
        jsonfile.write(json.dumps(data, indent=4, sort_keys=True))
        jsonfile.close()


def getImage(url):

    # Set up the image URL and filename
    filename = url.split("/")[-1]

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image sucessfully Downloaded: ', filename)
    else:
        print('Image Couldn\'t be retreived')

    return filename


my_parser = argparse.ArgumentParser(description="Rename movies filenames and get metadata from tmdb")
my_parser.add_argument("-p", "--path", type=str, help="path to the directory to analyse")
my_parser.add_argument("-l", "--language", type=str, help="language to use ")

args = my_parser.parse_args()
directory = args.Path

if not os.path.isdir(directory):
    print("The path specified does not exist")

if args.language:
    language = args.language

getFilm(search_file(DIR))
