from app.tools.order_tools import order_lookup, cancellation_eligibility
from app.tools.shipment_tools import shipment_tracking
from app.tools.refund_tools import refund_eligibility
from app.tools.knowledge_tools import knowledge_base_search
from app.tools.ticket_tools import support_ticket_creation, ticket_lookup
ALL_TOOLS = [
    order_lookup,
    shipment_tracking,
    knowledge_base_search,
    refund_eligibility,
    cancellation_eligibility,
    support_ticket_creation,
    ticket_lookup
]