# Google OAuth Setup Guide

Step-by-step guide to configure Google OAuth for Kana API.

## Prerequisites

- Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Kana API")
4. Click "Create"

### 2. Enable Google+ API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type
3. Fill in required information:
   - App name: "Kana API"
   - User support email: your email
   - Developer contact: your email
4. Click "Save and Continue"
5. Add scopes:
   - `openid`
   - `email`
   - `profile`
6. Click "Save and Continue"
7. Add test users (for development)
8. Click "Save and Continue"

### 4. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Web application"
4. Configure:
   - Name: "Kana API Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:8000` (development)
     - `https://your-domain.com` (production)
   - Authorized redirect URIs:
     - `http://localhost:8000/api/auth/google/callback` (development)
     - `https://your-domain.com/api/auth/google/callback` (production)
5. Click "Create"
6. Copy the Client ID and Client Secret

### 5. Configure Environment Variables

Add to your `.env` file:

\`\`\`bash
GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
\`\`\`

### 6. Test the Integration

1. Start your API server:
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`

2. Test the OAuth flow:
   \`\`\`bash
   curl http://localhost:8000/api/v1/auth/google/login
   \`\`\`

3. Visit the returned `auth_url` in your browser

4. Sign in with Google and authorize the app

5. You'll be redirected back with an authorization code

## Production Deployment

### Update Redirect URIs

1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add production redirect URI:
   \`\`\`
   https://your-domain.com/api/auth/google/callback
   \`\`\`

### Update Environment Variables

\`\`\`bash
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback
\`\`\`

### Verify Domain Ownership

For production apps, Google may require domain verification:

1. Go to "OAuth consent screen"
2. Click "Add domain"
3. Follow verification steps

## Security Best Practices

1. **Never commit credentials** - Keep `.env` in `.gitignore`
2. **Use HTTPS in production** - Required by Google OAuth
3. **Rotate secrets regularly** - Generate new client secrets periodically
4. **Limit scopes** - Only request necessary permissions
5. **Validate state parameter** - Prevent CSRF attacks
6. **Monitor usage** - Check Google Cloud Console for suspicious activity

## Troubleshooting

### Error: redirect_uri_mismatch

**Solution:** Ensure the redirect URI in your request exactly matches one configured in Google Cloud Console (including protocol, domain, port, and path).

### Error: invalid_client

**Solution:** Verify your Client ID and Client Secret are correct in `.env`.

### Error: access_denied

**Solution:** User declined authorization. This is normal user behavior.

### Error: invalid_grant

**Solution:** Authorization code expired or already used. Request a new code.

## Testing

Use the provided example:

\`\`\`bash
python examples/google_auth_example.py
\`\`\`

Follow the instructions to complete the OAuth flow.

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
- [Google Cloud Console](https://console.cloud.google.com/)
