recurring = {
    "food": 200,
    "rent": 75,
    "health_insurance": 13.32 / 2,
    "gym": 42 / 4,
    "phone": 75.50 / 4,
    "fuel": 20,
    "heroku": 11 / 4,
    "spotify": 13 / 4,
    "chatgpt": 34.49 / 4,
    "psych": 94,
}


# flat payments due
car_rego = 300
car_insurance = 300
bills = 100
interest = 100

recurring_total = sum([recurring[x] * 12 for x in recurring])

print("recurring: ", recurring_total)
print("total: ", recurring_total + car_rego + car_insurance + bills + interest)