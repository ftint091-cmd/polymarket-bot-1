import uuid

def new_cycle_id() -> str:
    return f"cyc_{uuid.uuid4().hex[:12]}"

def new_signal_id() -> str:
    return f"sig_{uuid.uuid4().hex[:12]}"

def new_order_id() -> str:
    return f"ord_{uuid.uuid4().hex[:12]}"

def new_position_id() -> str:
    return f"pos_{uuid.uuid4().hex[:12]}"
