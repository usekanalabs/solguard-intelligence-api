"""
Example: Google OAuth authentication with Kana API
"""
import asyncio
import httpx
from typing import Optional

API_BASE_URL = "http://localhost:8000/api/v1"

class GoogleAuthExample:
    """Example Google OAuth authentication flow"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.email: Optional[str] = None
    
    async def get_auth_url(self) -> str:
        """
        Step 1: Get Google OAuth authorization URL
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/auth/google/login")
            data = response.json()
            
            print(f"Authorization URL: {data['auth_url']}")
            print(f"\nPlease visit this URL in your browser to authorize.")
            print(f"After authorization, you'll be redirected with a 'code' parameter.")
            
            return data['auth_url']
    
    async def authenticate_with_code(self, code: str, redirect_uri: str):
        """
        Step 2: Exchange authorization code for JWT token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/auth/google/callback",
                json={
                    "code": code,
                    "redirect_uri": redirect_uri
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.email = data["email"]
                
                print(f"\n✓ Authentication successful!")
                print(f"Email: {self.email}")
                print(f"Token: {self.token[:50]}...")
                
                return data
            else:
                print(f"\n✗ Authentication failed: {response.text}")
                return None
    
    async def get_profile(self):
        """
        Get authenticated user profile
        """
        if not self.token:
            print("Not authenticated. Please authenticate first.")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/auth/profile",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                profile = response.json()
                print(f"\n✓ Profile retrieved:")
                print(f"Email: {profile.get('email')}")
                print(f"Auth Method: {profile.get('auth_method')}")
                print(f"Linked Accounts: {profile.get('linked_accounts')}")
                return profile
            else:
                print(f"\n✗ Failed to get profile: {response.text}")
                return None
    
    async def link_wallet(self, wallet_address: str):
        """
        Link a Solana wallet to the Google account
        """
        if not self.token:
            print("Not authenticated. Please authenticate first.")
            return None
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/auth/link-wallet",
                params={"wallet_address": wallet_address},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Wallet linked successfully!")
                print(f"Email: {data['email']}")
                print(f"Wallet: {data['wallet_address']}")
                return data
            else:
                print(f"\n✗ Failed to link wallet: {response.text}")
                return None

async def main():
    """
    Run Google OAuth authentication example
    """
    print("=" * 60)
    print("Kana API - Google OAuth Authentication Example")
    print("=" * 60)
    
    auth = GoogleAuthExample()
    
    # Step 1: Get authorization URL
    print("\n[Step 1] Getting Google OAuth URL...")
    auth_url = await auth.get_auth_url()
    
    # In a real application, you would:
    # 1. Redirect user to auth_url
    # 2. User authorizes on Google
    # 3. Google redirects back with code
    # 4. Extract code from redirect URL
    
    print("\n" + "=" * 60)
    print("Manual Steps Required:")
    print("=" * 60)
    print("1. Visit the authorization URL above")
    print("2. Sign in with your Google account")
    print("3. Copy the 'code' parameter from the redirect URL")
    print("4. Run this script again with the code:")
    print("   python examples/google_auth_example.py --code YOUR_CODE")
    print("=" * 60)
    
    # Example: If you have a code, authenticate
    # code = "your_authorization_code_here"
    # redirect_uri = "http://localhost:8000/api/auth/google/callback"
    # await auth.authenticate_with_code(code, redirect_uri)
    # await auth.get_profile()
    
    # Example: Link wallet (after authentication)
    # wallet_address = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
    # await auth.link_wallet(wallet_address)

if __name__ == "__main__":
    asyncio.run(main())
