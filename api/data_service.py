import csv
import os
from typing import List, Optional, Dict, Any
from models import Book, MLFeature, MLFeatures, TrainingData

class DataService:
    def __init__(self):
        # Tenta primeiro o caminho local (desenvolvimento), depois o caminho do container
        if os.path.exists("../data/books_data.csv"):
            self.csv_path = "../data/books_data.csv"
        elif os.path.exists("/app/data/books_data.csv"):
            self.csv_path = "/app/data/books_data.csv"
        else:
            self.csv_path = "data/books_data.csv"
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
    
    # ML Methods
    def get_ml_features(self) -> MLFeatures:
        """Retorna dados formatados para features de ML"""
        if not self.books_data:
            return MLFeatures(features=[], total=0, feature_names=[])
        
        # Mapeia categorias para números
        categories = list(set(row['categoria'] for row in self.books_data))
        category_mapping = {cat: idx for idx, cat in enumerate(categories)}
        
        features = []
        for row in self.books_data:
            try:
                # Codifica disponibilidade: 1 para "In stock", 0 para outros
                disponibilidade_encoded = 1 if "In stock" in row['disponibilidade'] else 0
                
                feature = MLFeature(
                    id=int(row['id']),
                    titulo_length=len(row['titulo']),
                    preco=float(row['preco']),
                    rating=int(row['rating']),
                    disponibilidade_encoded=disponibilidade_encoded,
                    categoria_encoded=category_mapping[row['categoria']],
                    categoria=row['categoria']
                )
                features.append(feature)
            except (ValueError, KeyError) as e:
                print(f"Erro ao processar feature: {e}")
                continue
        
        feature_names = [
            "titulo_length", "preco", "rating", 
            "disponibilidade_encoded", "categoria_encoded"
        ]
        
        return MLFeatures(
            features=features,
            total=len(features),
            feature_names=feature_names
        )
    
    def get_training_data(self) -> TrainingData:
        """Retorna dataset formatado para treinamento de ML"""
        if not self.books_data:
            return TrainingData(features=[], labels=[], feature_names=[], total_samples=0)
        
        # Mapeia categorias para números
        categories = list(set(row['categoria'] for row in self.books_data))
        category_mapping = {cat: idx for idx, cat in enumerate(categories)}
        
        features = []
        labels = []
        
        for row in self.books_data:
            try:
                # Features numéricas
                titulo_length = len(row['titulo'])
                preco = float(row['preco'])
                disponibilidade_encoded = 1 if "In stock" in row['disponibilidade'] else 0
                categoria_encoded = category_mapping[row['categoria']]
                
                # Label (target)
                rating = int(row['rating'])
                
                features.append([titulo_length, preco, disponibilidade_encoded, categoria_encoded])
                labels.append(rating)
                
            except (ValueError, KeyError) as e:
                print(f"Erro ao processar dados de treinamento: {e}")
                continue
        
        feature_names = [
            "titulo_length", "preco", "disponibilidade_encoded", "categoria_encoded"
        ]
        
        return TrainingData(
            features=features,
            labels=labels,
            feature_names=feature_names,
            total_samples=len(features)
        )
    
    def predict_rating(self, titulo_length: int, preco: float, 
                      disponibilidade: str, categoria: str) -> Dict[str, Any]:
        """Predição simples de rating baseada em heurísticas"""
        # Mapeia categorias existentes
        categories = list(set(row['categoria'] for row in self.books_data))
        if categoria not in categories:
            categoria_encoded = 0  # Categoria desconhecida
        else:
            category_mapping = {cat: idx for idx, cat in enumerate(categories)}
            categoria_encoded = category_mapping[categoria]
        
        disponibilidade_encoded = 1 if "In stock" in disponibilidade else 0
        
        # Heurística simples para predição
        # Baseada em análise dos dados existentes
        predicted_rating = 3  # Rating padrão
        confidence = 0.5
        
        # Ajusta rating baseado no preço (livros mais caros tendem a ter ratings melhores)
        if preco > 50:
            predicted_rating += 1
            confidence += 0.1
        elif preco < 20:
            predicted_rating -= 1
            confidence += 0.1
        
        # Ajusta rating baseado na disponibilidade
        if disponibilidade_encoded == 1:
            predicted_rating += 0.5
            confidence += 0.1
        
        # Ajusta rating baseado no tamanho do título
        if titulo_length > 50:
            predicted_rating += 0.3
        elif titulo_length < 20:
            predicted_rating -= 0.3
        
        # Limita rating entre 1 e 5
        predicted_rating = max(1, min(5, round(predicted_rating)))
        confidence = min(1.0, confidence)
        
        return {
            "predicted_rating": predicted_rating,
            "confidence": confidence,
            "input_features": {
                "titulo_length": titulo_length,
                "preco": preco,
                "disponibilidade": disponibilidade,
                "categoria": categoria,
                "disponibilidade_encoded": disponibilidade_encoded,
                "categoria_encoded": categoria_encoded
            }
        }
