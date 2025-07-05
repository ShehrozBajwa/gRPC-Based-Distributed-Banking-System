import grpc
import bank_pb2
import bank_pb2_grpc

class BankClient:
    def __init__(self, host='localhost', port=50051):
        # Establishes a connection to the gRPC server
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = bank_pb2_grpc.BankServiceStub(self.channel)

    def create_account(self, account_id: str, account_type: str) -> str:
        """Sends a request to create a new bank account."""
        try:
            response = self.stub.CreateAccount(
                bank_pb2.AccountRequest(account_id=account_id, account_type=account_type)
            )
            return response.message  # Returns server response message
        except grpc.RpcError as e:
            return f"Error: {e.details()}"  # Handles RPC errors

    def get_balance(self, account_id: str) -> float:
        """Fetches the balance of the specified account."""
        try:
            response = self.stub.GetBalance(
                bank_pb2.AccountRequest(account_id=account_id)
            )
            return response.balance  # Returns the account balance
        except grpc.RpcError as e:
            raise Exception(f"Error: {e.details()}")  # Raises an exception if an error occurs

    def deposit(self, account_id: str, amount: float) -> str:
        """Deposits a specified amount into the given account."""
        try:
            response = self.stub.Deposit(
                bank_pb2.DepositRequest(account_id=account_id, amount=amount)
            )
            return response.message  # Returns server response message
        except grpc.RpcError as e:
            return f"Error: {e.details()}"  # Handles RPC errors

    def withdraw(self, account_id: str, amount: float) -> str:
        """Withdraws a specified amount from the given account."""
        try:
            response = self.stub.Withdraw(
                bank_pb2.WithdrawRequest(account_id=account_id, amount=amount)
            )
            return response.message  # Returns server response message
        except grpc.RpcError as e:
            return f"Error: {e.details()}"  # Handles RPC errors

    def calculate_interest(self, account_id: str, annual_interest_rate: float) -> str:
        """Calculates interest on the given account based on an annual interest rate."""
        try:
            response = self.stub.CalculateInterest(
                bank_pb2.InterestRequest(
                    account_id=account_id,
                    annual_interest_rate=annual_interest_rate
                )
            )
            return response.message  # Returns server response message
        except grpc.RpcError as e:
            return f"Error: {e.details()}"  # Handles RPC errors

# Example usage
if __name__ == "__main__":
    client = BankClient()
    
    # Example operations
    print(client.create_account("123", "savings"))  # Create a savings account
    print(client.deposit("123", 1000.0))  # Deposit $1000 into the account
    print(f"Balance: ${client.get_balance('123'):.2f}")  # Retrieve and print account balance
    print(client.withdraw("123", 500.0))  # Withdraw $500 from the account
    print(client.calculate_interest("123", 2.5))  # Calculate interest with 2.5% annual rate
