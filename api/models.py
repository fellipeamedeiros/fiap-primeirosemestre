from pydantic import BaseModel
from typing import Optional, List, Dict

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
