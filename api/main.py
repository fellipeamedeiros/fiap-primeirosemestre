from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from models import Book, BookSearch, HealthCheck, StatsOverview, StatsCategories, CategoryStats, PriceRangeFilter
from data_service import DataService

app = FastAPI(
    title="Books API",
    description="API para gerenciar dados de livros extraídos do Books to Scrape",
    version="1.0.0"
)

# Inicializa o serviço de dados
data_service = DataService()

@app.get("/")
def read_root():
    return {"message": "ok"}

@app.get("/api/v1/books", response_model=List[Book])
def get_all_books():
    """Lista todos os livros disponíveis na base de dados"""
    books = data_service.get_all_books()
    return books

@app.get("/api/v1/books/search", response_model=BookSearch)
def search_books(
    title: Optional[str] = Query(None, description="Título do livro para busca"),
    category: Optional[str] = Query(None, description="Categoria do livro para busca")
):
    """Busca livros por título e/ou categoria"""
    if not title and not category:
        raise HTTPException(status_code=400, detail="Pelo menos um parâmetro de busca (title ou category) deve ser fornecido")
    
    books = data_service.search_books(title=title, category=category)
    return BookSearch(books=books, total=len(books))

@app.get("/api/v1/books/top-rated", response_model=List[Book])
def get_top_rated_books():
    """Lista os livros com melhor avaliação (rating mais alto)"""
    top_books = data_service.get_top_rated_books()
    return top_books

@app.get("/api/v1/books/price-range", response_model=PriceRangeFilter)
def get_books_by_price_range(
    min: float = Query(..., description="Preço mínimo", ge=0),
    max: float = Query(..., description="Preço máximo", ge=0)
):
    """Filtra livros dentro de uma faixa de preço específica"""
    if min > max:
        raise HTTPException(status_code=400, detail="Preço mínimo não pode ser maior que o preço máximo")
    
    books = data_service.get_books_by_price_range(min, max)
    return PriceRangeFilter(
        livros=books,
        total=len(books),
        preco_minimo=min,
        preco_maximo=max
    )

@app.get("/api/v1/books/{book_id}", response_model=Book)
def get_book_by_id(book_id: int):
    """Retorna detalhes completos de um livro específico pelo ID"""
    book = data_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@app.get("/api/v1/categories", response_model=List[str])
def get_all_categories():
    """Lista todas as categorias de livros disponíveis"""
    categories = data_service.get_all_categories()
    return categories

@app.get("/api/v1/health", response_model=HealthCheck)
def health_check():
    """Verifica status da API e conectividade com os dados"""
    total_books = data_service.get_total_books()
    data_available = data_service.is_data_available()
    
    if data_available and total_books > 0:
        status = "healthy"
        message = f"API funcionando corretamente com {total_books} livros carregados"
    elif data_available and total_books == 0:
        status = "warning"
        message = "API funcionando mas nenhum livro encontrado na base de dados"
    else:
        status = "error"
        message = "Erro ao acessar a base de dados"
    
    return HealthCheck(
        status=status,
        message=message,
        total_books=total_books,
        data_file_exists=data_available
    )

@app.get("/api/v1/stats/overview", response_model=StatsOverview)
def get_stats_overview():
    """Estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings)"""
    stats = data_service.get_stats_overview()
    return StatsOverview(**stats)

@app.get("/api/v1/stats/categories", response_model=StatsCategories)
def get_stats_categories():
    """Estatísticas detalhadas por categoria (quantidade de livros, preços por categoria)"""
    categories_stats = data_service.get_stats_by_category()
    categories = [CategoryStats(**cat_stat) for cat_stat in categories_stats]
    return StatsCategories(categorias=categories, total_categorias=len(categories))
