from flask import Blueprint, render_template, request, redirect, url_for, flash,current_app
from models import db, Recipe, User, Foods, Process
from forms import RecipeForm, FoodsForm, Process_contentForm, LoginForm, SignUpForm
from flask_login import login_required, current_user  # <= リスト13-2追加

#https://qiita.com/keimoriyama/items/7c935c91e95d857714fb
#↑を参考に
import os
# request フォームから送信した情報を扱うためのモジュール
# redirect  ページの移動
# url_for アドレス遷移
from werkzeug.utils import secure_filename
# 画像のダウンロード
from flask import send_from_directory, abort

# memoのBlueprint
recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipe')
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}



# ==================================================
# ルーティング
# ==================================================
# 一覧
@recipe_bp.route("/")
@login_required
def index():
    # メモ全件取得
    user_id = current_user.id
    
    recipes = Recipe.query.filter_by(user_id=user_id).all()
    
    # 画面遷移
    return render_template("recipe/index.html", recipes=recipes)



@recipe_bp.route("/search",methods=["GET", "POST"])
@login_required
def search():
    user_id = current_user.id
    search_word = request.form.get("keyword")
    like_pattern = f"%{search_word}%"
    
    #ユーザーidでレシピを全件取得している
    recipe_full = Recipe.query.filter(
        Recipe.user_id == user_id
    ).all()
    
    #キーワードが含まれている、レシピのタイトルをログインユーザーで取得
    recipes = Recipe.query.filter(
        Recipe.user_id == user_id,
        (Recipe.title.ilike(like_pattern))
    ).all()
    
    recipe_ids = [r.id for r in recipe_full]
    
    
    #ログインユーザーから取得したレシピの中でキーワードが含まれているものを取得
    foods = Foods.query.filter(
        Foods.recipe_id.in_(recipe_ids),
        (Foods.foods.ilike(like_pattern))
    ).all()
    
    recipe_ids2= [r.id for r in recipes]
    # 材料から取得したレシピIDを取得する
    recipe_ids_from_foods = [f.recipe_id for f in foods]

    # タイトルからのレシピIDと合わせて、重複を除いてリスト化
    list_number = list(set(recipe_ids2 + recipe_ids_from_foods))
    list_number.sort()
    
    
    
    # food_ids = [a.id for a in foods]
    
    # list_number = list(set(recipe_ids2 + food_ids))
    # list_number.sort()
    # list_number = []
    # for a in recipes:
    #     list_number.append(a.id)
        
    # for a,c in zip(list_number,range(len(list_number))):
    #     for b in foods:
    #         if a.id != b.recipe_id :
    #             if a.id < b.recipe_id:
    #                 list_number.insert(c+1,a.id)
    #             else:
    #                 list_number.append(b.recipe_id)
            
    
    search_return = Recipe.query.filter(Recipe.id.in_(list_number)).all()
    
    return render_template("recipe/search_result.html", form=search_return,search_word=search_word,recipes=recipes,foods=foods)

    

# 写真をinstance配下から取り出しているだけ
@recipe_bp.route('/recipe_image/<int:user_id>/<filename>')
@login_required
def user_image(user_id, filename):
    if current_user.id != user_id:
        abort(403)
    
    folder_path = os.path.join(current_app.root_path, "instance", "recipe_images", str(user_id))
    return send_from_directory(folder_path, filename)

# 登録（Form使用）
@recipe_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    

    
    
    # Formインスタンス生成
    form = RecipeForm(request.form)
    user_id = current_user.id
    db_up_path = ""
    if form.validate_on_submit():
        # データ入力取得
        # recipeのdatabase
        title = form.title.data
        content = form.content.data
        uploadpath = form.image_path.data
        
        
        foods_list = request.form.getlist('foods[]')
        

        # 空欄禁止チェック
        for i, food in enumerate(foods_list):
            if not food.strip():
                flash(f"材料{i + 1}は必須入力です。","danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
                
        
        
        # 材料の文字数チェック（空欄は前段でチェック済み）
        for i, food in enumerate(foods_list):
            if len(food.strip()) > 30:
                flash(f"材料{i + 1}は30文字以内で入力してください。", "danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))

        # 重複チェック（オプション）
        if len(foods_list) != len(set([f.strip() for f in foods_list])):
            flash("同じ材料が重複しています。")
            return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
            
        
        quantity_list = request.form.getlist('quantity[]')
        # 分量の文字数チェック

        for i,quantity in enumerate(quantity_list):  # または request.form.getlist('quantity[]')
            if quantity.strip() and len(quantity.strip()) > 30:
                flash(f"分量{i + 1}は30文字以内で入力してください。", "danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))  # 入力値を保持して元のページに戻る

        
        for i, food in enumerate(quantity_list):
            if not food.strip():
                flash(f"分量{i + 1}は必須入力です。","danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        process_step_raw = request.form.getlist("process_text[]")
        steps = [step.strip()for step in process_step_raw if step.strip()]
        process_length = len(steps)
        # 更新や登録処理の直前にチェック
        
        
        # 手順（process_text[]）空欄と文字数チェック
        process_raw_list = request.form.getlist('process_text[]')
        for i, step in enumerate(process_raw_list):
            if not step.strip():
                flash(f"作り方{i + 1}は必須入力です。", "danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=foods_list,
                    quantity_list=quantity_list,
                    process_list=process_raw_list)
                
        for step in steps:  # または new_process_data
            if len(step) > 100:
                flash("作り方", "danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))  # 元のページに戻るなど適宜処理
        recipe_id = 1
        user_id = current_user.id
        recipe = Foods.query.all()
        recipe_data = []
        if recipe:
            for recipe_id_num in recipe:
                recipe_data.append(int(recipe_id_num.recipe_id))
            
            max_recipe_id = max(recipe_data)
            
            recipe_id = max_recipe_id + 1
            
        

        file = request.files.get("file")
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("許可されていない画像形式です（jpg, jpeg, png, gifのみ可）","danger")
                return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
            
            original_filename = secure_filename(file.filename)
            _, ext = os.path.splitext(original_filename)  # ← .jpg や .png などを取得
            filename = f"{recipe_id}_{user_id}{ext}"      # ← 拡張子つきで保存名を作る
            folder_path = os.path.join(current_app.root_path, "instance","recipe_images" , str(user_id))
            
            os.makedirs(folder_path, exist_ok=True)  # フォルダなければ作成
            uploadpath = os.path.join(folder_path, filename)
            db_up_path = os.path.join("recipe_images", str(user_id),filename).replace("\\","/")
            file.save(uploadpath)
            
            



        #processのdatabase
        process_content = form.process_content.data
        

        #foodsのdatabase
        for a in range(len(foods_list)):
            foods = request.form.getlist('foods[]')[a]
            quantity = request.form.getlist('quantity[]')[a]
            foods = Foods(foods=foods,quantity=quantity,recipe_id=recipe_id)
            db.session.add(foods)
            
        
        for step in steps:
            
            process_class = Process(process_content=step, recipe_id=recipe_id)
            db.session.add(process_class)
        #recipe_id
        
        
        recipe = Recipe(title=title, content=content, user_id=user_id,image_path=db_up_path)
        
        # 登録処理
        
        db.session.add(recipe)
        db.session.commit()
        # フラッシュメッセージ
        flash("登録しました")          
        # 画面遷移
        return redirect(url_for("recipe.index"))
    # GET時
    # 画面遷移
    #return render_template("recipe/create_form.html", form=form)
    return render_template("recipe/create_form.html", form=form,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))

@recipe_bp.route("/update/<int:recipe_id>", methods=["GET", "POST"])
@login_required
def update(recipe_id):
    user_id = current_user.id
    target_data = Recipe.query.get_or_404(recipe_id)

    foods_data = Foods.query.filter_by(recipe_id=recipe_id).all()
    process_data = Process.query.filter_by(recipe_id=recipe_id).all()

    form = RecipeForm(obj=target_data)
    form.recipe_id = target_data.id

    # POST時
    if request.method == 'POST' and form.validate():
        new_foods_data = request.form.getlist("foods[]")
        new_quantity_data = request.form.getlist("quantity[]")
        new_process_data = request.form.getlist("process_text[]")

        # === バリデーションチェック ===
        
        # 材料：空欄チェック
        for i, food in enumerate(new_foods_data):
            if not food.strip():
                flash(f"材料{i + 1}は必須入力です。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )

        # 材料：文字数チェック
        for i, food in enumerate(new_foods_data):
            if len(food.strip()) > 30:
                flash(f"材料{i + 1}は30文字以内で入力してください。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )
                

        # 材料：重複チェック
        if len(new_foods_data) != len(set([f.strip() for f in new_foods_data])):
            flash("同じ材料が重複しています。", "danger")
            return render_template("recipe/update_form.html",
                form=form,
                edit_id=target_data.id,
                foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                process_data=[{"process_content": p} for p in new_process_data],
                image_path=target_data.image_path
            )


        # 分量：文字数チェック
        for i, quantity in enumerate(new_quantity_data):
            quantity = quantity.strip()
            if quantity and len(quantity) > 30:
                flash(f"分量{i + 1}は30文字以内で入力してください。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )


        # 分量：空欄チェック
        for i, qty in enumerate(new_quantity_data):
            if not qty.strip():
                flash(f"分量{i + 1}は必須入力です。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )

        
        # 手順：空欄チェック
        for i, step in enumerate(new_process_data):
            if not step.strip():
                flash(f"作り方{i + 1}は必須入力です。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )


        # 手順：文字数チェック（100文字以内）
        for i, step in enumerate(new_process_data):
            if len(step.strip()) > 100:
                flash(f"作り方{i + 1}は100文字以内で入力してください。", "danger")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )



        

        # === 画像処理 ===
        file = request.files.get("file")
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("許可されていない画像形式です（jpg, jpeg, png, gifのみ可）")
                return render_template("recipe/update_form.html",
                    form=form,
                    edit_id=target_data.id,
                    foods_data=[{"foods": f, "quantity": q} for f, q in zip(new_foods_data, new_quantity_data)],
                    process_data=[{"process_content": p} for p in new_process_data],
                    image_path=target_data.image_path
                )

            original_filename = secure_filename(file.filename)
            _, ext = os.path.splitext(original_filename)
            filename = f"{recipe_id}_{current_user.id}{ext}"
            folder_path = os.path.join(current_app.root_path, "instance", "recipe_images", str(current_user.id))
            os.makedirs(folder_path, exist_ok=True)
            uploadpath = os.path.join(folder_path, filename)
            db_up_path = os.path.join("recipe_images", str(current_user.id), filename).replace("\\", "/")
            file.save(uploadpath)
            target_data.image_path = db_up_path
            
        if request.form.get("delete_image") == "1":
            target_data.image_path = ""

        # === DB更新 ===
        target_data.title = form.title.data
        target_data.content = form.content.data

        # 一旦古いデータ削除
        for f in foods_data:
            db.session.delete(f)
        for p in process_data:
            db.session.delete(p)

        # 新しい材料データ登録
        for f, q in zip(new_foods_data, new_quantity_data):
            db.session.add(Foods(foods=f, quantity=q, recipe_id=recipe_id))
            
        raw_process_list = request.form.getlist("process_text[]")
        cleaned_process = [step.strip() for step in raw_process_list if step.strip()]
        
        # 新しい手順データ登録
        for step in cleaned_process:
            db.session.add(Process(process_content=step, recipe_id=recipe_id))

        db.session.commit()
        flash("変更しました")
        return redirect(url_for("recipe.index"))

    #GET時（初回表示）
    return render_template("recipe/update_form.html",
        form=form,
        edit_id=target_data.id,
        foods_data=foods_data,
        process_data=process_data,
        image_path=target_data.image_path
    )
    
    
    
"""
# 更新（Form使用）
@recipe_bp.route("/update/<int:recipe_id>", methods=["GET", "POST"])
def update(recipe_id):
    # データベースからrecipe_idに一致するメモを取得し、
    # 見つからない場合は404エラーを表示
    user_id = current_user.id
    target_data = Recipe.query.get_or_404(recipe_id)
    
    foods_data = Foods.query.filter_by(recipe_id=recipe_id).all()
    
    #foods_length = len(foods_data)
    process_data = Process.query.filter_by(recipe_id=recipe_id).all()
    #process_length = len(process_data)
    print(foods_data)
    
    
    for a in foods_data:
        print(a)
        
    
    form = RecipeForm(obj=target_data)
    form.recipe_id = target_data.id
    form_foods = FoodsForm(obj=foods_data)
    form_process = Process_contentForm(obj=process_data)
    print(f"foods_data: {foods_data}")
    print(f"process_data: {process_data}")
    
    if request.method == 'POST' and form.validate():
        #foods、quantity、processは追加削除したりするから更新の仕方わかんないな～って、、、、一旦そのデータを削除して入れなおせばいいのでは魂胆です
        new_foods_data = request.form.getlist("foods[]")
        new_quantity_data = request.form.getlist("quantity[]")
        # 空欄禁止チェック
        for i, food in enumerate(new_foods_data):
            if not food.strip():
                flash(f"材料{i + 1}は必須入力です。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        # 重複チェック（オプション）
        if len(new_foods_data) != len(set([f.strip() for f in new_foods_data])):
            flash("同じ材料が重複しています。")
            return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        quantity_list = new_quantity_data
        for i, food in enumerate(quantity_list):
            if not food.strip():
                flash(f"分量{i + 1}は必須入力です。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        
        
        for a in range(len(new_foods_data)):
            foods = request.form.getlist('foods[]')[a]
            quantity = request.form.getlist('quantity[]')[a]
            foods = Foods(foods=foods,quantity=quantity,recipe_id=recipe_id)
            db.session.add(foods)
        new_process_data = request.form.getlist("process_text[]")
        new_process_data = [step.strip() for step in new_process_data if step.strip()]
        for step in new_process_data:  # または new_process_data
            if len(step) > 100:
                flash("手順は100文字以内で入力してください。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
            
        
        file = request.files.get("file")
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("許可されていない画像形式です（jpg, jpeg, png, gifのみ可）")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))

            original_filename = secure_filename(file.filename)
            _, ext = os.path.splitext(original_filename)
            filename = f"{recipe_id}_{current_user.id}{ext}"
            folder_path = os.path.join(current_app.root_path, "instance", "recipe_images", str(current_user.id))
            os.makedirs(folder_path, exist_ok=True)
            uploadpath = os.path.join(folder_path, filename)
            db_up_path = os.path.join("recipe_images", str(current_user.id), filename).replace("\\", "/")
            file.save(uploadpath)
            # 更新対象のレシピ画像パスを変更
            target_data.image_path = db_up_path

        # 変更処理
        target_data.title = form.title.data
        target_data.content = form.content.data
        
        
        
        
        
        
        for a in foods_data:
            db.session.delete(a)
            
        for a in process_data:
            db.session.delete(a)
        
        
        for a in range(len(new_foods_data)):
            
            foods = new_foods_data[a]
            quantity = new_quantity_data[a]
            foods_list = Foods(foods=foods,quantity=quantity,recipe_id=recipe_id)
            db.session.add(foods_list)
            
            
        
        for a in new_process_data:
            
            
            process_content = a
            process_class = Process(process_content=process_content, recipe_id=recipe_id)
            db.session.add(process_class)
        db.session.commit()
        #print(Foods.query.filter_by(recipe_id=recipe_id).all())
        # フラッシュメッセージ
        flash("変更しました")        
        # 画面遷移
        return redirect(url_for("recipe.index"))
    # GET時
    # 画面遷移
    #return render_template("recipe/update_form.html", form=form, edit_id = target_data.id,foods_data = foods_data,process_data=process_data)
    return render_template("recipe/update_form.html", form=form, edit_id = target_data.id,foods_data = foods_data,process_data=process_data,image_path=form.image_path)
"""
# 削除
@recipe_bp.route("/delete/<int:recipe_id>")
@login_required
def delete(recipe_id):
    # データベースからrecipe_idに一致するメモを取得し、
    # 見つからない場合は404エラーを表示
    recipe = Recipe.query.get_or_404(recipe_id)
    foods = Foods.query.filter_by(recipe_id=recipe_id).all()
    process = Process.query.filter_by(recipe_id=recipe_id).all()
    
    for a in foods:
        db.session.delete(a)
        
    for a in process:
        db.session.delete(a)
    
    # 削除処理
    db.session.delete(recipe)
    
    
    db.session.commit()
    # フラッシュメッセージ
    flash("削除しました")
    # 画面遷移
    return redirect(url_for("recipe.index"))


# wiki結果反映
@recipe_bp.route('/create_from_search', methods=['POST'])
@login_required
def create_from_search():
    # 入力値の取得
    title = request.form['title']
    content = request.form['content']
    new_memo = Recipe(title=title, content=content, user_id=current_user.id)
    # 追加処理
    db.session.add(new_memo)
    db.session.commit()
    # フラッシュメッセージ
    flash("wikiからデータ登録しました")          
    # 画面遷移
    return redirect(url_for("memo.index"))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






"""
# 更新（Form使用）
@recipe_bp.route("/update/<int:recipe_id>", methods=["GET", "POST"])
def update(recipe_id):
    # データベースからrecipe_idに一致するメモを取得し、
    # 見つからない場合は404エラーを表示
    user_id = current_user.id
    target_data = Recipe.query.get_or_404(recipe_id)
    
    foods_data = Foods.query.filter_by(recipe_id=recipe_id).all()
    
    #foods_length = len(foods_data)
    process_data = Process.query.filter_by(recipe_id=recipe_id).all()
    #process_length = len(process_data)
    print(foods_data)
    
    
    for a in foods_data:
        print(a)
  

    書いたけど不必要になった
    print(foods_data)
    foods_data_foods = []
    
    for a in foods_data:
        foods_data_foods.append(a.foods)
        
    
    foods_data_quantity = []
    for a in foods_data:
        foods_data_quantity.append(a.quantity)

    process_data = Process.query.filter_by(recipe_id=recipe_id).all()
    process_data_process = []
    for a in process_data:
        process_data_process.append(a.process_content)
    
    
    
    これだと辞書型ふぁからfood.titleみたいな感じで参照できない
    recipe_data = {
        'title': target_data.title,
        'content': target_data.content,
        'foods': foods_data_foods,
        'quantity': foods_data_quantity,
        'process_content': process_data_process,
        
    }
    form = RecipeForm(obj = recipe_data)
    
    
    form = RecipeForm(obj=target_data)
    form.recipe_id = target_data.id
    form_foods = FoodsForm(obj=foods_data)
    form_process = Process_contentForm(obj=process_data)
    print(f"foods_data: {foods_data}")
    print(f"process_data: {process_data}")
    
    #これだと
    # Formに入れ替え
    #foods_form = FoodsForm(obj=foods_data)
    
    #process_form = Process_contentForm(obj=process_data)
    #foods = FoodsForm(foods_list)   
    if request.method == 'POST' and form.validate():
        print("たのみ～～～～～")
        print(request.form)
        
        file = request.files.get("file")
        if file and file.filename != "":
            if not allowed_file(file.filename):
                flash("許可されていない画像形式です（jpg, jpeg, png, gifのみ可）")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))

            original_filename = secure_filename(file.filename)
            _, ext = os.path.splitext(original_filename)
            filename = f"{recipe_id}_{current_user.id}{ext}"
            folder_path = os.path.join(current_app.root_path, "instance", "recipe_images", str(current_user.id))
            os.makedirs(folder_path, exist_ok=True)
            uploadpath = os.path.join(folder_path, filename)
            db_up_path = os.path.join("recipe_images", str(current_user.id), filename).replace("\\", "/")
            file.save(uploadpath)
            # 更新対象のレシピ画像パスを変更
            target_data.image_path = db_up_path

        # 変更処理
        target_data.title = form.title.data
        target_data.content = form.content.data
        
        
        #foods、quantity、processは追加削除したりするから更新の仕方わかんないな～って、、、、一旦そのデータを削除して入れなおせばいいのでは魂胆です
        new_foods_data = request.form.getlist("foods[]")
        new_quantity_data = request.form.getlist("quantity[]")
        
        # 空欄禁止チェック
        for i, food in enumerate(new_foods_data):
            if not food.strip():
                flash(f"材料{i + 1}は必須入力です。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        # 重複チェック（オプション）
        if len(new_foods_data) != len(set([f.strip() for f in new_foods_data])):
            flash("同じ材料が重複しています。")
            return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        
        quantity_list = new_quantity_data
        for i, food in enumerate(quantity_list):
            if not food.strip():
                flash(f"分量{i + 1}は必須入力です。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        
        
        for a in range(len(new_foods_data)):
            foods = request.form.getlist('foods[]')[a]
            quantity = request.form.getlist('quantity[]')[a]
            foods = Foods(foods=foods,quantity=quantity,recipe_id=recipe_id)
            db.session.add(foods)
        new_process_data = request.form.getlist("process_text[]")
        new_process_data = [step.strip() for step in new_process_data if step.strip()]
        for step in new_process_data:  # または new_process_data
            if len(step) > 100:
                flash("手順は100文字以内で入力してください。")
                return render_template("recipe/update_form.html", form=form,
                    edit_id=target_data.id,
                    foods_list=request.form.getlist('foods[]'),
                    quantity_list=request.form.getlist('quantity[]'),
                    process_list=request.form.getlist('process_text[]'))
        #print(new_foods_data)
        #print(new_quantity_data)
        #print(new_process_data)
        for a in foods_data:
            db.session.delete(a)
            
        for a in process_data:
            db.session.delete(a)
        
        
        for a in range(len(new_foods_data)):
            
            foods = new_foods_data[a]
            quantity = new_quantity_data[a]
            foods_list = Foods(foods=foods,quantity=quantity,recipe_id=recipe_id)
            db.session.add(foods_list)
            
            
        
        for a in new_process_data:
            
            
            process_content = a
            process_class = Process(process_content=process_content, recipe_id=recipe_id)
            db.session.add(process_class)
        db.session.commit()
        #print(Foods.query.filter_by(recipe_id=recipe_id).all())
        # フラッシュメッセージ
        flash("変更しました")        
        # 画面遷移
        return redirect(url_for("recipe.index"))
    # GET時
    # 画面遷移
    #return render_template("recipe/update_form.html", form=form, edit_id = target_data.id,foods_data = foods_data,process_data=process_data)
    return render_template("recipe/update_form.html", form=form, edit_id = target_data.id,foods_data = foods_data,process_data=process_data,image_path=form.image_path)
"""