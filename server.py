import grpc
from concurrent import futures
import redis
import threading
import bank_pb2
import bank_pb2_grpc
import time

class BankServiceServicer(bank_pb2_grpc.BankServiceServicer):
    def __init__(self):
        # Initialize Redis connection
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        # Dictionary to store locks for each account
        self.account_locks = {}
        self.lock_dict_lock = threading.Lock()

    def get_account_lock(self, account_id):
        with self.lock_dict_lock:
            if account_id not in self.account_locks:
                self.account_locks[account_id] = threading.Lock()
            return self.account_locks[account_id]

    def get_account_data(self, account_id):
        account_data = self.redis_client.hgetall(f"account:{account_id}")
        if not account_data:
            return None
        return {
            'account_id': account_id,
            'account_type': account_data[b'account_type'].decode('utf-8'),
            'balance': float(account_data[b'balance'])
        }

    def CreateAccount(self, request, context):
        account_id = request.account_id
        account_type = request.account_type

        # Validate account type
        if account_type not in ['savings', 'checking']:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Account type must be 'savings' or 'checking'")
            return bank_pb2.AccountResponse()

        # Check if account already exists
        if self.redis_client.exists(f"account:{account_id}"):
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Account already exists")
            return bank_pb2.AccountResponse()

        # Create new account with initial balance of 0
        self.redis_client.hmset(f"account:{account_id}", {
            'account_type': account_type,
            'balance': 0.0
        })

        return bank_pb2.AccountResponse(
            account_id=account_id,
            message=f"Account {account_id} created successfully"
        )

    def GetBalance(self, request, context):
        account_data = self.get_account_data(request.account_id)
        if not account_data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Account not found. Please check the account ID.")
            return bank_pb2.BalanceResponse()

        return bank_pb2.BalanceResponse(
            account_id=request.account_id,
            balance=account_data['balance'],
            message="Balance retrieved successfully"
        )

    def Deposit(self, request, context):
        if request.amount <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Transaction amount must be positive.")
            return bank_pb2.TransactionResponse()

        account_lock = self.get_account_lock(request.account_id)
        with account_lock:
            account_data = self.get_account_data(request.account_id)
            if not account_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found. Please check the account ID.")
                return bank_pb2.TransactionResponse()

            new_balance = account_data['balance'] + request.amount
            self.redis_client.hset(f"account:{request.account_id}", 'balance', new_balance)

            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                message=f"Successfully deposited ${request.amount:.2f}",
                balance=new_balance
            )

    def Withdraw(self, request, context):
        if request.amount <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Transaction amount must be positive.")
            return bank_pb2.TransactionResponse()

        account_lock = self.get_account_lock(request.account_id)
        with account_lock:
            account_data = self.get_account_data(request.account_id)
            if not account_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found. Please check the account ID.")
                return bank_pb2.TransactionResponse()

            if account_data['balance'] < request.amount:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Insufficient funds for the requested withdrawal.")
                return bank_pb2.TransactionResponse()

            new_balance = account_data['balance'] - request.amount
            self.redis_client.hset(f"account:{request.account_id}", 'balance', new_balance)

            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                message=f"Successfully withdrew ${request.amount:.2f}",
                balance=new_balance
            )

    def CalculateInterest(self, request, context):
        if request.annual_interest_rate <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Annual interest rate must be a positive value.")
            return bank_pb2.TransactionResponse()

        account_lock = self.get_account_lock(request.account_id)
        with account_lock:
            account_data = self.get_account_data(request.account_id)
            if not account_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Account not found. Please check the account ID.")
                return bank_pb2.TransactionResponse()

            # Calculate daily interest rate and apply it
            rate = request.annual_interest_rate
            interest_amount = account_data['balance'] * (rate / 100.0)
            new_balance = account_data['balance'] + interest_amount

            self.redis_client.hset(f"account:{request.account_id}", 'balance', new_balance)

            return bank_pb2.TransactionResponse(
                account_id=request.account_id,
                message=f"Applied daily interest rate of {rate:.4f}% to bank amount of ${account_data['balance']:.2f} for interest amount of ${interest_amount:.2f}",
                balance=new_balance
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()