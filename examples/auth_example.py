"""
Example usage of Solana wallet authentication
"""
import httpx
import base58
from nacl.signing import SigningKey
import asyncio

API_BASE_URL = "http://localhost:8000/api/v1"

async def authenticate_wallet():
    """
    Complete authentication flow example
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Generate a keypair (in real app, this comes from wallet)
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        wallet_address = base58.b58encode(bytes(verify_key)).decode('ascii')
        
        print(f"Wallet Address: {wallet_address}")
        
        # Step 2: Request challenge
        print("\n1. Requesting authentication challenge...")
        challenge_response = await client.post(
            f"{API_BASE_URL}/auth/challenge",
            params={"wallet_address": wallet_address}
        )
        challenge_data = challenge_response.json()
        message = challenge_data["challenge"]
        
        print(f"Challenge received: {message[:50]}...")
        
        # Step 3: Sign the message
        print("\n2. Signing challenge message...")
        signature_bytes = signing_key.sign(message.encode()).signature
        signature = base58.b58encode(signature_bytes).decode('ascii')
        
        # Step 4: Verify signature and get token
        print("\n3. Verifying signature...")
        verify_response = await client.post(
            f"{API_BASE_URL}/auth/verify",
            json={
                "wallet_address": wallet_address,
                "signature": signature,
                "message": message
            }
        )
        token_data = verify_response.json()
        access_token = token_data["access_token"]
        
        print(f"✅ Authentication successful!")
        print(f"Access Token: {access_token[:50]}...")
        
        # Step 5: Use token to access protected route
        print("\n4. Accessing protected profile endpoint...")
        profile_response = await client.get(
            f"{API_BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_data = profile_response.json()
        
        print(f"✅ Profile retrieved: {profile_data}")
        
        return access_token

async def use_protected_endpoint(token: str):
    """
    Example of using protected endpoints
    """
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Example: Protected wallet analysis
        response = await client.post(
            f"{API_BASE_URL}/wallet/analyze",
            json={
                "wallet_address": "YourWalletAddress",
                "analyze_transactions": True
            },
            headers=headers
        )
        
        print(f"Protected endpoint response: {response.json()}")

if __name__ == "__main__":
    # Run authentication flow
    token = asyncio.run(authenticate_wallet())
    
    # Use the token for protected endpoints
    # asyncio.run(use_protected_endpoint(token))
