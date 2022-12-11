import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config

JWT_KEY = config("JWT_KEY")

class AuthJwtCsrf():
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret_key = JWT_KEY

    # ユーザーのPWを引数としてPWのハッシュ化を行う
    def generate_hashed_pw(self, password) -> str:
        return self.pwd_ctx.hash(password)
    
    # ユーザーがタイプしたPWとDBのPWの検証を実施
    def verify_pw(self, plain_pw, hashed_pw) -> bool:
        return self.pwd_ctx.verify(plain_pw, hashed_pw)
    
    # JWTを生成するメソッド
    def encode_jwt(self, email) -> str:
        payload = {
            # JWTの有効期限->5分後
            "exp": datetime.utcnow() + timedelta(days=0, minutes=5),
            # JWTの生成日時
            "iat": datetime.utcnow(),
            # ユーザーを一意に識別できるメールアドレス
            "sub": email
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm="HS256"
        )

    # JWTを解析してくれるメソッド
    def decode_jwt(self, token) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload["sub"]
        # JWTトークンが失効している場合
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401, detail="The JWT has expired."
            )
        # JWTのフォーマットに準拠していない場合、からのトークンの場合
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="JWT is not valid.")