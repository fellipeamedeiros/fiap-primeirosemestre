import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class AuthService:
    def __init__(self):
        self.SECRET_KEY = "primeiro-semestre"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
        
        # Usuário padrão (em produção, use um banco de dados)
        self.users = {
            "usuario": {
                "username": "usuario",
                "password": self._hash_password("teste")
            }
        }
        
        # Armazena refresh tokens válidos (em produção, use Redis ou banco de dados)
        self.valid_refresh_tokens = set()
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Autentica o usuário"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        return user["password"] == self._hash_password(password)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de acesso JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de refresh JWT"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        # Adiciona o token à lista de tokens válidos
        self.valid_refresh_tokens.add(encoded_jwt)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verifica e decodifica um token JWT"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            
            # Verifica se o tipo do token está correto
            if payload.get("type") != token_type:
                return None
            
            # Para refresh tokens, verifica se ainda está na lista de tokens válidos
            if token_type == "refresh" and token not in self.valid_refresh_tokens:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Realiza o login e retorna os tokens"""
        if not self.authenticate_user(username, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Dados para incluir no token
        token_data = {"sub": username}
        
        # Cria os tokens
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # em segundos
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Renova o token de acesso usando o refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Remove o refresh token antigo da lista de tokens válidos
        self.valid_refresh_tokens.discard(refresh_token)
        
        # Cria novos tokens
        token_data = {"sub": username}
        new_access_token = self.create_access_token(token_data)
        new_refresh_token = self.create_refresh_token(token_data)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": self.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # em segundos
        }
    
    def revoke_refresh_token(self, refresh_token: str):
        """Revoga um refresh token"""
        self.valid_refresh_tokens.discard(refresh_token)
