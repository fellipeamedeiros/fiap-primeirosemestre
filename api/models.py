from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Book(BaseModel):
    id: int
    titulo: str
    preco: float
    rating: int
    disponibilidade: str
    categoria: str
    imagem_url: str

class BookSearch(BaseModel):
    books: List[Book]
    total: int
    
class HealthCheck(BaseModel):
    status: str
    message: str
    total_books: int
    data_file_exists: bool

class StatsOverview(BaseModel):
    total_livros: int
    preco_medio: float
    preco_minimo: float
    preco_maximo: float
    distribuicao_ratings: Dict[int, int]  # {rating: count}
    total_categorias: int

class CategoryStats(BaseModel):
    categoria: str
    total_livros: int
    preco_medio: float
    preco_minimo: float
    preco_maximo: float
    distribuicao_ratings: Dict[int, int]

class StatsCategories(BaseModel):
    categorias: List[CategoryStats]
    total_categorias: int

class PriceRangeFilter(BaseModel):
    livros: List[Book]
    total: int
    preco_minimo: float
    preco_maximo: float

# ML Models
class MLFeature(BaseModel):
    id: int
    titulo_length: int
    preco: float
    rating: int
    disponibilidade_encoded: int  # 0 ou 1
    categoria_encoded: int
    categoria: str

class MLFeatures(BaseModel):
    features: List[MLFeature]
    total: int
    feature_names: List[str]

class TrainingData(BaseModel):
    features: List[List[float]]  # Features numéricas para treinamento
    labels: List[int]  # Labels (ratings) para treinamento
    feature_names: List[str]
    total_samples: int

class PredictionRequest(BaseModel):
    titulo_length: int
    preco: float
    disponibilidade: str  # "In stock" ou "Out of stock"
    categoria: str

class PredictionResponse(BaseModel):
    predicted_rating: int
    confidence: float
    input_features: Dict[str, Any]

# Authentication Models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str
