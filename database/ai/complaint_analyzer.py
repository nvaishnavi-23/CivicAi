"""
AI Complaint Analyzer Module
Supports both Gemini API and fallback rule-based analysis
"""

import os
import json
import re
from typing import Dict, Any


class ComplaintAnalyzer:
    """Main complaint analyzer class"""
    
    def __init__(self, use_gemini=False, api_key=''):
        self.use_gemini = use_gemini and bool(api_key)
        self.api_key = api_key
        self.gemini_model = "gemini-pro-vision"
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    def analyze_complaint(self, category: str, description: str, image_path: str = None)
        """
        Analyze complaint and return category, priority, and department
        
        Args:
            title: Complaint title
            description: Complaint description
            image_path: Optional path to complaint image
            
        Returns:
            Dict with category, priority, priority_reason, department
        """
        if self.use_gemini and self.api_key:
            return self._analyze_with_gemini(title, description, image_path)
        else:
            return self._analyze_with_rules(category, description)
    
    def _analyze_with_rules(self, category: str, description: str) -> Dict[str, Any]:
        """Rule-based complaint analysis (fallback)"""
        
        text = ( description).lower()
        
        # Category detection
        category = category if category else self._detect_category(text)
        
        # Priority detection
        priority, priority_reason = self._detect_priority(text, category)
        
        # Department assignment
        department = self._assign_department(category)
        
        return {
            'category': category,
            'priority': priority,
            'priority_reason': priority_reason,
            'department': department
        }
    
    def _detect_category(self, text: str) -> str:
        """Detect complaint category from text"""
        
        keywords = {
    'Garbage/Waste': [
        'garbage', 'waste', 'trash', 'rubbish', 'litter',
        'dustbin', 'dump', 'dumping', 'dirty waste',
        'solid waste', 'plastic waste', 'food waste',
        'waste material', 'waste dumped', 'garbage dumped',
        'garbage pile', 'waste pile', 'unclean area',
        'dirty area'
    ],

    'Pothole/Road Damage': [
        'pothole', 'potholes', 'pot hole', 'road damage',
        'damaged road', 'broken road', 'road crack',
        'cracked road', 'uneven road', 'bad road',
        'road condition', 'pavement damage', 'asphalt damage'
    ],

    'Streetlight': [
        'streetlight', 'street light', 'street lamp',
        'lamp', 'light pole', 'broken light',
        'light not working', 'light not working',
        'no light', 'dark street', 'dark road',
        'street is dark'
    ],

    'Water Leakage': [
        'water leak', 'water leakage', 'leaking water',
        'pipe leak', 'pipe leakage', 'broken pipe',
        'burst pipe', 'water pipe', 'water wastage',
        'water flowing', 'water coming out'
    ],

    'Drainage': [
        'drainage', 'drain', 'blocked drain',
        'drain blocked', 'clogged drain', 'sewer',
        'sewage', 'stagnant water', 'waterlogging',
        'water logging', 'drain cleaning'
    ],

    'Traffic/Safety': [
        'traffic', 'traffic signal', 'signal not working',
        'accident', 'dangerous', 'danger',
        'traffic jam', 'road safety', 'unsafe',
        'speed breaker', 'vehicle problem'
    ],

    'Public Infrastructure': [
        'park', 'bench', 'playground', 'public toilet',
        'public building', 'footpath', 'sidewalk',
        'street sign', 'signboard', 'public facility',
        'public infrastructure'
    ]
}
        
        for category, keywords_list in keywords.items():
            for keyword in keywords_list:
                if keyword in text:
                    return category
        
        return 'Other'
    
   def _detect_priority(self, text: str, category: str) -> tuple:
    """Detect priority based on severity of the complaint"""

    text = text.lower()

    # Critical = immediate danger to life/safety
    critical_keywords = [
        'accident',
        'injury',
        'injured',
        'death',
        'life threatening',
        'life-threatening',
        'emergency',
        'very dangerous',
        'major accident',
        'electrocution',
        'fire'
    ]

    # High = serious problem needing quick action
    high_keywords = [
        'dangerous',
        'danger',
        'hazard',
        'urgent',
        'severe',
        'major',
        'large',
        'overflowing',
        'blocked',
        'flooding',
        'waterlogging',
        'health risk',
        'health hazard',
        'school',
        'hospital',
        'busy road',
        'heavy traffic'
    ]

    # Check critical first
    if any(keyword in text for keyword in critical_keywords):
        return (
            'Critical',
            'Immediate attention required due to serious safety risk'
        )

    # Category-specific rules
    if category == 'Garbage/Waste':
        if any(word in text for word in [
            'overflowing',
            'huge pile',
            'large pile',
            'health risk',
            'health hazard',
            'bad smell',
            'disease'
        ]):
            return (
                'High',
                'Garbage accumulation may create a health hazard'
            )

        return (
            'Medium',
            'Waste management issue requiring attention'
        )

    elif category == 'Pothole/Road Damage':
        if any(word in text for word in [
            'large pothole',
            'deep pothole',
            'multiple potholes',
            'accident',
            'dangerous',
            'busy road'
        ]):
            return (
                'High',
                'Road damage may create a safety hazard'
            )

        return (
            'Medium',
            'Road repair is required'
        )

    elif category == 'Streetlight':
        if any(word in text for word in [
            'dark',
            'no light',
            'multiple lights',
            'busy road',
            'unsafe',
            'dangerous'
        ]):
            return (
                'High',
                'Poor lighting may create a safety risk'
            )

        return (
            'Medium',
            'Streetlight maintenance is required'
        )

    elif category == 'Water Leakage':
        if any(word in text for word in [
            'burst',
            'flooding',
            'large leak',
            'heavy leakage',
            'water everywhere'
        ]):
            return (
                'High',
                'Significant water leakage requires quick attention'
            )

        return (
            'Medium',
            'Water leakage requires repair'
        )

    elif category == 'Drainage':
        if any(word in text for word in [
            'flooding',
            'waterlogging',
            'sewage overflow',
            'overflowing',
            'blocked completely'
        ]):
            return (
                'High',
                'Drainage problem may cause flooding or health risks'
            )

        return (
            'Medium',
            'Drainage maintenance is required'
        )

    elif category == 'Traffic/Safety':
        return (
            'High',
            'Traffic or public safety issue requires attention'
        )

    elif category == 'Public Infrastructure':
        if any(word in text for word in [
            'dangerous',
            'broken completely',
            'unsafe',
            'collapse'
        ]):
            return (
                'High',
                'Damaged infrastructure may create a safety risk'
            )

        return (
            'Low',
            'Routine infrastructure maintenance required'
        )

    # Other category
    if any(keyword in text for keyword in high_keywords):
        return (
            'High',
            'Issue requires prompt attention'
        )

    return (
        'Medium',
        'General civic maintenance issue'
    )
    
    def _assign_department(self, category: str) -> str:
        """Assign appropriate department based on category"""
        
        department_map = {
            'Pothole/Road Damage': 'Roads Department',
            'Garbage/Waste': 'Sanitation Department',
            'Streetlight': 'Electrical Department',
            'Water Leakage': 'Water Department',
            'Drainage': 'Drainage Department',
            'Traffic/Safety': 'Traffic Department',
            'Public Infrastructure': 'General Civic Department',
            'Other': 'General Civic Department'
        }
        
        return department_map.get(category, 'General Civic Department')
    
    def _analyze_with_gemini(self, title: str, description: str, image_path: str = None) -> Dict[str, Any]:
        """
        Analyze using Google Gemini API
        Note: This is a placeholder. Full implementation requires proper API setup.
        """
        try:
            import requests
            
            # Prepare the prompt
            prompt = f"""
            Analyze this civic complaint and provide:
            1. Category (choose from: Pothole/Road Damage, Garbage/Waste, Streetlight, Water Leakage, Drainage, Traffic/Safety, Public Infrastructure, Other)
            2. Priority (Low, Medium, High, or Critical)
            3. Priority reason (brief explanation)
            4. Department (appropriate municipal department)
            
            Complaint Title: {title}
            Complaint Description: {description}
            
            Respond in JSON format:
            {{
                "category": "...",
                "priority": "...",
                "priority_reason": "...",
                "department": "..."
            }}
            """
            
            # Fallback to rules if API fails
            return self._analyze_with_rules(title, description)
            
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to rule-based analysis.")
            return self._analyze_with_rules(title, description)


# Global analyzer instance
_analyzer = None


def get_analyzer(use_gemini=False, api_key=''):
    """Get or create analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ComplaintAnalyzer(use_gemini=use_gemini, api_key=api_key)
    return _analyzer


def analyze_complaint(title: str, description: str, image_path: str = None) -> Dict[str, Any]:
    """Analyze complaint"""
    analyzer = get_analyzer()
    return analyzer.analyze_complaint(title, description, image_path)