import uuid
from app.db.database import engine, SessionLocal, Base
from app.db.model import Customer, Order, OrderItem, Shipment

Base.metadata.create_all(bind=engine)
db = SessionLocal()


if db.query(Order).count() == 0:
    cust1 = Customer(customer_id="CUST-501", city="Mumbai", state="MH")
    cust2 = Customer(customer_id="CUST-502", city="Bengaluru", state="KA")
    db.add_all([cust1, cust2])
    db.commit()


    ord1 = Order(order_id="ORD-1001", customer_id="CUST-501", order_date="2026-08-20", status="Delivered")
    item1 = OrderItem(id=uuid.uuid4().hex, order_id="ORD-1001", sku="SKU-AUDIO-1", name="Wireless Headset", price=89.99)
    ship1 = Shipment(tracking_num="TRK-9901", order_id="ORD-1001", carrier="FedEx", status="Delivered", estimated_delivery="2026-08-24")

    ord2 = Order(order_id="ORD-1002", customer_id="CUST-502", order_date="2026-08-30", status="Processing")
    item2 = OrderItem(id=uuid.uuid4().hex, order_id="ORD-1002", sku="SKU-MON-2", name="Smart Monitor", price=320.00)
    ship2 = Shipment(tracking_num="TRK-9902", order_id="ORD-1002", carrier="UPS", status="Label Created", estimated_delivery="2026-09-05")

    db.add_all([ord1, item1, ship1, ord2, item2, ship2])
    db.commit()
    print("Database initialised with base orders successfully!")

db.close()