from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

app = FastAPI()

# Permite que o frontend (JS) comunique com este backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, coloque o domínio do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- BASE DE DADOS (Em Memória para simular o estado inicial) ---
# --- BASE DE DADOS (Em Memória para simular o estado inicial) ---
db = {
    "users": [
        { "id": 1, "username": 'lucas', "password": '123', "photo": 'https://i.pravatar.cc/150?u=lucas', "name": 'Lucas' },
        { "id": 2, "username": 'roberto', "password": '123', "photo": 'https://i.pravatar.cc/150?u=roberto', "name": 'Roberto' },
        { "id": 3, "username": 'daniel', "password": '123', "photo": 'https://i.pravatar.cc/150?u=daniel', "name": 'Daniel' },
        { "id": 4, "username": 'gabriel', "password": '123', "photo": 'https://i.pravatar.cc/150?u=gabriel', "name": 'Gabriel' },
        { "id": 5, "username": 'lucas_brenner', "password": '123', "photo": 'https://i.pravatar.cc/150?u=lucas_brenner', "name": 'Lucas Brenner' }
    ],
    "books": [
        { "id": 1, "title": 'Admirável Mundo Novo', "author": 'Aldous Huxley', "totalPages": 311, "totalChapters": 18, "currentProgress": 0, "cover": 'https://upload.wikimedia.org/wikipedia/en/6/62/BraveNewWorld_FirstEdition.jpg', "isClubBook": True, "owner": 'Clube' },
        { "id": 2, "title": 'As Nuvens', "author": 'Aristófanes', "totalPages": 150, "totalChapters": 5, "currentProgress": 0, "cover": 'https://covers.openlibrary.org/b/id/8316132-L.jpg', "isClubBook": True, "owner": 'Clube' },
        { "id": 3, "title": '1984', "author": 'George Orwell', "totalPages": 328, "totalChapters": 24, "currentProgress": 0, "cover": 'https://covers.openlibrary.org/b/id/153256-L.jpg', "isClubBook": True, "owner": 'Clube' },
        { "id": 4, "title": 'O Investidor de Bom Senso', "author": 'John C. Bogle', "totalPages": 216, "totalChapters": 18, "currentProgress": 216, "cover": 'https://covers.openlibrary.org/b/id/12534505-L.jpg', "isClubBook": False, "owner": 'Clube' },
        { "id": 5, "title": 'Freakonomics', "author": 'Steven Levitt & Stephen Dubner', "totalPages": 320, "totalChapters": 6, "currentProgress": 320, "cover": 'https://upload.wikimedia.org/wikipedia/en/6/63/Freakonomics.jpg', "isClubBook": False, "owner": 'Clube' },
        { "id": 6, "title": 'A Morte de Ivan Ilitch', "author": 'Liev Tolstói', "totalPages": 100, "totalChapters": 12, "currentProgress": 100, "cover": 'https://covers.openlibrary.org/b/id/12613589-L.jpg', "isClubBook": False, "owner": 'Clube' }
    ]
}

# --- MODELOS DE DADOS PARA RECEBER REQUESTS ---
class BookCreate(BaseModel):
    title: str
    author: str
    cover: str
    totalPages: int
    totalChapters: int

class ProgressUpdate(BaseModel):
    progress: int

# --- ENDPOINTS DA API (Substituem os Services do JS) ---

@app.get("/users/{username}")
def get_user(username: str):
    user = next((u for u in db["users"] if u["username"].lower() == username.lower()), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/books/club")
def get_club_books():
    return [b for b in db["books"] if b.get("isClubBook")]

@app.get("/books/external")
def get_external_books():
    return [b for b in db["books"] if not b.get("isClubBook")]

@app.put("/books/{book_id}/progress")
def update_progress(book_id: int, data: ProgressUpdate):
    for book in db["books"]:
        if book["id"] == book_id:
            book["currentProgress"] = data.progress
            return {"status": "success", "new_progress": data.progress}
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books/club")
def add_club_book(book: BookCreate):
    new_book = {
        "id": int(time.time() * 1000),
        "title": book.title,
        "author": book.author,
        "cover": book.cover,
        "totalPages": book.totalPages,
        "totalChapters": book.totalChapters,
        "currentProgress": 0,
        "isClubBook": True,
        "owner": 'Clube'
    }
    db["books"].append(new_book)
    return {"status": "success", "book": new_book}

# --------------------------------------------------------------------------------------------------------------------------


# 1. NOVO MODELO: Para os livros pessoais
class BookCreateExternal(BaseModel):
    title: str
    author: str
    cover: str
    totalPages: int
    owner: str

# 2. NOVA ROTA: Buscar no Google Books (A lógica do seu escavator.py)
@app.get("/books/search")

def search_books(q: str):
    url = "https://www.googleapis.com/books/v1/volumes"
    
    # Parâmetros limpos: NENHUMA chave de API será enviada
    params = {
        "q": q,
        "maxResults": 12
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"[ERRO GOOGLE BOOKS] Status: {response.status_code} | Resposta: {response.text}")
        return []
        
    data = response.json()
    results = []
    
    for item in data.get("items", []):
        vol = item.get("volumeInfo", {})
        
        image_links = vol.get("imageLinks") or {}
        cover_url = image_links.get("thumbnail", "https://placehold.co/150x225/2c3440/9ab?text=Sem+Capa")
        cover_url = cover_url.replace("http://", "https://")
        
        results.append({
            "id": item.get("id"),
            "title": vol.get("title", "Sem Título"),
            "author": ", ".join(vol.get("authors", [])) if vol.get("authors") else "Autor Desconhecido",
            "cover": cover_url,
            "totalPages": vol.get("pageCount", 200)
        })
        
    return results

#def search_books(q: str):
   # url = "https://www.googleapis.com/books/v1/volumes"
    
    # O 'requests' vai formatar os espaços e acentos automaticamente
   # params = {
   #    "q": q,
    #    "maxResults": 12,
    #    "key": GOOGLE_BOOKS_API_KEY # Usando a chave para evitar bloqueios
    #}
    
    #response = requests.get(url, params=params)
    
    # Se não for 200, imprime o erro no terminal para facilitar o debug
   # if response.status_code != 200:
    #    print(f"[ERRO GOOGLE BOOKS] Status: {response.status_code} | Resposta: {response.text}")
   #     return []
        
    #data = response.json()
    #results = []
    
    #for item in data.get("items", []):
     #   vol = item.get("volumeInfo", {})
        
        # O 'or {}' previne um erro caso o Google retorne "imageLinks": null no JSON
      #  image_links = vol.get("imageLinks") or {}
      #  cover_url = image_links.get("thumbnail", "https://placehold.co/150x225/2c3440/9ab?text=Sem+Capa")
      #  cover_url = cover_url.replace("http://", "https://")
        
     #   results.append({
     #       "id": item.get("id"),
     #       "title": vol.get("title", "Sem Título"),
     #       "author": ", ".join(vol.get("authors", [])) if vol.get("authors") else "Autor Desconhecido",
     #       "cover": cover_url,
     #       "totalPages": vol.get("pageCount", 200)
    #    })
        
    #return results


# 3. NOVA ROTA: Guardar livro na Minha Biblioteca
@app.post("/books/external")
def add_external_book(book: BookCreateExternal):
    new_book = {
        "id": int(time.time() * 1000),
        "title": book.title,
        "author": book.author,
        "cover": book.cover,
        "totalPages": book.totalPages,
        "totalChapters": 1, # Livros externos podem não ter capítulos definidos
        "currentProgress": 0,
        "isClubBook": False, # Define que NÃO é do clube (apenas Pessoal/Central)
        "owner": book.owner
    }
    db["books"].append(new_book)
    return {"status": "success", "book": new_book}