"""Sample module to demonstrate the sequence extractor."""


class DatabaseHandler:
    """Handles database operations."""

    def __init__(self, connection_string):
        self.connection_string = connection_string
        print(f"Connecting to: {connection_string}")

    def query(self, sql):
        """Execute a query."""
        print(f"Executing SQL: {sql}")
        return ["result1", "result2"]

    def update(self, sql, parameters):
        """Execute an update."""
        print(f"Updating with: {sql}, params: {parameters}")
        return True


class UserRepository:
    """Repository for user data."""

    def __init__(self, db_handler):
        self.db = db_handler

    def get_user_by_id(self, user_id):
        """Get a user by ID."""
        sql = f"SELECT * FROM users WHERE id = {user_id}"
        return self.db.query(sql)

    def save_user(self, user):
        """Save a user to the database."""
        sql = "INSERT INTO users (name, email) VALUES (?, ?)"
        params = [user.name, user.email]
        return self.db.update(sql, params)


class EmailService:
    """Service for sending emails."""

    def send_welcome_email(self, user):
        """Send welcome email to a new user."""
        print(f"Sending welcome email to {user.email}")
        return True


class User:
    """User model."""

    def __init__(self, name, email):
        self.name = name
        self.email = email


class UserService:
    """Business logic for user operations."""

    def __init__(self, user_repository, email_service):
        self.repository = user_repository
        self.email_service = email_service

    def get_user(self, user_id):
        """Get a user."""
        return self.repository.get_user_by_id(user_id)

    def create_user(self, name, email):
        """Create a new user and send welcome email."""
        user = User(name, email)
        success = self.repository.save_user(user)

        if success:
            self.email_service.send_welcome_email(user)

        return user


def create_services():
    """Factory function to create the service objects."""
    db = DatabaseHandler("postgresql://localhost:5432/userdb")
    user_repo = UserRepository(db)
    email_service = EmailService()
    return UserService(user_repo, email_service)


def main():
    """Main function to demonstrate the sequence."""
    # Create service objects
    user_service = create_services()

    # Create a new user
    user = user_service.create_user("John Doe", "john@example.com")
    print(f"Created user: {user.name}")

    # Get user details
    result = user_service.get_user(1)
    print(f"Found user: {result}")


if __name__ == "__main__":
    main()
