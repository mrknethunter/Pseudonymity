"""Synthetic datasets for demos and tests."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from pseudonymity.io import write_csv
from pseudonymity.profiles import REQUIRED_COLUMNS

FIRST_NAMES = [
    "Alessia",
    "Andrea",
    "Bianca",
    "Carlo",
    "Chiara",
    "Davide",
    "Elena",
    "Fabio",
    "Giulia",
    "Luca",
    "Marta",
    "Matteo",
    "Noemi",
    "Paolo",
    "Sara",
    "Simone",
    "Valentina",
    "Vittorio",
]

LAST_NAMES = [
    "Bianchi",
    "Conti",
    "Costa",
    "De Luca",
    "Esposito",
    "Ferrari",
    "Galli",
    "Greco",
    "Marino",
    "Moretti",
    "Ricci",
    "Rinaldi",
    "Romano",
    "Russo",
    "Serra",
    "Villa",
]

CITIES = [
    ("Milano", "Lombardia", "20121"),
    ("Bergamo", "Lombardia", "24121"),
    ("Torino", "Piemonte", "10121"),
    ("Asti", "Piemonte", "14100"),
    ("Bologna", "Emilia-Romagna", "40121"),
    ("Parma", "Emilia-Romagna", "43121"),
    ("Firenze", "Toscana", "50121"),
    ("Pisa", "Toscana", "56121"),
    ("Roma", "Lazio", "00184"),
    ("Viterbo", "Lazio", "01100"),
    ("Napoli", "Campania", "80121"),
    ("Salerno", "Campania", "84121"),
]

SUBSCRIPTION_PLANS = ["basic", "plus", "premium"]
PURCHASE_CATEGORIES = ["books", "electronics", "home", "sport", "travel"]
PREFERRED_CHANNELS = ["email", "sms", "app", "phone", "none"]
DIAGNOSIS_CODES = ["NONE", "I10", "E11", "J45", "M54", "F41"]
TEST_NETS = ["192.0.2.", "198.51.100.", "203.0.113."]


def make_synthetic_row(index: int, rng: random.Random) -> dict[str, str]:
    first_name = rng.choice(FIRST_NAMES)
    last_name = rng.choice(LAST_NAMES)
    city, region, base_postal = rng.choice(CITIES)
    customer_id = f"CUST-{index:05d}"
    email_local = f"{first_name}.{last_name}.{index}".lower().replace(" ", "-")
    birth_start = date(1951, 1, 1)
    dob = birth_start + timedelta(days=rng.randint(0, 19000))
    signup_start = date(2022, 1, 1)
    signup_date = signup_start + timedelta(days=rng.randint(0, 1500))
    ip = rng.choice(TEST_NETS) + str(rng.randint(1, 240))
    street_number = rng.randint(1, 180)
    phone_tail = f"{index:04d}{rng.randint(10, 99)}"
    amount = round(rng.uniform(18.0, 950.0), 2)
    tickets = rng.choices([0, 1, 2, 3, 4, 5, 6], weights=[28, 22, 18, 13, 9, 6, 4])[0]
    churn = min(0.98, max(0.02, (tickets * 0.11) + rng.uniform(0.02, 0.45)))

    return {
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{email_local}@example-demo.test",
        "phone": f"+39 02 5550 {phone_tail}",
        "date_of_birth": dob.isoformat(),
        "street_address": f"Via Demo {street_number}",
        "city": city,
        "region": region,
        "postal_code": str(int(base_postal) + rng.randint(0, 18)).zfill(5),
        "last_login_ip": ip,
        "signup_date": signup_date.isoformat(),
        "subscription_plan": rng.choice(SUBSCRIPTION_PLANS),
        "purchase_category": rng.choice(PURCHASE_CATEGORIES),
        "purchase_amount_eur": f"{amount:.2f}",
        "support_tickets": str(tickets),
        "churn_risk_score": f"{churn:.2f}",
        "loyalty_points": str(rng.randint(0, 9000)),
        "preferred_channel": rng.choice(PREFERRED_CHANNELS),
        "marketing_consent": rng.choice(["yes", "no"]),
        "diagnosis_code": rng.choices(DIAGNOSIS_CODES, weights=[55, 10, 10, 8, 9, 8])[0],
    }


def generate_sample_dataset(output: Path, rows: int, seed: int) -> None:
    rng = random.Random(seed)
    data = [make_synthetic_row(index, rng) for index in range(1, rows + 1)]
    write_csv(output, data, REQUIRED_COLUMNS)
