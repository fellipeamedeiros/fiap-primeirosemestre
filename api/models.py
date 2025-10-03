from pydantic import BaseModel
from typing import Optional, List

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
