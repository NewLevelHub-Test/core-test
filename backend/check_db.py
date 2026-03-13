from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"Найдено таблиц: {len(tables)}")
    print(f"Список таблиц: {', '.join(tables)}")
    
    if len(tables) >= 14:
        print("\n Все таблицы на месте")
    else:
        print(f"\n Найдено только {len(tables)} таблиц")