"""
Download images of drivers and teams

Use png as default image format
"""
import os
import sys
import time
from turtle import up

import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm

# --------------------------------------------------------------------------- #
# CONFIGURAÇÃO GERAL
# --------------------------------------------------------------------------- #
DEFAULT_IMAGE_SIZE = (250, 250)
START_SEASON = 2000
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Opera GX";v="118", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0 (Edition std-2)',
}


# --------------------------------------------------------------------------- #
# Drivers
# --------------------------------------------------------------------------- #
def get_driver_images_urls(drivers: pd.DataFrame):
    drivers_images = {}
    for _, driver in tqdm(drivers.iterrows(), total=drivers.shape[0], desc='Urls drivers'):
        response = requests.get(driver.url, headers=headers)
        soup = BeautifulSoup(response.text, features='lxml')
        img_url = 'https:' + soup.find(class_='infobox-image').find('img')['src']
        drivers_images[driver.driverId] = img_url
    return drivers_images


# --------------------------------------------------------------------------- #
# Constructors
# --------------------------------------------------------------------------- #
def get_seeklogo_url(team: str):
    params = {'q': team}
    response = requests.get('https://seeklogo.com/search', params=params, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    img = soup.select_one("ul.logoGroupCt img.logoImage")
    if img is None or not img.get("src"):
        print(f"Image not found for team: {team}")
        return None
    return img["src"]


def get_constructors_images_urls(constructors: pd.DataFrame) -> dict[str, str]:
    constructors_images = {}
    for _, constructor in tqdm(constructors.iterrows(), desc='Urls constructors', total=len(constructors)):
        url = get_seeklogo_url(constructor['name'])
        if url is None:
            continue
        constructors_images[constructor.constructorId] = url
    return constructors_images


# --------------------------------------------------------------------------- #
# Images
# --------------------------------------------------------------------------- #
def format_image(caminho_imagem):
    if not (caminho_imagem.lower().endswith('.jpg') or caminho_imagem.lower().endswith('.png')):
        raise ValueError("O arquivo precisa ser uma imagem .jpg ou .png")

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size

    lado = min(largura, altura)
    esquerda = (largura - lado) // 2
    topo = (altura - lado) // 2
    direita = esquerda + lado
    fundo = topo + lado

    imagem_crop = imagem.crop((esquerda, topo, direita, fundo))

    imagem_redimensionada = imagem_crop.resize(DEFAULT_IMAGE_SIZE, Image.LANCZOS)

    if caminho_imagem.lower().endswith('.jpg'):
        novo_caminho = os.path.splitext(caminho_imagem)[0] + '.png'
        imagem_redimensionada.save(novo_caminho, 'PNG')
        os.remove(caminho_imagem)
    else:
        imagem_redimensionada.save(caminho_imagem, 'PNG')


def download_image(url: str, id: str, folder: str):
    for _ in range(5):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(3)
    if response.status_code != 200:
        print(f'\tError downloading image for driver {id}: {url}')
        return
    extension = url.split('.')[-1].split('?')[0]
    image_path = os.path.join(folder, f'{id}.{extension.lower()}')
    with open(image_path, 'wb') as f:
        f.write(response.content)
    format_image(image_path)


def download_images(map_images: dict[str, str], folder: str):
    os.makedirs(folder, exist_ok=True)
    for id, url in tqdm(map_images.items(), desc='Download images', total=len(map_images)):
        if os.path.exists(os.path.join(folder, f'{id}.png')):
            continue
        download_image(url, id, folder)

# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def update_images(data_folder: str, images_folder: str):
    os.makedirs(images_folder, exist_ok=True)

    drivers = pd.read_csv('static/data/drivers.csv')
    driver_standings = pd.read_csv('static/data/driver_standings.csv')
    drivers = drivers[drivers.driverId.isin(driver_standings[driver_standings.season >= START_SEASON].driverId.unique())]
    drivers_images = get_driver_images_urls(drivers)
    download_images(drivers_images, os.path.join(images_folder, 'drivers'))

    constructors = pd.read_csv('static/data/constructors.csv')
    constructor_standings = pd.read_csv('static/data/constructor_standings.csv')
    constructors = constructors[constructors.constructorId.isin(constructor_standings[constructor_standings.season >= START_SEASON].constructorId.unique())]
    constructors_images = get_constructors_images_urls(constructors)
    download_images(constructors_images, os.path.join(images_folder, 'constructors'))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python manager/images.py <data folder> <images folder>")
        sys.exit(1)
    
    data_folder = sys.argv[1]
    images_folder = sys.argv[2]
    if not os.path.exists(data_folder):
        print(f"Data folder {data_folder} does not exist")
        sys.exit(1)
    update_images(data_folder, images_folder)
    print("Images updated successfully")
