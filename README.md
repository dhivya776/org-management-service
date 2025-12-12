# Organization Management Service

A backend service built with **FastAPI** and **MongoDB** that supports a multi-tenant architecture. This system allows for creating organizations, managing admin authentication, and handling dynamic data isolation using separate collections per tenant.

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Database:** MongoDB (Motor Async Driver)
* **Authentication:** JWT (JSON Web Tokens) & Bcrypt hashing

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-link>
    cd org_management
    ```

2.  **Set up the Virtual Environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a file named `.env` in the root directory and add:
    ```env
    MONGO_URL=mongodb://localhost:27017
    SECRET_KEY=supersecretkey123
    ALGORITHM=HS256
    DB_NAME=master_db
    ```

5.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```

6.  **Access API Documentation:**
    Open your browser to: `http://127.0.0.1:8000/docs`

## Architecture & Design Choices

### **Multi-Tenancy Strategy**
I chose a **Collection-Based Isolation** strategy.
* **Master Database:** Stores global metadata (Tenant list, Admin Users).
* **Dynamic Collections:** Each organization gets its own collection (e.g., `org_tesla`, `org_google`).

### **Trade-offs**
* **Pros:** * **Data Isolation:** Easier to backup or delete a single client's data.
    * **Simplicity:** Queries do not need complex filtering by `tenant_id`.
* **Cons:** * **Scalability:** MongoDB has a limit on the number of namespaces. Scaling to 10,000+ organizations might degrade performance compared to a "Shared Collection" approach (Row-Level Isolation).

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/org/create` | Create a new organization & admin. |
| `GET` | `/org/get` | Fetch organization details. |
| `PUT` | `/org/update` | Update org name & migrate data. |
| `DELETE` | `/org/delete` | Delete org & drop collection (Auth required). |
| `POST` | `/admin/login` | Login to get JWT Token. |
