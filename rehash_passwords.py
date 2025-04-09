# this file is used for migrating from werkzeug to flask-bcrypt, even the binary one that forgot to be decoded into utf-8 first
# run it using uv run python rehash_passwords.py
from app import create_app, bcrypt
from app.models.user import User, db
from werkzeug.security import check_password_hash


def rehash_passwords():
    app = create_app()

    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users to process")

        for user in users:
            try:
                if user.password_hash.startswith('\\x'):
                    binary_hash = bytes.fromhex(user.password_hash[2:])
                    decoded_hash = binary_hash.decode('utf-8')

                    # Update the hash
                    print(f"Fixed hash for user: {user.username}")
                    print(f"Old hash: {user.password_hash}")
                    user.password_hash = decoded_hash
                    print(f"New hash: {decoded_hash}")
                    continue

                elif user.password_hash.startswith('scrypt'):
                    plain_password = input(
                        f"Enter plain password for user {user.username}: ")

                    # Verify the old hash first
                    if check_password_hash(user.password_hash, plain_password):
                        # Generate new bcrypt hash
                        new_hash = bcrypt.generate_password_hash(
                            plain_password).decode('utf-8')
                        user.password_hash = new_hash
                        print(f"Password rehashed for user: {user.username}")
                    else:
                        print(
                            f"Invalid password for user: {user.username}, skipping...")
                        continue

                else:
                    continue

            except Exception as e:
                print(f"Error processing user {user.username}: {str(e)}")
                continue

        try:
            db.session.commit()
            print("All passwords have been rehashed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error saving changes to database: {str(e)}")


if __name__ == "__main__":
    rehash_passwords()
