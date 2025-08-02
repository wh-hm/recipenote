from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import relationship

# Flask-SQLAlchemyの生成
db = SQLAlchemy()

# ==================================================
# モデル
# ==================================================

# ユーザー
class User(UserMixin, db.Model):
    # テーブル名
    __tablename__ = 'users'
    # ID（PK）    
    id = db.Column(db.Integer, primary_key=True)
    # ユーザー名
    username = db.Column(db.String(50), unique=True, nullable=False)
    # パスワード
    password = db.Column(db.String(120), nullable=False)
    
    # ▼▼▼ リスト13-1追加 ▼▼▼
    # Memo とのリレーション
    # リレーション: １対多
    recipes = db.relationship("Recipe", backref="users")
    # ▲▲▲ リスト13-1追加 ▲▲▲
    
    # パスワードをハッシュ化して設定する
    def set_password(self, password):
        self.password = generate_password_hash(password)
    # 入力したパスワードとハッシュ化されたパスワードの比較
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Recipe(db.Model):
    # テーブル名
    __tablename__ = 'recipe'
    # ID（PK）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # タイトル（NULL許可しない）
    title = db.Column(db.String(50), nullable=False)
    # 内容
    content = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    
class Foods(db.Model):
    
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    foods = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    

class Process(db.Model):
    __tablename__ = 'process'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    process_content = db.Column(db.String(100), nullable=False)
    recipe_id = db.Column(db.Integer,nullable=False)
    



"""
データベースメモ

「１」メイン：レシピ
ID,レシピ名、メモ、
主キー：ID

「２」材料
ID,材料名、分量名、１のIDと同じやつ
主キー:ID

「３」作り方
ID（順番）、作り方、１のIDと同じやつ
主キー:ID
"""