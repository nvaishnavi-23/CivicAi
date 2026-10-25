"""
CivicAI Chatbot Module
Provides responses to common citizen queries
"""

import re
from typing import Dict, Any


class CivicAIAssistant:
    """CivicAI Chatbot Assistant"""
    
    def __init__(self, use_gemini=False, api_key=''):
        self.use_gemini = use_gemini and bool(api_key)
        self.api_key = api_key
    
    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Get chatbot response for user message
        
        Args:
            user_message: User's question/message
            
        Returns:
            Dict with 'response' and 'type' keys
        """
        message = user_message.lower().strip()
        
        # Try to match with predefined responses
        response = self._match_pattern(message)
        
        if response:
            return {'response': response, 'type': 'answer'}
        
        # If Gemini is available, use it
        if self.use_gemini and self.api_key:
            return self._get_gemini_response(user_message)
        
        # Default response
        return {
            'response': self._get_default_response(message),
            'type': 'answer'
        }
    
    def _match_pattern(self, message: str) -> str:
        """Match user message with predefined patterns"""
        
        patterns = {
            # Reporting complaints
            r'(how|where|can i|how do i).*(report|submit|file|lodge).*(complaint|issue|problem)': 
                self._how_to_report(),
            r'(how|where|can i).*(report|submit).*(pothole|road)': 
                self._report_pothole(),
            r'(how|where|can i).*(report|submit).*(garbage|waste|litter|trash)': 
                self._report_garbage(),
            r'(how|where|can i).*(report|submit).*(streetlight|light|lamp)': 
                self._report_streetlight(),
            r'(how|where|can i).*(report|submit).*(water leak)': 
                self._report_water(),
            r'(how|where|can i).*(report|submit).*(drainage|drain)': 
                self._report_drainage(),
            
            # Checking status
            r'(what is|whats|how is).*(complaint status|status of my complaint|my complaint)':
                self._check_status(),
            r'(track|check|view).*(complaint|issue|problem)':
                self._track_complaint(),
            
            # Understanding system
            r'(what|who|which|who handles).*(pothole|road damage)':
                self._explain_pothole(),
            r'(what|who|which|who handles).*(garbage|waste)':
                self._explain_garbage(),
            r'(what|who|which|who handles).*(streetlight|light)':
                self._explain_streetlight(),
            r'(what|who|which|who handles).*(water|water leak)':
                self._explain_water(),
            r'(what|who|which|who handles).*(drainage|drain)':
                self._explain_drainage(),
            
            # Understanding priorities
            r'(what does|what is|what|explain).*(high priority|critical priority|priority|urgent)':
                self._explain_priority(),
            
            # General help
            r'(help|how does|how does it work|feature|what can|what do)':
                self._explain_system(),
            
            # Greeting
            r'(hello|hi|hey|namaste|greetings)':
                self._greeting(),
            
            # Thanks
            r'(thank|thanks|thankyou|ty|appreciate)':
                self._thank_you()
        }
        
        for pattern, response_func in patterns.items():
            if re.search(pattern, message):
                return response_func
        
        return None
    
    def _how_to_report(self) -> str:
        return (
            "📝 **How to Report a Complaint:**\n\n"
            "1. Click 'Submit Complaint' on your dashboard\n"
            "2. Choose the complaint category\n"
            "3. Enter location/address or use GPS\n"
            "4. Write a detailed description\n"
            "5. Upload a photo if available\n"
            "6. Click 'Submit'\n\n"
            "Your complaint will be analyzed by our AI system and automatically assigned to the right department!"
        )
    
    def _report_pothole(self) -> str:
        return (
            "🕳️ **Report a Pothole:**\n\n"
            "1. Go to 'Submit Complaint'\n"
            "2. Select 'Pothole/Road Damage'\n"
            "3. Describe the location and size\n"
            "4. Add a photo showing the damage\n"
            "5. Explain any safety concerns\n\n"
            "Our system will mark it as High/Critical priority if it's a safety hazard!\n"
            "Department: Roads Department"
        )
    
    def _report_garbage(self) -> str:
        return (
            "🗑️ **Report Garbage Issues:**\n\n"
            "1. Go to 'Submit Complaint'\n"
            "2. Select 'Garbage/Waste'\n"
            "3. Describe the location and situation\n"
            "4. Upload a photo\n"
            "5. Mention if bins are overflowing\n\n"
            "Department: Sanitation Department"
        )
    
    def _report_streetlight(self) -> str:
        return (
            "💡 **Report Broken Streetlight:**\n\n"
            "1. Go to 'Submit Complaint'\n"
            "2. Select 'Streetlight'\n"
            "3. Specify the exact location\n"
            "4. Take a photo if possible\n"
            "5. Mention if it's a safety concern\n\n"
            "Department: Electrical Department"
        )
    
    def _report_water(self) -> str:
        return (
            "💧 **Report Water Leakage:**\n\n"
            "1. Go to 'Submit Complaint'\n"
            "2. Select 'Water Leakage'\n"
            "3. Describe the location\n"
            "4. Upload a photo\n"
            "5. Explain the severity\n\n"
            "Department: Water Department"
        )
    
    def _report_drainage(self) -> str:
        return (
            "🌊 **Report Drainage Issues:**\n\n"
            "1. Go to 'Submit Complaint'\n"
            "2. Select 'Drainage'\n"
            "3. Describe blocked areas\n"
            "4. Photo of water accumulation\n"
            "5. Mention waterlogging risk\n\n"
            "Department: Drainage Department"
        )
    
    def _check_status(self) -> str:
        return (
            "📊 **Check Your Complaint Status:**\n\n"
            "1. Click 'My Complaints' on dashboard\n"
            "2. Find your complaint by ID or category\n"
            "3. Click on it to see full details\n\n"
            "**Status Stages:**\n"
            "✓ Submitted - Received by system\n"
            "✓ Assigned - Assigned to department\n"
            "✓ In Progress - Being worked on\n"
            "✓ Resolved - Issue fixed\n"
            "✗ Rejected - Could not address"
        )
    
    def _track_complaint(self) -> str:
        return (
            "🔍 **Track Your Complaint:**\n\n"
            "1. Log in to your citizen account\n"
            "2. Visit 'My Complaints' section\n"
            "3. See all your submitted complaints\n"
            "4. Click any complaint for details\n"
            "5. View status updates and remarks\n\n"
            "You'll see updates as the department works on your issue!"
        )
    
    def _explain_pothole(self) -> str:
        return (
            "🕳️ **Pothole/Road Damage**\n\n"
            "**Handled by:** Roads Department\n"
            "**Priority:** Usually High or Critical if safety concern\n\n"
            "Issues include:\n"
            "• Holes in road surface\n"
            "• Broken pavement\n"
            "• Uneven road\n"
            "• Cracks in asphalt\n\n"
            "Report immediately if causing accidents!"
        )
    
    def _explain_garbage(self) -> str:
        return (
            "🗑️ **Garbage/Waste Issues**\n\n"
            "**Handled by:** Sanitation Department\n"
            "**Priority:** Medium to High (if overflowing)\n\n"
            "Issues include:\n"
            "• Overflowing trash bins\n"
            "• Littered areas\n"
            "• Improper disposal\n"
            "• Waste accumulation\n\n"
            "Health hazard - report promptly!"
        )
    
    def _explain_streetlight(self) -> str:
        return (
            "💡 **Streetlight Issues**\n\n"
            "**Handled by:** Electrical Department\n"
            "**Priority:** Medium to High (safety concern)\n\n"
            "Issues include:\n"
            "• Broken lights\n"
            "• Dark areas at night\n"
            "• Non-working lamps\n"
            "• Faulty wiring\n\n"
            "Report dark areas immediately for safety!"
        )
    
    def _explain_water(self) -> str:
        return (
            "💧 **Water Leakage**\n\n"
            "**Handled by:** Water Department\n"
            "**Priority:** Medium to High\n\n"
            "Issues include:\n"
            "• Leaking pipes\n"
            "• Burst water mains\n"
            "• Water waste\n"
            "• Flooding from pipes\n\n"
            "Wastes precious resources - report quickly!"
        )
    
    def _explain_drainage(self) -> str:
        return (
            "🌊 **Drainage Issues**\n\n"
            "**Handled by:** Drainage Department\n"
            "**Priority:** High (especially waterlogging)\n\n"
            "Issues include:\n"
            "• Blocked drains\n"
            "• Water accumulation\n"
            "• Waterlogging\n"
            "• Sewage backup\n\n"
            "Risk of disease - report immediately!"
        )
    
    def _explain_priority(self) -> str:
        return (
            "🚨 **Understanding Priority Levels:**\n\n"
            "**🔴 CRITICAL**\n"
            "• Life-threatening safety hazards\n"
            "• Causing injuries or accidents\n"
            "• Extreme water/gas leaks\n"
            "→ Action within 24 hours\n\n"
            "**🟠 HIGH**\n"
            "• Major issues affecting many\n"
            "• Serious safety concerns\n"
            "• Health hazards\n"
            "→ Action within 3-5 days\n\n"
            "**🟡 MEDIUM**\n"
            "• Regular maintenance issues\n"
            "• Moderate inconvenience\n"
            "→ Action within 1-2 weeks\n\n"
            "**🟢 LOW**\n"
            "• Minor cosmetic issues\n"
            "• Routine maintenance\n"
            "→ Action within 1 month"
        )
    
    def _explain_system(self) -> str:
        return (
            "🏛️ **CivicAI - Smart City Platform**\n\n"
            "**What we do:**\n"
            "• Report civic complaints easily\n"
            "• AI analyzes and prioritizes\n"
            "• Automatic department assignment\n"
            "• Real-time status tracking\n"
            "• City-wide problem mapping\n\n"
            "**Key Features:**\n"
            "📱 Mobile-friendly reporting\n"
            "🤖 AI-powered analysis\n"
            "📊 Real-time analytics\n"
            "🗺️ Complaint mapping\n"
            "👥 Admin oversight\n\n"
            "**Get Started:**\n"
            "1. Register as citizen or admin\n"
            "2. Log in to your dashboard\n"
            "3. Citizens: Report issues\n"
            "4. Admins: Manage complaints"
        )
    
    def _greeting(self) -> str:
        return (
            "👋 **Hello!**\n\n"
            "I'm CivicAI Assistant! I'm here to help you report and track civic complaints.\n\n"
            "I can help with:\n"
            "❓ How to report different issues\n"
            "📊 Checking complaint status\n"
            "🏛️ Understanding departments\n"
            "🚨 Priority levels\n\n"
            "What would you like to know?"
        )
    
    def _thank_you(self) -> str:
        return (
            "😊 **You're welcome!**\n\n"
            "Thank you for helping keep our city clean and safe!\n\n"
            "If you have more questions, just ask me anytime. 🙏"
        )
    
    def _get_default_response(self, message: str) -> str:
        """Default response for unmatched queries"""
        return (
            "🤔 **I'm not sure I understood that.**\n\n"
            "I can help with:\n"
            "• **How to report** issues (pothole, garbage, light, etc.)\n"
            "• **Check status** of your complaints\n"
            "• **Understand** complaint types and priorities\n"
            "• **Learn about** which department handles what\n\n"
            "Try asking: 'How do I report a pothole?' or 'What is High Priority?'"
        )
    
    def _get_gemini_response(self, user_message: str) -> Dict[str, Any]:
        """Get response from Gemini API (placeholder)"""
        # Fallback to default
        return {
            'response': self._get_default_response(user_message),
            'type': 'answer'
        }


# Global assistant instance
_assistant = None


def get_assistant(use_gemini=False, api_key=''):
    """Get or create assistant instance"""
    global _assistant
    if _assistant is None:
        _assistant = CivicAIAssistant(use_gemini=use_gemini, api_key=api_key)
    return _assistant


def chat(user_message: str) -> Dict[str, Any]:
    """Chat with CivicAI Assistant"""
    assistant = get_assistant()
    return assistant.get_response(user_message)