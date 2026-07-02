from sqlalchemy import create_engine, String, Numeric, ForeignKey, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

engine = create_engine('sqlite:///:memory:')
LocalSession = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    products: Mapped[list['Product']] = relationship(
        back_populates='category',
        passive_deletes=True,
    )

    def __str__(self):
        return f'{self.name}: {self.description}'

    def __repr__(self):
        return f'Category(id={self.id}, name={self.name})'


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00)
    in_stock: Mapped[bool]
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE')
    )
    category: Mapped['Category'] = relationship(back_populates='products')

    def __str__(self):
        return f'{self.id} {self.name} - {self.price} - {self.in_stock}'

    def __repr__(self):
        return f'Product(name={self.name}, price={self.price})'


with engine.begin() as connection:
    Base.metadata.create_all(connection)

with LocalSession() as session:
    category_electronics = Category(name='Electronics', description='Gadgets and devices.')
    category_books = Category(name='Books', description='Printed and electronic books')
    category_clothing = Category(name='Clothing', description='Clothing for men and women')

    session.add_all([
        Product(name='Smartphone', price=299.99, in_stock=True, category=category_electronics),
        Product(name='Laptop', price=499.99, in_stock=False, category=category_electronics),
        Product(name='Sci-Fi Novel', price=15.99, in_stock=True, category=category_books),
        Product(name='Jeans', price=40.50, in_stock=True, category=category_clothing),
        Product(name='T-Shirt', price=20.00, in_stock=True, category=category_clothing),
    ])
    session.commit()


def get_all_categories(session) -> list[Category]:
    return session.execute(select(Category)).scalars().all()


def update_price(session, product_name: str, new_price: float) -> bool:
    product = session.execute(
        select(Product).where(Product.name == product_name)
    ).scalar_one_or_none()

    if product is None:
        return False

    product.price = new_price
    session.commit()
    return True


def count_products_by_category(session) -> list[tuple[str, int]]:
    return session.execute(
        select(Category.name, func.count(Product.id))
        .join(Product)
        .group_by(Category.name)
    ).all()


def filter_categories_with_multiple_products(session) -> list[tuple[str, int]]:
    return session.execute(
        select(Category.name, func.count(Product.id))
        .join(Product)
        .group_by(Category.name)
        .having(func.count(Product.id) > 1)
    ).all()


with LocalSession() as session:

    print('=' * 50)
    print('All categories and products:')
    for category in get_all_categories(session):
        print(f'\n  {category}')
        for product in category.products:
            print(f'    {product.name} - {product.price}')

    product_name = input('\nEnter product name: ')
    new_price = float(input('Enter new price: '))

    if update_price(session, product_name, new_price):
        print('\nPrice updated. Current state:')
        for category in get_all_categories(session):
            print(f'\n  {category}')
            for product in category.products:
                print(f'    {product.name} - {product.price}')
    else:
        print(f'Product "{product_name}" not found.')

    print('\nProduct count by category:')
    for name, count in count_products_by_category(session):
        print(f'  {name}: {count}')

    print('\nCategories with more than 1 product:')
    for name, count in filter_categories_with_multiple_products(session):
        print(f'  {name}: {count}')