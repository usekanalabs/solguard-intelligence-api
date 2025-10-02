"""
AI Service for intelligent analysis and chat
"""
from typing import Dict, Any
import json

class AIService:
    """Service for AI-powered analysis and interactions"""
    
    def __init__(self):
        self.model = "gpt-4"
    
    async def analyze_token_risk(self, context: Dict[str, Any]) -> str:
        """Analyze token risk using AI"""
        prompt = f"""
        Analyze the following Solana token for investment risks and opportunities:
        
        Token Data: {json.dumps(context.get('token_data', {}), indent=2)}
        Liquidity: {json.dumps(context.get('liquidity_data', {}), indent=2)}
        Holders: {json.dumps(context.get('holder_data', {}), indent=2)}
        
        Provide a concise analysis covering:
        1. Overall risk assessment
        2. Key concerns or red flags
        3. Potential opportunities
        4. Market sentiment
        
        Keep response under 200 words.
        """
        
        # In production, integrate with actual AI SDK
        # For now, return structured analysis
        return self._generate_mock_analysis(context)
    
    async def generate_wallet_insights(self, context: Dict[str, Any]) -> str:
        """Generate AI insights for wallet analysis"""
        prompt = f"""
        Analyze this Solana wallet and provide actionable insights:
        
        Portfolio: {json.dumps(context.get('portfolio', {}), indent=2)}
        Suspicious Activities: {context.get('suspicious_activities', [])}
        
        Provide insights on:
        1. Portfolio health and diversification
        2. Risk exposure
        3. Optimization opportunities
        4. Security concerns
        
        Keep response under 200 words.
        """
        
        return self._generate_mock_wallet_insights(context)
    
    async def chat_with_user(self, message: str, context: Dict[str, Any]) -> str:
        """Handle conversational AI chat"""
        system_prompt = """
        You are Kana, an intelligent AI assistant specializing in Solana ecosystem security and guidance.
        You help users navigate the Solana blockchain safely, analyze tokens, manage portfolios, and avoid scams.
        Be helpful, concise, and always prioritize user security.
        """
        
        # In production, use actual AI SDK with conversation history
        return self._generate_mock_chat_response(message, context)
    
    async def analyze_transaction_security(self, transaction_data: Dict, threat_analysis: Dict) -> str:
        """Analyze transaction security using AI"""
        prompt = f"""
        Analyze this Solana transaction for security threats:
        
        Transaction: {json.dumps(transaction_data, indent=2)}
        Detected Threats: {json.dumps(threat_analysis.get('threats', []), indent=2)}
        
        Provide security analysis and recommendation.
        """
        
        return self._generate_mock_security_analysis(transaction_data, threat_analysis)
    
    def _generate_mock_analysis(self, context: Dict) -> str:
        """Generate mock token analysis"""
        token_data = context.get('token_data', {})
        liquidity = context.get('liquidity_data', {})
        
        analysis = f"""
        Based on comprehensive analysis of this token:
        
        The token shows {'verified contract status' if token_data.get('verified') else 'unverified status, which raises concerns'}. 
        Liquidity levels are {'adequate for trading' if liquidity and liquidity.get('total_liquidity', 0) > 50000 else 'concerning and may indicate rug pull risk'}.
        
        Key observations: The holder distribution and market activity suggest {'a healthy, distributed community' if context.get('holder_data', {}).get('holder_count', 0) > 500 else 'concentrated ownership which increases manipulation risk'}.
        
        Recommendation: {'Proceed with caution and only invest amounts you can afford to lose' if token_data.get('verified') else 'Avoid until more information is available'}.
        """
        
        return analysis.strip()
    
    def _generate_mock_wallet_insights(self, context: Dict) -> str:
        """Generate mock wallet insights"""
        portfolio = context.get('portfolio', {})
        suspicious = context.get('suspicious_activities', [])
        
        insights = f"""
        Your wallet analysis reveals:
        
        Portfolio Health: Your diversification score of {portfolio.get('diversification_score', 0)} indicates {'good' if portfolio.get('diversification_score', 0) > 0.5 else 'poor'} asset distribution.
        
        {'⚠️ Security Alert: ' + ', '.join(suspicious) if suspicious else '✅ No suspicious activities detected'}.
        
        Recommendations: {'Consider rebalancing to reduce concentration risk' if portfolio.get('diversification_score', 0) < 0.3 else 'Your portfolio shows healthy diversification'}. 
        Monitor your high-risk holdings closely and consider taking profits on volatile positions.
        """
        
        return insights.strip()
    
    def _generate_mock_chat_response(self, message: str, context: Dict) -> str:
        """Generate mock chat response"""
        message_lower = message.lower()
        
        if 'risk' in message_lower or 'safe' in message_lower:
            return """
            When evaluating risk in the Solana ecosystem, I recommend:
            
            1. Always verify token contracts before investing
            2. Check liquidity levels (aim for >$50k minimum)
            3. Review holder distribution (avoid tokens where top 10 holders own >50%)
            4. Start with small amounts to test
            5. Use stop-loss orders to protect your capital
            
            Would you like me to analyze a specific token for you?
            """
        elif 'portfolio' in message_lower or 'diversif' in message_lower:
            return """
            For optimal portfolio diversification on Solana:
            
            1. Spread investments across 5-10 different tokens
            2. Mix established tokens (SOL, USDC) with growth opportunities
            3. Limit any single position to <20% of portfolio
            4. Regularly rebalance based on performance
            5. Keep some stablecoins for opportunities
            
            I can analyze your current portfolio if you share your wallet address.
            """
        else:
            return """
            I'm here to help you navigate Solana safely! I can assist with:
            
            • Analyzing tokens for risks and opportunities
            • Reviewing your wallet and portfolio
            • Detecting potential scams and threats
            • Providing market insights and recommendations
            
            What would you like help with today?
            """
    
    def _generate_mock_security_analysis(self, transaction_data: Dict, threat_analysis: Dict) -> str:
        """Generate mock security analysis"""
        threats = threat_analysis.get('threats', [])
        risk_score = threat_analysis.get('risk_score', 0)
        
        if risk_score > 0.7:
            return f"""
            🚨 CRITICAL SECURITY ALERT 🚨
            
            This transaction shows multiple red flags: {', '.join(threats)}
            
            RECOMMENDATION: DO NOT PROCEED with this transaction. It exhibits patterns consistent with known scams.
            
            Protect your assets by canceling this transaction immediately.
            """
        elif risk_score > 0.4:
            return f"""
            ⚠️ CAUTION ADVISED
            
            This transaction has some concerning elements: {', '.join(threats) if threats else 'unusual patterns detected'}
            
            RECOMMENDATION: Proceed only if you fully understand and trust the recipient. Consider:
            - Verifying the recipient address
            - Starting with a small test transaction
            - Double-checking the transaction details
            """
        else:
            return """
            ✅ TRANSACTION APPEARS SAFE
            
            No significant threats detected. Standard security checks passed.
            
            RECOMMENDATION: Transaction can proceed, but always verify:
            - Recipient address is correct
            - Amount is as intended
            - You understand the purpose of this transaction
            """
