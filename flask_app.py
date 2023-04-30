from flask import Flask

import table.Model as DB

# create_app은 플라스크 내부에서 정의된 함수명이다.
# def create_app():
if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get('DB_URL')
    # initialize the app with the extension
    DB.db.init_app(app)

    with app.app_context():
        DB.db.create_all()

    import views.main_views as main_views
    import views.dish_views as dish_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(dish_views.bp)

    app.run()

