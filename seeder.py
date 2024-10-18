# populate_db.py
import random
from faker import Faker
from models import User, Bid, Operation
from connection import session
from decimal import Decimal

# Crear instancia de Faker
fake = Faker()

# Poblar la base de datos con datos falsos
def populate_users(n):
    users = []
    for _ in range(n):
        user = User(
            id=fake.uuid4(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            nickname=fake.user_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            role=random.choice(['admin', 'investor', 'operator']),
            country=fake.country(),
            state=fake.state(),
            city=fake.city()
        )
        users.append(user)
        session.add(user)

    session.commit()
    return users

def populate_operations(users, n):
    for _ in range(n):
        user = random.choice(users)
        operation = Operation(
            id=fake.uuid4(),
            operator_id=user.id,
            required_amount=Decimal(round(random.uniform(1000.00, 10000.00), 2)),  # Convertir a Decimal
            annual_interest=Decimal(round(random.uniform(5.0, 15.0), 2)),  # Convertir a Decimal
            deadline=fake.date_between(start_date='today', end_date='+30d'),
            current_amount=Decimal(0),  # Convertir a Decimal
            status=random.choice(['Open', 'Closed']),
        )
        session.add(operation)

    session.commit()

def populate_bids(users, operations, n):
    for _ in range(n):
        user = random.choice(users)
        operation = random.choice(operations)
        invested_amount = Decimal(round(random.uniform(100.00, float(operation.required_amount)), 2))  # Asegúrate de que sea un float
        bid = Bid(
            id=fake.uuid4(),
            investor_id=user.id,
            operation_id=operation.id,
            invested_amount=invested_amount,  # Ahora esto es un Decimal
            interest_rate=operation.annual_interest,
        )
        session.add(bid)

    session.commit()

if __name__ == "__main__":
    # Poblar la base de datos
    num_users = 30
    num_operations = 100
    num_bids = 50

    users = populate_users(num_users)
    populate_operations(users, num_operations)
    operations = session.query(Operation).all()
    populate_bids(users, operations, num_bids)

    print(f"Se generaron {num_users} usuarios, {num_operations} operaciones y {num_bids} ofertas.")
