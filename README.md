# gRPC-Based Distributed Banking System

This project is a high-performance, distributed application for managing bank accounts, built with Python. It demonstrates a modern client-server architecture using gRPC for efficient communication and Redis for fast, persistent data storage. The system is designed to handle concurrent operations safely, ensuring data integrity through a robust locking mechanism.

This project serves as a practical implementation of key concepts in scalable and reliable distributed systems.

## Key Features

-   **Account Management**: Create new "savings" or "checking" accounts.
-   **Core Banking Operations**: Perform deposits, withdrawals, and balance inquiries.
-   **Interest Calculation**: Apply an annual interest rate to an account's balance.
-   **Concurrency Control**: Safely handles simultaneous requests to the same account using a per-account locking mechanism to prevent race conditions.
-   **Robust Error Handling**: Gracefully manages scenarios like non-existent accounts, insufficient funds, and invalid inputs, returning clear gRPC status codes and messages.
-   **Data Persistence**: Uses Redis as a high-performance, in-memory key-value store for all account data.

## Tech Stack

-   **Backend**: Python
-   **RPC Framework**: `gRPC` for high-performance, cross-platform client-server communication.
-   **Data Serialization**: `Protocol Buffers` (Protobuf) for defining the service and message structures.
-   **Database**: `Redis` for fast, in-memory key-value data storage.
-   **Concurrency**: Python's `threading` module for managing locks and `concurrent.futures.ThreadPoolExecutor` for the gRPC server.

## System Architecture

The system follows a classic client-server model designed for scalability:

1.  **Client (`client.py`)**: A lightweight application that exposes simple Python functions to the end-user. It translates these function calls into gRPC requests.
2.  **gRPC Service Definition (`bank.proto`)**: A Protobuf file defines the `BankService` with its RPC methods (`CreateAccount`, `GetBalance`, etc.) and message formats. This file acts as the contract between the client and server.
3.  **gRPC Server (`server.py`)**: The core of the application.
    -   It listens for incoming gRPC requests from clients.
    -   A thread pool manages concurrent client connections, allowing the server to handle multiple requests simultaneously.
    -   For operations that modify account data (deposit, withdraw, interest), a `threading.Lock` is acquired for the specific `account_id` to ensure atomic updates and prevent data corruption.
4.  **Redis Database**: The server connects to a Redis instance to persist all account information. Each account is stored as a Redis Hash, with the account ID as the key. This provides fast data retrieval and updates.

```
+-----------+       gRPC (Protobuf)        +-------------------+       Redis Commands        +-------+
|           | <--------------------------> |                   | <-------------------------> |       |
|  Client   |                              |   gRPC Server     |                             | Redis |
|           | -------------------------->  | (with ThreadPool) | --------------------------> |       |
+-----------+                              +-------------------+                             +-------+
                                                 |
                                                 v
                                           +----------------+
                                           | Account Locks  |
                                           | (for Concurrency)|
                                           +----------------+
```

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   Redis server installed and running on `localhost:6379`. You can download it from the [official Redis website](https://redis.io/download/).

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/grpc-banking-system.git
    cd grpc-banking-system
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows: venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    *(Note: You may need to create a `requirements.txt` file containing `grpcio`, `grpcio-tools`, and `redis`)*
    ```bash
    pip install grpcio grpcio-tools redis
    ```

4.  **(If needed) Generate gRPC code from the `.proto` file:**

    The necessary `bank_pb2.py` and `bank_pb2_grpc.py` files are included. However, if you modify `bank.proto`, you'll need to regenerate them using `grpcio-tools`:
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. bank.proto
    ```

## How to Run

1.  **Start the Redis Server:**
    Ensure your Redis server is running. By default, it runs on `localhost:6379`.

2.  **Start the gRPC Server:**
    Open a terminal and run the server. It will wait for incoming client connections.
    ```bash
    python server.py
    ```
    You should see the output: `Server started on port 50051`

3.  **Run the Client:**
    Open another terminal to run the client application, which will execute a series of pre-defined banking operations.
    ```bash
    python client.py
    ```

### Example Client Output

Running `client.py` will produce output similar to this:

```
Account 123 created successfully
Successfully deposited $1000.00
Balance: $1000.00
Successfully withdrew $500.00
Applied daily interest rate of 2.5000% to bank amount of $500.00 for interest amount of $12.50
```

## API Service Definition (`BankService`)

The gRPC service exposes the following methods:

| Method                 | Request Parameters                      | Response                                                                | Description                                                         |
| ---------------------- | --------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `CreateAccount`        | `account_id`, `account_type`            | `message`                                                               | Creates a new savings or checking account with a zero balance.      |
| `GetBalance`           | `account_id`                            | `balance`, `message`                                                    | Retrieves the current balance for a specified account.              |
| `Deposit`              | `account_id`, `amount`                  | `balance`, `message`                                                    | Deposits a positive amount into an account.                         |
| `Withdraw`             | `account_id`, `amount`                  | `balance`, `message`                                                    | Withdraws a positive amount, if funds are sufficient.               |
| `CalculateInterest`    | `account_id`, `annual_interest_rate`    | `balance`, `message`                                                    | Calculates and applies interest to the account balance.             |

## Future Improvements

-   **Dockerize Application**: Containerize the server and Redis for easier deployment and environment consistency.
-   **Authentication & Authorization**: Implement token-based authentication (e.g., JWT) to secure the RPC methods.
-   **Add Unit and Integration Tests**: Develop a comprehensive test suite to ensure the reliability of each component.
-   **Implement Transaction History**: Add a new RPC method to retrieve a list of all transactions for an account.
-   **Asynchronous Client/Server**: Refactor using Python's `asyncio` for potentially higher performance under heavy I/O load.
