# 🛡️ Solguard intelligence api by Kana


![enter image description here](https://olive-chemical-haddock-701.mypinata.cloud/ipfs/bafybeifiwbcrtgefhno6e3gzx74hrofwraz4qqs5mb3cr52mxci7b3wcpu)

**Your intelligent companion for navigating the Solana ecosystem safely.**

Kana is an advanced AI-powered backend API that provides comprehensive security analysis, threat detection, and intelligent guidance for Solana blockchain users. Built with FastAPI and integrated with cutting-edge AI models, Kana helps protect your digital assets from emerging threats while providing actionable insights.

---

## ✨ Features

### 🪙 Coin Analyzer
- **Comprehensive Token Analysis**: Deep dive into any Solana token with multi-factor risk assessment
- **Liquidity Analysis**: Real-time liquidity pool monitoring across major DEXs
- **Holder Distribution**: Detect whale concentration and manipulation risks
- **Smart Contract Verification**: Automated contract security checks
- **AI-Powered Risk Scoring**: Machine learning models that adapt to new threat patterns
- **Red/Green Flag Detection**: Instant visual indicators of token safety
- **Trending Tokens**: Curated list of trending tokens with safety scores

### 💼 Wallet Assistant AI
- **Portfolio Analysis**: Comprehensive portfolio health and diversification metrics
- **Transaction Pattern Analysis**: Detect unusual activity and suspicious patterns
- **Conversational AI**: Natural language interface for personalized guidance
- **Security Monitoring**: Real-time alerts for suspicious activities
- **Portfolio Optimization**: AI-driven recommendations for better asset allocation
- **Personalized Watchlists**: Custom token recommendations based on your activity

### 🔒 Security & Threat Detection
- **Pre-Transaction Analysis**: Scan transactions before execution
- **Scam Database**: Continuously updated database of known malicious addresses
- **Phishing Detection**: AI-powered identification of phishing attempts
- **Malicious Contract Detection**: Automated analysis of smart contract risks
- **Community Reporting**: Crowdsourced threat intelligence
- **Real-time Threat Alerts**: Instant notifications of emerging threats

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone or download the repository**

2. **Create a virtual environment**
\`\`\`bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Configure environment variables**
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

5. **Run the API**
\`\`\`bash
python main.py
\`\`\`

The API will be available at `http://localhost:8000`

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Coin Analyzer

**POST /api/v1/coin/analyze**
\`\`\`json
{
  "token_address": "TokenAddress111111111111111111111111",
  "include_social": true,
  "include_liquidity": true
}
\`\`\`

Response includes:
- Risk score (0-1)
- Risk level (low/medium/high/critical)
- Red flags and green flags
- AI-powered analysis
- Actionable recommendations

**GET /api/v1/coin/trending**

Get trending Solana tokens with safety scores.

**GET /api/v1/coin/watchlist/{wallet_address}**

Get personalized token watchlist based on wallet activity.

---

#### Wallet Assistant

**POST /api/v1/wallet/analyze**
\`\`\`json
{
  "wallet_address": "WalletAddress1111111111111111111111111",
  "analyze_transactions": true,
  "check_suspicious_activity": true
}
\`\`\`

Response includes:
- Portfolio composition
- Risk assessment
- Suspicious activity alerts
- AI-generated insights
- Optimization recommendations

**POST /api/v1/wallet/chat**
\`\`\`json
{
  "message": "How can I diversify my portfolio?",
  "wallet_address": "WalletAddress1111111111111111111111111"
}
\`\`\`

Chat with AI assistant for personalized guidance.

**GET /api/v1/wallet/portfolio/{wallet_address}**

Get detailed portfolio summary with AI insights.

---

#### Security

**POST /api/v1/security/detect-threat**
\`\`\`json
{
  "transaction_data": {
    "recipient": "RecipientAddress111111111111111111",
    "amount": 100,
    "contract_interaction": true
  },
  "wallet_address": "YourWalletAddress111111111111111111"
}
\`\`\`

Analyze transaction for threats before execution.

**GET /api/v1/security/scam-database**

Get list of known scam addresses and patterns.

**POST /api/v1/security/report-scam**

Report a suspected scam address to the community.

---

## 🏗️ Architecture

\`\`\`
kana-api/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── models/
│   └── schemas.py        # Pydantic models for validation
├── routes/
│   ├── coin_analyzer.py  # Coin analysis endpoints
│   ├── wallet_assistant.py # Wallet AI endpoints
│   └── security.py       # Security endpoints
└── services/
    ├── ai_service.py     # AI integration service
    ├── solana_service.py # Solana blockchain service
    └── security_service.py # Security analysis service
\`\`\`

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Runtime environment | `development` |
| `PORT` | API server port | `8000` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - |
| `SOLANA_RPC_URL` | Solana RPC endpoint | `https://api.mainnet-beta.solana.com` |
| `MAX_RISK_SCORE` | Maximum acceptable risk score | `0.7` |
| `THREAT_DETECTION_ENABLED` | Enable threat detection | `true` |

---

## 🤖 AI Integration

Kana uses advanced AI models for:

- **Risk Assessment**: Multi-factor analysis of tokens and transactions
- **Natural Language Processing**: Conversational interface for user guidance
- **Pattern Recognition**: Detection of suspicious activities and scams
- **Predictive Analytics**: Forecasting potential threats
- **Adaptive Learning**: Continuous improvement from new data

### Supported AI Models

- GPT-4 (default)
- GPT-3.5-turbo
- Custom fine-tuned models

---

## 🔐 Security Best Practices

1. **Never share your private keys** - Kana only needs public addresses
2. **Verify all transactions** - Always double-check before confirming
3. **Start small** - Test with small amounts first
4. **Enable 2FA** - Use additional security layers
5. **Keep software updated** - Regular updates include security patches
6. **Report suspicious activity** - Help the community stay safe

---

## 📊 Risk Scoring System

Kana uses a comprehensive risk scoring system (0-1):

- **0.00 - 0.25**: Low Risk ✅
- **0.25 - 0.50**: Medium Risk ⚠️
- **0.50 - 0.75**: High Risk 🔶
- **0.75 - 1.00**: Critical Risk 🚨

### Risk Factors

- Liquidity levels
- Holder concentration
- Contract verification status
- Token age
- Transaction patterns
- Known scam indicators
- Community reports

---

## 🛠️ Development

### Running in Development Mode

\`\`\`bash
# With auto-reload
uvicorn main:app --reload --port 8000
\`\`\`

### Running Tests

\`\`\`bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
\`\`\`

### Code Style

\`\`\`bash
# Install formatting tools
pip install black flake8

# Format code
black .

# Lint code
flake8 .
\`\`\`

---

## 🚢 Deployment

### Production Deployment

1. **Set environment to production**
\`\`\`bash
ENVIRONMENT=production
\`\`\`

2. **Use production-grade ASGI server**
\`\`\`bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
\`\`\`

3. **Enable HTTPS** - Always use SSL/TLS in production

4. **Set up monitoring** - Use tools like Prometheus, Grafana

5. **Configure rate limiting** - Protect against abuse

### Docker Deployment

\`\`\`dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
\`\`\`

---

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- Additional security checks
- More AI models integration
- Enhanced threat detection algorithms
- UI/UX improvements
- Documentation enhancements
- Test coverage

---

## 📝 API Rate Limits

- **Default**: 60 requests per minute per IP
- **Authenticated**: 120 requests per minute
- **Enterprise**: Custom limits available

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: API won't start
- Check Python version (3.9+)
- Verify all dependencies installed
- Check port 8000 is available

**Issue**: AI features not working
- Verify `OPENAI_API_KEY` is set
- Check API key has sufficient credits
- Ensure network connectivity

**Issue**: Solana data not loading
- Verify `SOLANA_RPC_URL` is accessible
- Check RPC endpoint rate limits
- Try alternative RPC providers

---

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: Report bugs and feature requests
- **Community**: Join our Discord/Telegram

---

## 📄 License

MIT License - feel free to use Kana in your projects!

---

## 🙏 Acknowledgments

- Solana Foundation
- FastAPI framework
- OpenAI for AI capabilities
- The Solana developer community

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Mobile SDK
- [ ] Browser extension
- [ ] Multi-chain support (Ethereum, BSC, etc.)
- [ ] Advanced portfolio analytics
- [ ] Social trading features
- [ ] Automated trading strategies
- [ ] NFT security analysis

---

**Built with ❤️ for the Solana community**

*Kana - Protecting your digital assets, one transaction at a time.*
