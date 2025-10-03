# Books to Scrape - Web Scraper

Este projeto contém um web scraper em Python para extrair informações de todos os livros do site [Books to Scrape](https://books.toscrape.com/).

## Funcionalidades

O scraper extrai as seguintes informações de cada livro:
- **Título**: Nome completo do livro
- **Preço**: Valor em libras (£)
- **Rating**: Avaliação de 1 a 5 estrelas
- **Disponibilidade**: Status de estoque
- **Categoria**: Gênero/categoria do livro
- **Imagem**: URL da capa do livro

## Instalação

1. Navegue até a pasta data:
```bash
cd data
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o scraper a partir da pasta data:
```bash
python3 books_scraper.py
```

O script irá:
1. Descobrir automaticamente todas as páginas do site
2. Extrair informações de todos os livros
3. Salvar os dados em `books_data.csv` na pasta atual

## Estrutura do Projeto

```
trabalho-pos/
├── README.md
├── venv/ (ambiente virtual)
└── data/
    ├── requirements.txt
    ├── books_scraper.py
    ├── books_data.csv (gerado após execução)
    └── books_data_partial.csv (gerado se interrompido)
```

## Características do Scraper

- **Navegação automática**: Descobre e processa todas as páginas automaticamente
- **Tratamento de erros**: Continua funcionando mesmo se alguns livros falharem
- **Rate limiting**: Inclui pausas para ser respeitoso com o servidor
- **Dados estruturados**: Salva em formato CSV para fácil análise
- **Estatísticas**: Mostra resumo dos dados coletados

## Exemplo de Dados Extraídos

| titulo | preco | rating | disponibilidade | categoria | imagem_url |
|--------|-------|--------|-----------------|-----------|------------|
| A Light in the Attic | 51.77 | 3 | 22 disponível | Poetry | https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg |