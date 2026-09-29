import os
import uuid
import random
import zipfile
import pandas as pd
from app.db.database import engine, SessionLocal, Base
from app.db.model import Customer, Order, OrderItem, Shipment

CSV_PATH = "olist_orders_dataset.csv"
ZIP_PATH = "olist_orders_dataset.csv.zip"

if os.path.exists(CSV_PATH):
    df_orders = pd.read_csv(CSV_PATH)
elif os.path.exists(ZIP_PATH):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        csv_inside = [name for name in z.namelist() if name.endswith(".csv")][0]
        with z.open(csv_inside) as f:
            df_orders = pd.read_csv(f)
else:
    raise FileNotFoundError(
        f"Neither '{CSV_PATH}' nor '{ZIP_PATH}' was found in {os.getcwd()}."
    )

Base.metadata.create_all(bind=engine)
db = SessionLocal()

status_mapping = {
    "delivered": "Delivered",
    "shipped": "Shipped",
    "processing": "Processing",
    "invoiced": "Placed",
    "created": "Placed",
    "approved": "Processing",
    "canceled": "Cancelled",
    "unavailable": "Cancelled"
}

carriers = ["FedEx", "UPS", "DHL", "Correios"]

product_catalog = [
    ("SKU-AUDIO-1", "Wireless Noise-Canceling Headphones", 89.99),
    ("SKU-MON-2", "27-inch 4K UHD Smart Monitor", 310.00),
    ("SKU-KEY-3", "Mechanical RGB Gaming Keyboard", 115.50),
    ("SKU-CABLE-4", "High-Speed Braided USB-C Cable", 19.99),
    ("SKU-CHAIR-5", "Ergonomic Office Swivel Chair", 229.00),
    ("SKU-MOUSE-6", "Wireless Precision Ergonomic Mouse", 45.00),
    ("SKU-POWER-7", "Portable 20,000mAh Power Bank", 54.99),
]

if not db.query(Order).filter(Order.order_id == "ORD-1001").first():
    c1 = Customer(customer_id="CUST-501", city="Mumbai", state="MH")
    db.merge(c1)
    db.commit()
    o1 = Order(order_id="ORD-1001", customer_id="CUST-501", order_date="2026-08-20", status="Delivered")
    it1 = OrderItem(id=uuid.uuid4().hex, order_id="ORD-1001", sku="SKU-AUDIO-1", name="Wireless Headset", price=89.99)
    sh1 = Shipment(tracking_num="TRK-9901", order_id="ORD-1001", carrier="FedEx", status="Delivered", estimated_delivery="2026-08-24", current_location="Delivered to Front Door")
    db.add_all([o1, it1, sh1])
    db.commit()

if not db.query(Order).filter(Order.order_id == "ORD-1002").first():
    c2 = Customer(customer_id="CUST-502", city="Bengaluru", state="KA")
    db.merge(c2)
    db.commit()
    o2 = Order(order_id="ORD-1002", customer_id="CUST-502", order_date="2026-08-30", status="Processing")
    it2 = OrderItem(id=uuid.uuid4().hex, order_id="ORD-1002", sku="SKU-MON-2", name="Smart Monitor", price=320.00)
    sh2 = Shipment(tracking_num="TRK-9902", order_id="ORD-1002", carrier="UPS", status="Label Created", estimated_delivery="2026-09-05", current_location="Carrier Facility")
    db.add_all([o2, it2, sh2])
    db.commit()

sampled_dfs = []
for status, group in df_orders.groupby("order_status"):
    sample_size = min(len(group), 8)
    sampled_dfs.append(group.sample(n=sample_size, random_state=42))

sample_orders = pd.concat(sampled_dfs).reset_index(drop=True)

inserted_count = 0

for _, row in sample_orders.iterrows():
    raw_id = str(row["order_id"]).strip().upper()
    cust_id = str(row["customer_id"]).strip().upper()

    if db.query(Order).filter(Order.order_id == raw_id).first():
        continue

    raw_status = str(row["order_status"]).lower()
    mapped_status = status_mapping.get(raw_status, "Processing")
    
    seed_val = abs(hash(raw_id))
    rnd = random.Random(seed_val)
    num_items = 1 if (seed_val % 3 != 0) else 2
    selected_items = rnd.sample(product_catalog, num_items)

    
    carrier = carriers[seed_val % len(carriers)]
    tracking_code = f"TRK-{raw_id[:6]}-{rnd.randint(1000, 9999)}"
    
    purchase_date = str(row.get("order_purchase_timestamp", "2026-08-01"))[:10]
    estimated_del = str(row.get("order_estimated_delivery_date", "2026-08-20"))[:10]

    cust_obj = Customer(customer_id=cust_id, city="Unknown", state="Unknown")
    db.merge(cust_obj)
    db.commit()


    order_obj = Order(
        order_id=raw_id,
        customer_id=cust_id,
        order_date=purchase_date,
        status=mapped_status
    )
    db.add(order_obj)
    db.commit()


    for sku, name, price in selected_items:
        it_obj = OrderItem(
            id=uuid.uuid4().hex,
            order_id=raw_id,
            sku=sku,
            name=name,
            price=price
        )
        db.add(it_obj)

    
    ship_obj = Shipment(
        tracking_num=tracking_code,
        order_id=raw_id,
        carrier=carrier,
        status=mapped_status,
        estimated_delivery=estimated_del,
        current_location="In Transit" if mapped_status != "Delivered" else "Delivered"
    )
    db.add(ship_obj)
    db.commit()
    inserted_count += 1

db.close()
print(f"Successfully populated SQLite database with {inserted_count} new Olist orders!")