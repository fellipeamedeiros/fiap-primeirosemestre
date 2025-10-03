#!/usr/bin/env python3
"""
Web Scraper para Books to Scrape
Extrai informações de todos os livros do site https://books.toscrape.com/
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse
import os

class BooksScraper:
    def __init__(self, base_url="https://books.toscrape.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.books_data = []
        
    def get_page(self, url):
        """Faz requisição HTTP com tratamento de erro"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
    
    def extract_rating(self, rating_class):
        """Extrai o rating numérico da classe CSS"""
        rating_map = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
        }
        
        for rating_text, rating_value in rating_map.items():
            if rating_text in rating_class:
                return rating_value
        return 0
    
    def extract_price(self, price_text):
        """Extrai o valor numérico do preço"""
        if price_text:
            # Remove símbolos de moeda e converte para float
            price_clean = re.sub(r'[£$€]', '', price_text.strip())
            try:
                return float(price_clean)
            except ValueError:
                return 0.0
        return 0.0
    
    def get_book_details(self, book_url):
        """Extrai detalhes adicionais da página individual do livro"""
        response = self.get_page(book_url)
        if not response:
            return None, None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extrair categoria
        breadcrumb = soup.find('ul', class_='breadcrumb')
        category = "N/A"
        if breadcrumb:
            category_links = breadcrumb.find_all('a')
            if len(category_links) >= 2:
                category = category_links[-1].text.strip()
        
        # Extrair disponibilidade
        availability = "N/A"
        availability_element = soup.find('p', class_='instock availability')
        if availability_element:
            availability_text = availability_element.text.strip()
            # Extrair número de itens disponíveis
            match = re.search(r'\((\d+) available\)', availability_text)
            if match:
                availability = f"{match.group(1)} disponível"
            elif "In stock" in availability_text:
                availability = "Em estoque"
        
        return category, availability
    
    def scrape_books_from_page(self, page_url):
        """Extrai informações dos livros de uma página"""
        print(f"Processando página: {page_url}")
        
        response = self.get_page(page_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.find_all('article', class_='product_pod')
        
        page_books = []
        
        for book in books:
            try:
                # Título
                title_element = book.find('h3').find('a')
                title = title_element.get('title', 'N/A')
                
                # URL do livro para detalhes adicionais
                book_relative_url = title_element.get('href')
                book_url = urljoin(page_url, book_relative_url)
                
                # Preço
                price_element = book.find('p', class_='price_color')
                price_text = price_element.text if price_element else "0"
                price = self.extract_price(price_text)
                
                # Rating
                rating_element = book.find('p', class_='star-rating')
                rating_class = rating_element.get('class', []) if rating_element else []
                rating = self.extract_rating(' '.join(rating_class))
                
                # URL da imagem
                img_element = book.find('div', class_='image_container').find('img')
                img_url = urljoin(self.base_url, img_element.get('src', '')) if img_element else "N/A"
                
                # Obter detalhes adicionais da página do livro
                category, availability = self.get_book_details(book_url)
                
                book_data = {
                    'titulo': title,
                    'preco': price,
                    'rating': rating,
                    'disponibilidade': availability,
                    'categoria': category,
                    'imagem_url': img_url
                }
                
                page_books.append(book_data)
                print(f"  ✓ Extraído: {title}")
                
                # Pequena pausa para ser respeitoso com o servidor
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ✗ Erro ao processar livro: {e}")
                continue
        
        return page_books
    
    def get_all_pages(self):
        """Descobre todas as páginas disponíveis"""
        print("Descobrindo todas as páginas...")
        
        # Começar com a primeira página
        current_url = self.base_url
        page_urls = []
        
        while current_url:
            page_urls.append(current_url)
            
            response = self.get_page(current_url)
            if not response:
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Procurar pelo botão "next"
            next_button = soup.find('li', class_='next')
            if next_button:
                next_link = next_button.find('a')
                if next_link:
                    next_relative_url = next_link.get('href')
                    current_url = urljoin(current_url, next_relative_url)
                else:
                    break
            else:
                break
        
        print(f"Encontradas {len(page_urls)} páginas para processar")
        return page_urls
    
    def scrape_all_books(self):
        """Executa o scraping completo de todos os livros"""
        print("Iniciando scraping de todos os livros...")
        
        # Obter todas as URLs das páginas
        page_urls = self.get_all_pages()
        
        # Processar cada página
        for i, page_url in enumerate(page_urls, 1):
            print(f"\n--- Página {i}/{len(page_urls)} ---")
            books_from_page = self.scrape_books_from_page(page_url)
            self.books_data.extend(books_from_page)
            
            # Pausa entre páginas
            time.sleep(0.5)
        
        print(f"\n✅ Scraping concluído! Total de livros extraídos: {len(self.books_data)}")
        return self.books_data
    
    def save_to_csv(self, filename="books_data.csv"):
        """Salva os dados em arquivo CSV"""
        if not self.books_data:
            print("Nenhum dado para salvar!")
            return
        
        # Salvar diretamente na pasta atual (data/)
        filepath = filename
        
        df = pd.DataFrame(self.books_data)
        
        # Reordenar colunas
        column_order = ['titulo', 'preco', 'rating', 'disponibilidade', 'categoria', 'imagem_url']
        df = df[column_order]
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"📁 Dados salvos em: {filepath}")
        
        # Mostrar estatísticas
        print(f"\n📊 Estatísticas:")
        print(f"   Total de livros: {len(df)}")
        print(f"   Categorias únicas: {df['categoria'].nunique()}")
        print(f"   Preço médio: £{df['preco'].mean():.2f}")
        print(f"   Rating médio: {df['rating'].mean():.1f}/5")
        
        return filepath

def main():
    """Função principal"""
    print("🚀 Iniciando Web Scraper para Books to Scrape")
    print("=" * 50)
    
    # Criar instância do scraper
    scraper = BooksScraper()
    
    try:
        # Executar scraping
        scraper.scrape_all_books()
        
        # Salvar dados
        csv_file = scraper.save_to_csv()
        
        print(f"\n🎉 Processo concluído com sucesso!")
        print(f"📄 Arquivo CSV salvo: {csv_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️ Processo interrompido pelo usuário")
        if scraper.books_data:
            print("Salvando dados parciais...")
            scraper.save_to_csv("books_data_partial.csv")
    except Exception as e:
        print(f"\n❌ Erro durante o scraping: {e}")
        if scraper.books_data:
            print("Salvando dados parciais...")
            scraper.save_to_csv("books_data_partial.csv")

if __name__ == "__main__":
    main()
