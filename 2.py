first_user = {"name": "Dima", "surname": "Petrenko", "age": 34,}
second_user = {"name": "Vanya", "surname": "Omelko", "age": 16,}

def print_user(user):
    print(f"User {user['name']} {user['surname']} (age={user['age']})")


print_user(first_user)
print_user(second_user)
