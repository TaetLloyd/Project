# Todo Backend
# FastAPI System Readme

This repository contains a FastAPI system that provides registration and login functionality with email and name, and ensures that passwords are securely hashed. This readme file will guide you through the setup and usage of the system.

## Installation

To install and run the FastAPI system, please follow these steps:

1. Clone the repository to your local machine:

```
git clone <repository-url>
```

2. Navigate to the project directory:

```
cd fastapi-system
```

3. Create a virtual environment:

```
python3 -m venv env
```

4. Activate the virtual environment:

- For Windows:
```
env\Scripts\activate.bat
```

5. Install the required dependencies:

```
pip install -r requirements.txt
```

6. Set up the database:

- The system uses a MYSQL database. Make sure you have MYSQL installed and running on your machine.

- Create a new MYSQL database for the system.

- Update the database connection details in the `config.py` file located in the `app` directory.

7. Run the database migrations:

```
alembic upgrade head
```

8. Start the FastAPI server:

```
uvicorn app.main:app --reload
```

The server should now be up and running on `http://localhost:8000`.

## Usage

Once the FastAPI server is running, you can interact with the system using the following endpoints:

### Registration

- Endpoint: `POST /register`
- Request body:
  ```json
  {
    "email": "user@example.com",
    "name": "Tatenda Lloyd",
    "password": "password123"
  }
  ```
  Replace the values with the desired email, name, and password.

- Response:
  ```json
  {
    "message": "User registered successfully"
  }
  ```

### Login

- Endpoint: `POST /login`
- Request body:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
  Replace the values with the registered email and password.

- Response:
  ```json
  {
    "message": "Login successful",
    "access_token": "<access-token>"
  }
  ```
  The `<access-token>` is a JSON Web Token (JWT) that can be included in subsequent requests for authentication.

- Note: The access token is valid for a certain duration (configured in `config.py`). You will need to include the token in the `Authorization` header for protected endpoints.

### Protected Endpoint

- Endpoint: `GET /protected`
- Request headers:
  ```
  Authorization: Bearer <access-token>
  ```
  Replace `<access-token>` with the actual access token obtained during the login process.

- Response:
  ```json
  {
    "message": "Welcome to the protected endpoint!"
  }
  ```

## Conclusion

Congratulations! You have successfully installed and set up the FastAPI system for registration and login with hashed passwords. You can now start using the system by registering users, logging in, and accessing protected endpoints. Feel free to explore the codebase and customize it to fit your specific requirements.

If you have any questions or issues, please refer to the documentation or reach out to the project maintainers.

Happy coding!
