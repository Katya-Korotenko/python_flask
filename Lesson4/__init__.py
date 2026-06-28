from sqlalchemy import create_engine, String, Numeric, ForeignKey, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,sessionmaker, relationship

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
        return f'{self.name}: {self.description}'




with engine.begin() as connection:
    Base.metadata.create_all(connection)

with LocalSession() as session:

    category_electronics = Category(name="Electronics", description="Gadgets and devices.")
    category_books = Category(name="Books", description="Printed and electronic books")
    category_clothing = Category(name="Clothing", description="Clothing for men and women")

    session.add_all([
        Product(name="Smartphone", price=299.99, in_stock=True, category=category_electronics),
        Product(name="Laptop", price=499.99, in_stock=False, category=category_electronics),
        Product(name="Sci-Fi Novel", price=15.99, in_stock=True, category=category_books),
        Product(name="Jeans", price=40.50, in_stock=True, category=category_clothing),
        Product(name="T-Shirt", price=20.00, in_stock=True, category=category_clothing)
    ])

    session.commit()


def get_all_categories():
    sql_query = select(Category)
    categories = session.execute(sql_query).scalars().all()
    for category in categories:
        print('*'*50, f'\n{category}')
        for product in category.products:
            print(f"{product.name}-{product.price}")

def update_price(product_name, new_price):
    query = select(Product).where(Product.name == product_name)
    product = session.execute(query).scalar_one_or_none()
    if product:
        product.price = new_price
        session.commit()

def count_products_by_category():
    query = select(Category.name, func.count(Product.id)).join(Product).group_by(Category.name)
    categories = session.execute(query).all()
    for category, products in categories:
        print(f'{category}: {products}')


def filter_category():
    query = select(Category.name, func.count(Product.id)).join(Product).group_by(Category.name).having(func.count(Product.id) > 1)
    categories = session.execute(query).all()
    for category, products in categories:
        print(f'{category}: {products}')


with LocalSession() as session:
    get_all_categories()
    product_name = input("Input a product name: ")
    new_price = float(input("Input a new price: "))
    update_price(product_name, new_price)
    get_all_categories()
    count_products_by_category()
    filter_category()
