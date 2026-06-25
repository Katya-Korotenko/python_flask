from sqlalchemy import create_engine, String, Numeric, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,sessionmaker, relationship

# Задача 3: Определите модель продукта Product со следующими типами колонок:
# id: числовой идентификатор
# name: строка (макс. 100 символов)
# price: числовое значение с фиксированной точностью
# in_stock: логическое значение
# Задача 4: Определите связанную модель категории Category со следующими типами колонок:
# id: числовой идентификатор
# name: строка (макс. 100 символов)
# description: строка (макс. 255 символов)
# Задача 5: Установите связь между таблицами Product и Category с помощью колонки category_id.

engine = create_engine('sqlite:///:memory:')
LocalSession = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[ float] = mapped_column(Numeric( 10, 2), default= 0.00)
    in_stock: Mapped[bool]
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    category: Mapped['Category'] = relationship(back_populates="products")
    def __str__(self):
        return f'{self.id} {self.name} - {self.price} - {self.in_stock} - {self.category}'

    def __repr__(self):
        return f'name={self.name}-price={self.price}'


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    products: Mapped[list[Product]] = relationship(back_populates="category")

    def __str__(self):
        return f'{self.name} - {self.description}'


with engine.begin() as connection:
    Base.metadata.create_all(connection)

with LocalSession() as session:

    category_obst = Category(name="Vegetables", description="Fresh")
    category_fruits = Category(name="Fruits", description="Sweet and fresh")

    product1 = Product(name="Potatoes", price=1.99, in_stock=True, category=category_obst)
    product2 = Product(name="Tomatoes", price=1.56, in_stock=False, category=category_obst)
    product3 = Product(name="Mango", price=2.28, in_stock=True, category=category_fruits)
    product4 = Product(name="Apple", price=1.52, in_stock=True, category=category_fruits)


    session.add(product1)
    session.add(product2)
    session.add(product3)
    session.add(product4)
    session.commit()


with LocalSession() as session:
    sql_query = select(Product)
    products = session.execute(sql_query).scalars().all()

    print(*products, sep='\n')
