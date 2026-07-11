from werkzeug.security import generate_password_hash

password = "admin123"

hash_password = generate_password_hash(password)

print(hash_password)