import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time


class Scraper:
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    def crear_driver(self):
        return webdriver.Chrome(options=self.options)

    def obtener_html(self, url):
        driver = self.crear_driver()
        try:
            driver.get(url)
            time.sleep(3) # tiempo para renderizar la página
            
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1) # espera para cargar más contenido
            
            driver.execute_script("window.scrollTo(0, 0);")
            
            return driver.page_source
        finally:
            driver.quit()

    async def scrape_catalogo(self, url_pagina):
        html = await asyncio.to_thread(self.obtener_html, url_pagina) # usa hilo para no bloquear el event loop
        print(f"HTML obtenido de {url_pagina} (longitud: {len(html) if html else 'None'})")
        
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        
        album_containers = soup.find_all('div', class_='showindex__children')
        if not album_containers:
            album_containers = soup.find_all('div', class_='categories__children')
        
        print(f"Se encontraron {len(album_containers)} álbumes en la página.")
        
        resultados = []
        
        for album in album_containers:
            try:
                album_links = album.find_all('a', class_='album__main')
                
                for alb in album_links:
                    title = alb.get('title', 'Sin Titulo').strip()
                    
                    img_element = alb.find('img', class_='album__img')
                    if img_element:
                        img_url = img_element.get('data-src') or img_element.get('src')
                        
                        if img_url and img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        
                        resultados.append({
                            "titulo": title,
                            "url_imagen": img_url
                        })
            except Exception as e:
                print(f"Error parseando álbum: {e}")
                continue

        return resultados


if __name__ == "__main__":
    async def main():
        scraper = Scraper()
        test_url = "https://wanfing.x.yupoo.com/albums?tab=gallery"
        items = await scraper.scrape_catalogo(test_url)
        
        print(f"✅ Se encontraron {len(items)} imágenes.")
        for i in items[:5]:
            print(f"- {i['titulo']}: {i['url_imagen']}")

    asyncio.run(main())
