from datetime import datetime

from sqlalchemy import and_
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session


# TODO: Connect to Azure LATER
# import urllib
# import pyodbc
# params = urllib.parse.quote_plus(
#     'Driver=%s;' % driver +
#     'Server=tcp:%s,1433;' % server +
#     'Database=%s;' % database +
#     'Uid=%s;' % username +
#     'Pwd={%s};' % password +
#     'Encrypt=yes;' +
#     'TrustServerCertificate=no;' +
#     'Connection Timeout=30;')

# conn_str = 'mssql+pyodbc:///?odbc_connect=' + params
# engine = create_engine(conn_str)




Model = declarative_base(name='Model')

class Order(Model):
    __tablename__ = "order"

    order_id = Column(Integer, primary_key=True)
    customer_name = Column(String(30), nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.now())
    order_items = relationship(
        "OrderItem", cascade="all, delete-orphan", backref="order"
    )

    def __init__(self, customer_name):
        self.customer_name = customer_name

class Item(Model):
    __tablename__ = "item"

    item_id = Column(Integer, primary_key=True)
    description = Column(String(30), nullable=False)
    price = Column(Float, nullable=False)

    def __init__(self, description, price):
        self.description = description
        self.price = price

    def __repr__(self):
        return "Item(%r, %r)" % (self.description, self.price)

class OrderItem(Model):
    __tablename__ = "orderitem"

    order_id = Column(Integer, ForeignKey("order.order_id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.item_id"), primary_key=True)
    price = Column(Float, nullable=False)

    def __init__(self, item, price=None):
        self.item = item
        self.price = price or item.price

    item = relationship(Item, lazy="joined")

def run():

    driver = "{ODBC Driver 17 for SQL Server}"
    server = "<server-name>.database.windows.net"
    database = "<db-name>"
    user = "<db-user>"
    password = "<db-password>"

    conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};
    Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""

    params = urllib.parse.quote_plus(conn)
    conn_str = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(params)
    engine = create_engine(conn_str, echo=True)
    engine = create_engine("sqlite://")
    Model.metadata.create_all(engine)

    session = Session(engine)

    # create catalog
    tshirt, mug, hat, crowbar = (
        Item("SA T-Shirt", 10.99),
        Item("SA Mug", 6.50),
        Item("SA Hat", 8.99),
        Item("MySQL Crowbar", 16.99),
    )
    session.add_all([tshirt, mug, hat, crowbar])
    session.commit()

    # create an order
    order = Order("john smith")

    # add three OrderItem associations to the Order and save
    order.order_items.append(OrderItem(mug))
    order.order_items.append(OrderItem(crowbar, 10.99))
    order.order_items.append(OrderItem(hat))
    session.add(order)
    session.commit()

    # query the order, print items
    order = session.query(Order).filter_by(customer_name="john smith")
    print(
        [
            (order_item.item.description, order_item.price)
            for order_item in order.order_items
        ]
    )

    # print customers who bought 'MySQL Crowbar' on sale
    q = session.query(Order).join("order_items", "item")
    q = q.filter(
        and_(Item.description == "MySQL Crowbar", Item.price > OrderItem.price)
    )

    print([order.customer_name for order in q])

run()
