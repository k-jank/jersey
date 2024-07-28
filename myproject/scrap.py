# scrap.py
import os
import django

# Konfigurasi Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from products.models import Product
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

def save_product(title, price, rating, sold, link, img_url):
    product, created = Product.objects.get_or_create(
        title=title,
        defaults={
            'price': price,
            'rating': rating,
            'sold': sold,
            'link': link,
            'image_url': img_url
        }
    )
    if not created:
        product.price = price
        product.rating = rating
        product.sold = sold
        product.link = link
        product.image_url = img_url
        product.save()

def scrape(urls):
    driver = webdriver.Chrome()

    for url in urls:
        driver.get(url)
        page_number = 1  # Menyimpan nomor halaman saat ini

        while True:
            # Beri waktu untuk halaman memuat konten awal
            time.sleep(5)

            # Scroll secara bertahap
            last_height = driver.execute_script("return document.body.scrollHeight")

            # Scroll pelan-pelan
            for i in range(0, last_height, 500):  # Scroll per 500px
                driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(5)  # Tunggu sebentar agar konten baru bisa dimuat

            # Scroll ke bawah hingga akhir halaman
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

            # Setelah semua produk dimuat, ambil HTML dan parsing
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_containers = soup.find_all('div', class_='css-1sn1xa2')
            print(f'Page {page_number}: Found {len(product_containers)} products from {url}')

            # Ekstrak data produk
            for product in product_containers:
                # Mendapatkan informasi dari elemen produk
                title = product.find('div', class_='prd_link-product-name css-3um8ox').get_text(strip=True)
                price = product.find('div', class_='prd_link-product-price css-h66vau').get_text(strip=True)
                
                # Cari rating jika ada
                rating_element = product.find('span', class_='prd_rating-average-text css-t70v7i')
                rating = rating_element.get_text(strip=True) if rating_element else 'No rating'
                
                # Cari sold jika ada
                sold_element = product.find('span', class_='prd_label-integrity css-1sgek4h')
                sold = sold_element.get_text(strip=True) if sold_element else 'No sales yet'
                
                link = product.find('a')['href']
                
                # Ekstrak gambar
                img_element = product.find('div', class_='pcv3_img_container css-1mygogd').find('img')
                img_url = img_element['src'] if img_element else None
                
                # Simpan data produk ke database
                save_product(title, price, rating, sold, link, img_url)

            # Navigasi ke halaman berikutnya
            try:
                next_button = driver.find_element(By.XPATH, '//a[@data-testid="btnShopProductPageNext"]')
                if next_button:
                    driver.get(next_button.get_attribute('href'))
                    page_number += 1 
                    time.sleep(5) 
                else:
                    print('No more pages found.')
                    break
            except Exception as e:
                print('No more pages found or error occurred.')
                break

    driver.quit()

# Daftar URL yang akan di-scrape
urls = [
    'https://www.tokopedia.com/gresikunitedstore/product',
    'https://www.tokopedia.com/psimstorejogja/product'
]

scrape(urls)
