import pandas as pd
from faker import Faker
import random

fake = Faker()
data = []
for i in range(200):
    data.append({
        "name": fake.name(),
        "email": fake.email() if random.random() > 0.1 else None,  # some missing
        "phone": fake.phone_number(),
        "signup_date": random.choice([fake.date(), fake.date_time().strftime("%d-%m-%Y")]),  # inconsistent formats
        "city": fake.city()
    })

df = pd.DataFrame(data)
# inject some duplicates
df = pd.concat([df, df.sample(10)], ignore_index=True)
df.to_csv("sample_data.csv", index=False)