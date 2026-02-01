from decimal import Decimal, getcontext
import math

getcontext().prec = 28


def cost(q_yes: Decimal, q_no: Decimal, b: Decimal) -> Decimal:
    # Using float exp for simplicity; acceptable for MVP with tolerance
    qy = float(q_yes / b)
    qn = float(q_no / b)
    return Decimal(b) * Decimal(math.log(math.exp(qy) + math.exp(qn)))


def price_yes(q_yes: Decimal, q_no: Decimal, b: Decimal) -> Decimal:
    qy = math.exp(float(q_yes / b))
    qn = math.exp(float(q_no / b))
    return Decimal(qy / (qy + qn))


def quote_buy(side: str, dq: Decimal, q_yes: Decimal, q_no: Decimal, b: Decimal, fee_rate: Decimal):
    if side == "YES":
        new_q_yes = q_yes + dq
        new_q_no = q_no
    else:
        new_q_no = q_no + dq
        new_q_yes = q_yes
    base_cost = cost(new_q_yes, new_q_no, b) - cost(q_yes, q_no, b)
    fee = base_cost * fee_rate
    total = base_cost + fee
    return {
        "base_cost": base_cost,
        "fee": fee,
        "total": total,
        "new_q_yes": new_q_yes,
        "new_q_no": new_q_no,
    }

