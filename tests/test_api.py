from fastapi.testclient import TestClient


def create_user(client: TestClient, full_name: str, email: str) -> dict:
    response = client.post(
        "/api/users",
        json={"full_name": full_name, "email": email},
    )
    assert response.status_code == 201
    return response.json()


def create_book(client: TestClient, title: str, author: str, copies_count: int = 1) -> dict:
    response = client.post(
        "/api/books",
        json={"title": title, "author": author, "copies_count": copies_count},
    )
    assert response.status_code == 201
    return response.json()


def test_create_user(client: TestClient):
    response = client.post(
        "/api/users",
        json={"full_name": "Jan Novak", "email": "jan.novak@example.com"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["full_name"] == "Jan Novak"
    assert data["email"] == "jan.novak@example.com"


def test_create_user_rejects_duplicate_email(client: TestClient):
    create_user(client, "Jan Novak", "jan.novak@example.com")

    response = client.post(
        "/api/users",
        json={"full_name": "Jan Novak 2", "email": "jan.novak@example.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists."


def test_create_book_returns_availability_summary(client: TestClient):
    response = client.post(
        "/api/books",
        json={"title": "1984", "author": "George Orwell", "copies_count": 3},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "1984"
    assert data["author"] == "George Orwell"
    assert data["total_copies"] == 3
    assert data["available_copies"] == 3
    assert data["is_available"] is True


def test_borrow_book_marks_copy_as_unavailable(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": book["id"]},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["book_id"] == book["id"]
    assert data["borrower_user_id"] == user["id"]
    assert data["is_active"] is True
    assert data["returned_at"] is None

    books_response = client.get("/api/books")
    assert books_response.status_code == 200
    books = books_response.json()
    assert books[0]["available_copies"] == 0
    assert books[0]["is_available"] is False


def test_borrow_book_requires_x_user_id_header(client: TestClient):
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    response = client.post(
        "/api/loans/borrow",
        json={"book_id": book["id"]},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["header", "x-user-id"]


def test_borrow_book_returns_conflict_when_no_copy_is_available(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    first_borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": book["id"]},
    )
    assert first_borrow_response.status_code == 201

    second_borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": book["id"]},
    )

    assert second_borrow_response.status_code == 409
    assert second_borrow_response.json()["detail"] == "No available copy for this book."


def test_return_book_restores_availability(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": book["id"]},
    )
    loan = borrow_response.json()

    return_response = client.post(
        "/api/loans/return",
        headers={"x-user-id": str(user["id"])},
        json={"loan_id": loan["id"]},
    )

    assert return_response.status_code == 200
    data = return_response.json()
    assert data["id"] == loan["id"]
    assert data["is_active"] is False
    assert data["returned_at"] is not None
    assert data["returned_by_user_id"] == user["id"]

    books_response = client.get("/api/books")
    books = books_response.json()
    assert books[0]["available_copies"] == 1
    assert books[0]["is_available"] is True


def test_return_closed_loan_returns_conflict(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": book["id"]},
    )
    loan = borrow_response.json()

    first_return_response = client.post(
        "/api/loans/return",
        headers={"x-user-id": str(user["id"])},
        json={"loan_id": loan["id"]},
    )
    assert first_return_response.status_code == 200

    second_return_response = client.post(
        "/api/loans/return",
        headers={"x-user-id": str(user["id"])},
        json={"loan_id": loan["id"]},
    )

    assert second_return_response.status_code == 409
    assert second_return_response.json()["detail"] == "Loan is already closed."


def test_available_only_filters_out_fully_borrowed_books(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    available_book = create_book(client, "Dune", "Frank Herbert", copies_count=1)
    borrowed_book = create_book(client, "1984", "George Orwell", copies_count=1)

    borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": borrowed_book["id"]},
    )
    assert borrow_response.status_code == 201

    response = client.get("/api/books", params={"available_only": True})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == available_book["id"]
    assert data[0]["title"] == "Dune"


def test_return_for_different_user_is_forbidden(client: TestClient):
    borrower = create_user(client, "Jan Novak", "jan.novak@example.com")
    another_user = create_user(client, "Eva Svobodova", "eva.svobodova@example.com")
    book = create_book(client, "1984", "George Orwell", copies_count=1)

    borrow_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(borrower["id"])},
        json={"book_id": book["id"]},
    )
    loan = borrow_response.json()

    return_response = client.post(
        "/api/loans/return",
        headers={"x-user-id": str(another_user["id"])},
        json={"loan_id": loan["id"]},
    )

    assert return_response.status_code == 403
    assert return_response.json()["detail"] == "Only the borrowing user can return this book."


def test_list_loans_returns_borrowing_history(client: TestClient):
    user = create_user(client, "Jan Novak", "jan.novak@example.com")
    first_book = create_book(client, "1984", "George Orwell", copies_count=1)
    second_book = create_book(client, "Dune", "Frank Herbert", copies_count=1)

    first_loan_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": first_book["id"]},
    )
    second_loan_response = client.post(
        "/api/loans/borrow",
        headers={"x-user-id": str(user["id"])},
        json={"book_id": second_book["id"]},
    )

    assert first_loan_response.status_code == 201
    assert second_loan_response.status_code == 201

    response = client.get("/api/loans")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["book_title"] == "Dune"
    assert data[1]["book_title"] == "1984"
    assert all(item["is_active"] is True for item in data)
