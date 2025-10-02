# Authentication Guide

Complete guide for implementing authentication with the Kana API. Supports both Solana wallet-based authentication and Google OAuth.

## Overview

Kana API provides two authentication methods:

1. **Solana Wallet Authentication** (Primary) - Secure challenge-response flow using wallet signatures
2. **Google OAuth** (Optional) - Traditional email-based authentication with optional wallet linking

## Authentication Methods

### Method 1: Solana Wallet Authentication

Secure, passwordless authentication using Solana wallet signatures.

#### Authentication Flow

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

#### Step-by-Step Implementation

##### Step 1: Request Authentication Challenge

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

##### Step 2: Sign the Challenge Message

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

##### Step 3: Verify Signature and Get Token

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

##### Step 4: Use Token for Protected Routes

Include the JWT token in the Authorization header:

\`\`\`bash
GET /api/v1/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
\`\`\`

### Method 2: Google OAuth (Optional)

Traditional email-based authentication using Google OAuth 2.0.

#### Setup Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - Development: `http://localhost:8000/api/auth/google/callback`
   - Production: `https://your-domain.com/api/auth/google/callback`
6. Copy Client ID and Client Secret to `.env`

#### Environment Variables

\`\`\`bash
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
\`\`\`

#### OAuth Flow

**Step 1: Get Authorization URL**

\`\`\`bash
GET /api/v1/auth/google/login
\`\`\`

**Response:**
\`\`\`json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "redirect_uri": "http://localhost:8000/api/auth/google/callback"
}
\`\`\`

**Step 2: Redirect User to Google**

Redirect the user to the `auth_url`. After authorization, Google redirects back with a code.

**Step 3: Exchange Code for Token**

\`\`\`bash
POST /api/v1/auth/google/callback
Content-Type: application/json

{
  "code": "authorization_code_from_google",
  "redirect_uri": "http://localhost:8000/api/auth/google/callback"
}
\`\`\`

**Response:**
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "email": "user@gmail.com",
  "wallet_address": null,
  "auth_method": "google"
}
\`\`\`

#### Link Wallet to Google Account

Users authenticated with Google can link their Solana wallet:

\`\`\`bash
POST /api/v1/auth/link-wallet?wallet_address={WALLET_ADDRESS}
Authorization: Bearer {GOOGLE_AUTH_TOKEN}
\`\`\`

**Response:**
\`\`\`json
{
  "message": "Wallet linked successfully",
  "email": "user@gmail.com",
  "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
}
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

### React with Google OAuth

\`\`\`typescript
import { GoogleOAuthProvider, useGoogleLogin } from '@react-oauth/google';

function GoogleAuthButton() {
  const handleGoogleAuth = async (credentialResponse) => {
    // Get authorization URL
    const loginRes = await fetch(`${API_URL}/auth/google/login`);
    const { auth_url } = await loginRes.json();
    
    // Redirect to Google
    window.location.href = auth_url;
  };
  
  // Handle callback (in your callback page)
  async function handleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code) {
      const response = await fetch(`${API_URL}/auth/google/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          redirect_uri: window.location.origin + '/auth/callback'
        })
      });
      
      const { access_token } = await response.json();
      localStorage.setItem('kana_token', access_token);
    }
  }
  
  return <button onClick={handleGoogleAuth}>Sign in with Google</button>;
}
\`\`\`

### React with Both Auth Methods

\`\`\`typescript
function AuthComponent() {
  const { publicKey, signMessage } = useWallet(); // Phantom wallet
  
  // Wallet authentication
  async function authenticateWithWallet() {
    // ... existing wallet auth code ...
  }
  
  // Google authentication
  async function authenticateWithGoogle() {
    const loginRes = await fetch(`${API_URL}/auth/google/login`);
    const { auth_url } = await loginRes.json();
    window.location.href = auth_url;
  }
  
  return (
    <div>
      <button onClick={authenticateWithWallet}>
        Connect Wallet
      </button>
      <button onClick={authenticateWithGoogle}>
        Sign in with Google
      </button>
    </div>
  );
}
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

## API Endpoints Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/auth/challenge` | POST | No | Request wallet challenge |
| `/auth/verify` | POST | No | Verify wallet signature |
| `/auth/google/login` | GET | No | Get Google OAuth URL |
| `/auth/google/callback` | POST | No | Exchange Google code for token |
| `/auth/link-wallet` | POST | Yes (Google) | Link wallet to Google account |
| `/auth/refresh` | POST | Yes | Refresh JWT token |
| `/auth/profile` | GET | Yes | Get user profile |
| `/auth/logout` | POST | Yes | Logout user |

## Security Best Practices

1. **Always use HTTPS** in production
2. **Store secrets securely** (JWT_SECRET_KEY, GOOGLE_CLIENT_SECRET)
3. **Implement rate limiting** on authentication endpoints
4. **Set appropriate token expiration** (default: 24 hours)
5. **Use Redis** for challenge and token storage in production
6. **Validate wallet addresses** and email addresses
7. **Log authentication attempts** for security monitoring
8. **Use state parameter** in OAuth flow to prevent CSRF
9. **Verify email** from Google OAuth response

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

## Testing

Run the example authentication flow:

\`\`\`bash
python examples/auth_example.py
