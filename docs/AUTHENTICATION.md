# Solana Wallet Authentication

Complete guide for implementing Solana wallet-based authentication with the Kana API.

## Overview

Kana API uses a secure challenge-response authentication flow with Solana wallet signatures. No passwords required - users authenticate by signing a message with their wallet.

## Authentication Flow

\`\`\`
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│ Client  │                    │   API   │                    │ Wallet  │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │  1. Request Challenge        │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │  2. Challenge Message        │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
     │  3. Sign Message             │                              │
     ├──────────────────────────────┼─────────────────────────────>│
     │                              │                              │
     │  4. Signature                │                              │
     │<─────────────────────────────┼──────────────────────────────┤
     │                              │                              │
     │  5. Verify Signature         │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
     │  6. JWT Token                │                              │
     │<─────────────────────────────┤                              │
     │                              │                              │
     │  7. Access Protected Routes  │                              │
     ├─────────────────────────────>│                              │
     │                              │                              │
\`\`\`

## Step-by-Step Implementation

### Step 1: Request Authentication Challenge

\`\`\`bash
POST /api/v1/auth/challenge?wallet_address={WALLET_ADDRESS}
\`\`\`

**Response:**
\`\`\`json
{
  "challenge": "Sign this message to authenticate with Kana API\n\nWallet: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU\nNonce: a1b2c3d4...\nTimestamp: 2025-02-10T12:00:00\n\nThis request will not trigger a blockchain transaction or cost any gas fees.",
  "expires_at": "2025-02-10T12:05:00",
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
\`\`\`

### Step 2: Sign the Challenge Message

Use your Solana wallet to sign the challenge message:

**JavaScript (with @solana/web3.js):**
\`\`\`javascript
import { Connection, PublicKey } from '@solana/web3.js';
import bs58 from 'bs58';

async function signMessage(message, wallet) {
  const encodedMessage = new TextEncoder().encode(message);
  const signature = await wallet.signMessage(encodedMessage);
  return bs58.encode(signature);
}
\`\`\`

**Python (with nacl):**
\`\`\`python
import base58
from nacl.signing import SigningKey

signing_key = SigningKey(private_key_bytes)
signature_bytes = signing_key.sign(message.encode()).signature
signature = base58.b58encode(signature_bytes).decode('ascii')
\`\`\`

### Step 3: Verify Signature and Get Token

\`\`\`bash
POST /api/v1/auth/verify
Content-Type: application/json

{
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
  "signature": "5VERy1ong5ignatur3str1ng...",
  "message": "Sign this message to authenticate..."
}
\`\`\`

**Response:**
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
\`\`\`

### Step 4: Use Token for Protected Routes

Include the JWT token in the Authorization header:

\`\`\`bash
GET /api/v1/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
\`\`\`

## Frontend Integration Examples

### React with Phantom Wallet

\`\`\`typescript
import { useWallet } from '@solana/wallet-adapter-react';
import bs58 from 'bs58';

function useKanaAuth() {
  const { publicKey, signMessage } = useWallet();
  
  async function authenticate() {
    if (!publicKey || !signMessage) {
      throw new Error('Wallet not connected');
    }
    
    // Step 1: Request challenge
    const challengeRes = await fetch(
      `${API_URL}/auth/challenge?wallet_address=${publicKey.toString()}`
    );
    const { challenge } = await challengeRes.json();
    
    // Step 2: Sign message
    const encodedMessage = new TextEncoder().encode(challenge);
    const signature = await signMessage(encodedMessage);
    const signatureBase58 = bs58.encode(signature);
    
    // Step 3: Verify and get token
    const verifyRes = await fetch(`${API_URL}/auth/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_address: publicKey.toString(),
        signature: signatureBase58,
        message: challenge
      })
    });
    
    const { access_token } = await verifyRes.json();
    
    // Store token
    localStorage.setItem('kana_token', access_token);
    
    return access_token;
  }
  
  return { authenticate };
}
\`\`\`

### Python Client

\`\`\`python
import httpx
import base58
from nacl.signing import SigningKey

class KanaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
    
    async def authenticate(self, signing_key: SigningKey):
        """Authenticate with Solana wallet"""
        verify_key = signing_key.verify_key
        wallet_address = base58.b58encode(bytes(verify_key)).decode('ascii')
        
        async with httpx.AsyncClient() as client:
            # Request challenge
            response = await client.post(
                f"{self.base_url}/auth/challenge",
                params={"wallet_address": wallet_address}
            )
            challenge_data = response.json()
            message = challenge_data["challenge"]
            
            # Sign message
            signature_bytes = signing_key.sign(message.encode()).signature
            signature = base58.b58encode(signature_bytes).decode('ascii')
            
            # Verify signature
            response = await client.post(
                f"{self.base_url}/auth/verify",
                json={
                    "wallet_address": wallet_address,
                    "signature": signature,
                    "message": message
                }
            )
            token_data = response.json()
            self.token = token_data["access_token"]
            
            return self.token
    
    def get_headers(self):
        """Get headers with authentication"""
        if not self.token:
            raise ValueError("Not authenticated")
        return {"Authorization": f"Bearer {self.token}"}
\`\`\`

## Protected Routes

To protect your routes, use the authentication middleware:

\`\`\`python
from fastapi import Depends
from middleware.auth_middleware import get_current_user

@router.get("/protected-endpoint")
async def protected_route(current_user: dict = Depends(get_current_user)):
    wallet_address = current_user["wallet_address"]
    # Your protected logic here
    return {"message": f"Hello {wallet_address}"}
\`\`\`

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store JWT_SECRET_KEY** securely (use environment variables)
3. **Implement rate limiting** on authentication endpoints
4. **Set appropriate token expiration** (default: 24 hours)
5. **Use Redis** for challenge and token storage in production
6. **Validate wallet addresses** before processing
7. **Log authentication attempts** for security monitoring

## Token Refresh

\`\`\`bash
POST /api/v1/auth/refresh
Authorization: Bearer {CURRENT_TOKEN}
\`\`\`

## Logout

\`\`\`bash
POST /api/v1/auth/logout
Authorization: Bearer {TOKEN}
\`\`\`

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 401 | Invalid signature or expired token |
| 403 | Token revoked or insufficient permissions |
| 429 | Too many authentication attempts |
| 500 | Server error during authentication |

## Environment Variables

\`\`\`bash
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
\`\`\`

## Testing

Run the example authentication flow:

\`\`\`bash
python examples/auth_example.py
