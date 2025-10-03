import csv
import os
from typing import List, Optional, Dict, Any
from models import Book

class DataService:
    def __init__(self):
        self.csv_path = "../data/books_data.csv"
        self.books_data = []
        self.load_data()
    
    def load_data(self):
        """Carrega os dados do CSV"""
        try:
            if os.path.exists(self.csv_path):
                with open(self.csv_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    self.books_data = []
                    for idx, row in enumerate(csv_reader, 1):
                        row['id'] = idx
                        self.books_data.append(row)
            else:
                self.books_data = []
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.books_data = []
    
    def get_all_books(self) -> List[Book]:
        """Retorna todos os livros"""
        if not self.books_data:
            return []
        
        books = []
        for row in self.books_data:
            try:
                book = Book(
                    id=int(row['id']),
                    titulo=str(row['titulo']),
                    preco=float(row['preco']),
                    rating=int(row['rating']),
                    disponibilidade=str(row['disponibilidade']),
                    categoria=str(row['categoria']),
                    imagem_url=str(row['imagem_url'])
                )
                books.append(book)
            except (ValueError, KeyError) as e:
                print(f"Erro ao processar livro: {e}")
                continue
        return books
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Retorna um livro específico pelo ID"""
        if not self.books_data:
            return None
        
        for row in self.books_data:
            if int(row['id']) == book_id:
                try:
                    return Book(
                        id=int(row['id']),
                        titulo=str(row['titulo']),
                        preco=float(row['preco']),
                        rating=int(row['rating']),
                        disponibilidade=str(row['disponibilidade']),
                        categoria=str(row['categoria']),
                        imagem_url=str(row['imagem_url'])
                    )
                except (ValueError, KeyError) as e:
                    print(f"Erro ao processar livro: {e}")
                    return None
        return None
    
    def search_books(self, title: Optional[str] = None, category: Optional[str] = None) -> List[Book]:
        """Busca livros por título e/ou categoria"""
        if not self.books_data:
            return []
        
        filtered_books = []
        for row in self.books_data:
            match = True
            
            if title:
                if title.lower() not in row['titulo'].lower():
                    match = False
            
            if category:
                if category.lower() not in row['categoria'].lower():
                    match = False
            
            if match:
                try:
                    book = Book(
                        id=int(row['id']),
                        titulo=str(row['titulo']),
                        preco=float(row['preco']),
                        rating=int(row['rating']),
                        disponibilidade=str(row['disponibilidade']),
                        categoria=str(row['categoria']),
                        imagem_url=str(row['imagem_url'])
                    )
                    filtered_books.append(book)
                except (ValueError, KeyError) as e:
                    print(f"Erro ao processar livro: {e}")
                    continue
        
        return filtered_books
    
    def get_all_categories(self) -> List[str]:
        """Retorna todas as categorias únicas"""
        if not self.books_data:
            return []
        
        categories = set()
        for row in self.books_data:
            categories.add(row['categoria'])
        
        return sorted(list(categories))
    
    def get_total_books(self) -> int:
        """Retorna o total de livros"""
        return len(self.books_data)
    
    def is_data_available(self) -> bool:
        """Verifica se os dados estão disponíveis"""
        return len(self.books_data) > 0 and os.path.exists(self.csv_path)
    
    def get_stats_overview(self) -> dict:
        """Retorna estatísticas gerais da coleção"""
        if not self.books_data:
            return {
                "total_livros": 0,
                "preco_medio": 0.0,
                "preco_minimo": 0.0,
                "preco_maximo": 0.0,
                "distribuicao_ratings": {},
                "total_categorias": 0
            }
        
        prices = []
        ratings = []
        categories = set()
        
        for row in self.books_data:
            try:
                prices.append(float(row['preco']))
                ratings.append(int(row['rating']))
                categories.add(row['categoria'])
            except (ValueError, KeyError):
                continue
        
        # Distribuição de ratings
        rating_dist = {}
        for rating in ratings:
            rating_dist[rating] = rating_dist.get(rating, 0) + 1
        
        return {
            "total_livros": len(self.books_data),
            "preco_medio": sum(prices) / len(prices) if prices else 0.0,
            "preco_minimo": min(prices) if prices else 0.0,
            "preco_maximo": max(prices) if prices else 0.0,
            "distribuicao_ratings": rating_dist,
            "total_categorias": len(categories)
        }
    
    def get_stats_by_category(self) -> list:
        """Retorna estatísticas detalhadas por categoria"""
        if not self.books_data:
            return []
        
        # Agrupa livros por categoria
        categories_data = {}
        for row in self.books_data:
            try:
                categoria = row['categoria']
                preco = float(row['preco'])
                rating = int(row['rating'])
                
                if categoria not in categories_data:
                    categories_data[categoria] = {
                        'prices': [],
                        'ratings': []
                    }
                
                categories_data[categoria]['prices'].append(preco)
                categories_data[categoria]['ratings'].append(rating)
            except (ValueError, KeyError):
                continue
        
        # Calcula estatísticas para cada categoria
        stats = []
        for categoria, data in categories_data.items():
            prices = data['prices']
            ratings = data['ratings']
            
            # Distribuição de ratings para esta categoria
            rating_dist = {}
            for rating in ratings:
                rating_dist[rating] = rating_dist.get(rating, 0) + 1
            
            stats.append({
                "categoria": categoria,
                "total_livros": len(prices),
                "preco_medio": sum(prices) / len(prices) if prices else 0.0,
                "preco_minimo": min(prices) if prices else 0.0,
                "preco_maximo": max(prices) if prices else 0.0,
                "distribuicao_ratings": rating_dist
            })
        
        return sorted(stats, key=lambda x: x['total_livros'], reverse=True)
    
    def get_top_rated_books(self) -> List[Book]:
        """Retorna livros com melhor avaliação (rating mais alto)"""
        if not self.books_data:
            return []
        
        # Encontra o rating máximo
        max_rating = 0
        for row in self.books_data:
            try:
                rating = int(row['rating'])
                max_rating = max(max_rating, rating)
            except (ValueError, KeyError):
                continue
        
        # Filtra livros com rating máximo
        top_books = []
        for row in self.books_data:
            try:
                if int(row['rating']) == max_rating:
                    book = Book(
                        id=int(row['id']),
                        titulo=str(row['titulo']),
                        preco=float(row['preco']),
                        rating=int(row['rating']),
                        disponibilidade=str(row['disponibilidade']),
                        categoria=str(row['categoria']),
                        imagem_url=str(row['imagem_url'])
                    )
                    top_books.append(book)
            except (ValueError, KeyError):
                continue
        
        return top_books
    
    def get_books_by_price_range(self, min_price: float, max_price: float) -> List[Book]:
        """Filtra livros dentro de uma faixa de preço específica"""
        if not self.books_data:
            return []
        
        filtered_books = []
        for row in self.books_data:
            try:
                preco = float(row['preco'])
                if min_price <= preco <= max_price:
                    book = Book(
                        id=int(row['id']),
                        titulo=str(row['titulo']),
                        preco=float(row['preco']),
                        rating=int(row['rating']),
                        disponibilidade=str(row['disponibilidade']),
                        categoria=str(row['categoria']),
                        imagem_url=str(row['imagem_url'])
                    )
                    filtered_books.append(book)
            except (ValueError, KeyError):
                continue
        
        return filtered_books
