from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String, primary_key=True, index=True)
    city = Column(String, default="Unknown")
    state = Column(String, default="Unknown")
    
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(String, nullable=False)
    status = Column(String, nullable=False) 
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    shipment = relationship("Shipment", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")

class Shipment(Base):
    __tablename__ = "shipments"
    tracking_num = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    carrier = Column(String, nullable=False)
    status = Column(String, nullable=False)
    estimated_delivery = Column(String, nullable=False)
    current_location = Column(String, default="In Transit")
    order = relationship("Order", back_populates="shipment")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    ticket_id = Column(String, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    customer_id = Column(String, nullable=False)
    order_id = Column(String, nullable=True)
    issue_type = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    status = Column(String, default="OPEN") 
    agent_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, index=True, nullable=False)
    order_id = Column(String, index=True, nullable=True)  # Links conversations to specific orders
    role = Column(String, nullable=False)                 
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())