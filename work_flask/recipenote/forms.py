# ▼▼▼ リスト 11-2の修正 ▼▼▼
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from models import Recipe, User
from flask_login import current_user

# ▲▲▲ リスト 11-2の修正 ▲▲▲

# ==================================================
# Formクラス
# ==================================================

# ▼▼▼ リスト 11-2の追加 ▼▼▼
# ログイン用入力クラス
class LoginForm(FlaskForm):
    username = StringField('ユーザー名：', 
                           validators=[DataRequired('ユーザー名は必須入力です'),Length(4,10,"ユーザー名の長さは4文字以上10文字以内です")])
    # パスワード：パスワード入力
    password = PasswordField('パスワード: ',
                             validators=[Length(4, 10,
                                    'パスワードの長さは4文字以上10文字以内です')])
    # ボタン
    submit = SubmitField('ログイン')
    
    # カスタムバリデータ
    # 英数字と記号が含まれているかチェックする
    def validate_password(self, password):
        if not (any(c.isalpha() for c in password.data) and \
            any(c.isdigit() for c in password.data) and \
            any(c in '!@#$%^&*()' for c in password.data)):
            raise ValidationError('パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります')
        
        

# サインアップ用入力クラス
class SignUpForm(LoginForm):
    # ボタン
    submit = SubmitField('サインアップ')

    # カスタムバリデータ
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('そのユーザー名は既に使用されています')
# ▲▲▲ リスト 11-2の追加 ▲▲▲



# ▼▼▼ リスト 14-6の追加 ▼▼▼
# Wiki用入力クラス
class WikiForm(FlaskForm):
    # タイトル
    keyword = StringField('検索ワード：', render_kw={"placeholder": "入力してください"})
    # ボタン
    submit = SubmitField('Wiki検索')
# ▲▲▲ リスト 14-6の追加 ▲▲▲


class RecipeForm(FlaskForm):
    # タイトル
    title = StringField('料理名：', validators=[DataRequired('タイトルは必須入力です'), 
                            Length(max=30, message='30文字以下で入力してください')])
    # メモ
    content = TextAreaField('メモ：',validators=[Length(max=500,message='500文字以内で入力してください')])
    
    image_path = StringField("画像パス")
    # ボタン
    submit = SubmitField('送信')
    
    
        # 材料
    foods = StringField('材料1.',name="foods[]",id="foods1")
    
    quantity = StringField('分量',name="quantity[]",id="quantity1")
    

    
    process_content = TextAreaField('手順1.',name="process[]",id="process1")
    
    # カスタムバリデータ
    def validate_title(self, title):
        # StringFieldオブジェクトではなく、その中のデータ（文字列）をクエリに渡す必要があるため
        # 以下のようにtitle.dataを使用して、StringFieldから実際の文字列データを取得する
        query = Recipe.query.filter_by(title=title.data, user_id = current_user.id)
        if hasattr(self, "recipe_id") and self.recipe_id:
            query = query.filter(Recipe.id != self.recipe_id)
        
        recipe = query.first()
        if recipe:
            raise ValidationError(f"タイトル '{title.data}' は既に存在します。\
                                  別のタイトルを入力してください。")



class FoodsForm(FlaskForm):
    # 材料
    foods = StringField('材料')
    
    quantity = StringField('分量')
    
class Process_contentForm(FlaskForm):
    
    process_content = TextAreaField('作り方')
    