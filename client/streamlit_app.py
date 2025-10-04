import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(
    page_title="Books Dashboard",
    page_icon="📚",
    layout="wide"
)

# URL base da API - Detecção de ambiente
def get_api_base_url():
    """Detecta se está rodando local ou em produção baseado na variável env"""
    
    # 1. Verifica variável de ambiente API_BASE_URL (prioridade máxima)
    env_url = os.getenv('API_BASE_URL')
    if env_url:
        return env_url
    
    # 2. Verifica se está em produção pela variável env
    env = os.getenv('env', '').lower()
    if env == 'prod':
        return "https://primeirosemestre-api-593831299563.us-central1.run.app/api/v1"
    
    # 3. Default para desenvolvimento local
    return "http://localhost:8000/api/v1"

API_BASE_URL = get_api_base_url()

def get_api_data(endpoint):
    """Faz requisição para a API"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Não foi possível conectar à API: {API_BASE_URL}")
        return None
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

# Título principal
st.title("📚 Books Dashboard")
st.markdown("Dashboard interativo para explorar a coleção de livros")

# Sidebar para navegação
st.sidebar.title("🔍 Navegação")
page = st.sidebar.selectbox(
    "Escolha uma página:",
    ["📊 Overview", "📈 Estatísticas", "🔍 Buscar Livros", "⭐ Top Rated", "💰 Filtro por Preço"]
)

# Mostrar URL da API sendo usada
environment = "🏠 Local" if "localhost" in API_BASE_URL else "☁️ Produção"
st.sidebar.info(f"**Ambiente:** {environment}")
st.sidebar.caption(f"API: {API_BASE_URL}")

# Verificar se a API está funcionando
health_data = get_api_data("/health")
if health_data:
    if health_data["status"] == "healthy":
        st.sidebar.success(f"✅ API Online - {health_data['total_books']} livros")
    else:
        st.sidebar.warning(f"⚠️ {health_data['message']}")
else:
    st.sidebar.error("❌ API Offline")
    st.stop()

# Página Overview
if page == "📊 Overview":
    st.header("📊 Visão Geral da Coleção")
    
    # Buscar estatísticas gerais
    stats = get_api_data("/stats/overview")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Livros", stats["total_livros"])
        
        with col2:
            st.metric("Preço Médio", f"£{stats['preco_medio']:.2f}")
        
        with col3:
            st.metric("Preço Mínimo", f"£{stats['preco_minimo']:.2f}")
        
        with col4:
            st.metric("Preço Máximo", f"£{stats['preco_maximo']:.2f}")
        
        # Gráfico de distribuição de ratings
        st.subheader("📊 Distribuição de Ratings")
        ratings_data = stats["distribuicao_ratings"]
        
        fig = px.bar(
            x=list(ratings_data.keys()),
            y=list(ratings_data.values()),
            labels={'x': 'Rating', 'y': 'Quantidade de Livros'},
            title="Distribuição de Ratings dos Livros"
        )
        st.plotly_chart(fig, use_container_width=True)

# Página Estatísticas
elif page == "📈 Estatísticas":
    st.header("📈 Estatísticas por Categoria")
    
    # Buscar estatísticas por categoria
    cat_stats = get_api_data("/stats/categories")
    if cat_stats:
        categories = cat_stats["categorias"]
        
        # Preparar dados para visualização (sem pandas)
        categories_data = []
        for cat in categories:
            categories_data.append({
                "Categoria": cat["categoria"],
                "Total Livros": cat["total_livros"],
                "Preço Médio": cat["preco_medio"],
                "Preço Mínimo": cat["preco_minimo"],
                "Preço Máximo": cat["preco_maximo"]
            })
        
        # Top 10 categorias por quantidade
        st.subheader("🏆 Top 10 Categorias por Quantidade")
        top_categories = categories_data[:10]  # Já vem ordenado da API
        
        # Preparar dados para o gráfico
        cat_names = [cat["Categoria"] for cat in top_categories]
        cat_totals = [cat["Total Livros"] for cat in top_categories]
        
        fig = px.bar(
            x=cat_totals,
            y=cat_names,
            orientation='h',
            title="Categorias com Mais Livros",
            labels={'x': 'Total Livros', 'y': 'Categoria'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Preços por categoria
        st.subheader("💰 Preços Médios por Categoria")
        cat_prices = [cat["Preço Médio"] for cat in top_categories]
        
        fig2 = px.scatter(
            x=cat_prices,
            y=cat_totals,
            size=cat_totals,
            hover_name=cat_names,
            title="Relação entre Preço Médio e Quantidade de Livros",
            labels={'x': 'Preço Médio', 'y': 'Total Livros'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tabela detalhada
        st.subheader("📋 Tabela Detalhada")
        st.dataframe(categories_data, use_container_width=True)

# Página Buscar Livros
elif page == "🔍 Buscar Livros":
    st.header("🔍 Buscar Livros")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title_search = st.text_input("🔤 Buscar por título:")
    
    with col2:
        category_search = st.text_input("📂 Buscar por categoria:")
    
    if st.button("🔍 Buscar") and (title_search or category_search):
        params = []
        if title_search:
            params.append(f"title={title_search}")
        if category_search:
            params.append(f"category={category_search}")
        
        search_endpoint = f"/books/search?{'&'.join(params)}"
        search_results = get_api_data(search_endpoint)
        
        if search_results:
            st.success(f"✅ Encontrados {search_results['total']} livros")
            
            # Mostrar resultados
            for book in search_results["livros"]:
                with st.expander(f"📖 {book['titulo']} - £{book['preco']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Categoria:** {book['categoria']}")
                        st.write(f"**Preço:** £{book['preco']}")
                        st.write(f"**Rating:** {'⭐' * book['rating']} ({book['rating']}/5)")
                        st.write(f"**Disponibilidade:** {book['disponibilidade']}")
                    
                    with col2:
                        st.image(book['imagem_url'], width=150)

# Página Top Rated
elif page == "⭐ Top Rated":
    st.header("⭐ Livros Mais Bem Avaliados")
    
    top_books = get_api_data("/books/top-rated")
    if top_books:
        st.success(f"✅ {len(top_books)} livros com rating máximo")
        
        # Grid de livros
        cols = st.columns(3)
        for idx, book in enumerate(top_books):
            with cols[idx % 3]:
                st.subheader(f"📖 {book['titulo']}")
                st.image(book['imagem_url'], width=200)
                st.write(f"**Preço:** £{book['preco']}")
                st.write(f"**Rating:** {'⭐' * book['rating']}")
                st.write(f"**Categoria:** {book['categoria']}")
                st.write(f"**Disponibilidade:** {book['disponibilidade']}")
                st.divider()

# Página Filtro por Preço
elif page == "💰 Filtro por Preço":
    st.header("💰 Filtrar Livros por Preço")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_price = st.number_input("💵 Preço Mínimo (£):", min_value=0.0, value=0.0, step=1.0)
    
    with col2:
        max_price = st.number_input("💰 Preço Máximo (£):", min_value=0.0, value=100.0, step=1.0)
    
    if st.button("🔍 Filtrar"):
        if min_price <= max_price:
            filter_endpoint = f"/books/price-range?min={min_price}&max={max_price}"
            filtered_books = get_api_data(filter_endpoint)
            
            if filtered_books:
                st.success(f"✅ {filtered_books['total']} livros encontrados na faixa £{min_price} - £{max_price}")
                
                # Preparar dados para análise (sem pandas)
                books_data = []
                prices = []
                for book in filtered_books["livros"]:
                    books_data.append({
                        "Título": book["titulo"],
                        "Preço": book["preco"],
                        "Rating": book["rating"],
                        "Categoria": book["categoria"],
                        "Disponibilidade": book["disponibilidade"]
                    })
                    prices.append(book["preco"])
                
                # Gráfico de distribuição de preços
                st.subheader("📊 Distribuição de Preços")
                fig = px.histogram(
                    x=prices,
                    nbins=20,
                    title="Distribuição de Preços dos Livros Filtrados",
                    labels={'x': 'Preço', 'y': 'Quantidade'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de resultados
                st.subheader("📋 Livros Encontrados")
                st.dataframe(books_data, use_container_width=True)
        else:
            st.error("❌ O preço mínimo deve ser menor ou igual ao preço máximo!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("📚 **Books Dashboard**")
st.sidebar.markdown("Desenvolvido com Streamlit")
