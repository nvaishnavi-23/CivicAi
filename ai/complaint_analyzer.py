"""
CivicAI - AI Complaint Analyzer

Features:
1. Gemini Vision image validation
2. Complaint text analysis
3. Category detection
4. Priority detection
5. Department assignment
6. Rule-based fallback
"""

import os
import json
import re
import base64
from typing import Dict, Any


class ComplaintAnalyzer:
    """Main complaint analyzer class"""

    CATEGORIES = [
        'Pothole/Road Damage',
        'Garbage/Waste',
        'Streetlight',
        'Water Leakage',
        'Drainage',
        'Traffic/Safety',
        'Public Infrastructure',
        'Other'
    ]

    def __init__(self, use_gemini=False, api_key=''):
        self.use_gemini = bool(use_gemini and api_key)
        self.api_key = api_key

        # Gemini multimodal model
        self.gemini_model = "gemini-2.5-flash"

        self.gemini_api_url = (
            "https://generativelanguage.googleapis.com/v1beta/models"
        )

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze_complaint(
        self,
        description: str,
        image_path: str = None,
        selected_category: str = None
    ) -> Dict[str, Any]:

        image_valid = True
        image_reason = ""

        # -----------------------------------------------------
        # IMAGE VALIDATION
        # -----------------------------------------------------

        if image_path and selected_category:

            if self.use_gemini:

                image_valid, image_reason = (
                    self._validate_image_with_gemini(
                        image_path,
                        selected_category,
                        description
                    )
                )

            else:

                image_valid = True

                image_reason = (
                    "AI image validation is disabled."
                )

        # -----------------------------------------------------
        # TEXT ANALYSIS
        # -----------------------------------------------------

        if self.use_gemini:

            try:

                result = self._analyze_with_gemini(
                    description,
                    image_path,
                    selected_category
                )

            except Exception as e:

                print(
                    f"Gemini analysis error: {e}"
                )

                result = self._analyze_with_rules(
                    description,
                    selected_category
                )

        else:

            result = self._analyze_with_rules(
                description,
                selected_category
            )

        result['image_valid'] = image_valid
        result['image_reason'] = image_reason

        return result

    # =========================================================
    # RULE-BASED ANALYSIS
    # =========================================================

    def _analyze_with_rules(
        self,
        description: str,
        selected_category: str = None
    ) -> Dict[str, Any]:

        text = description.lower().strip()

        if selected_category in self.CATEGORIES:
            category = selected_category
        else:
            category = self._detect_category(text)

        priority, priority_reason = self._detect_priority(
            text,
            category
        )

        department = self._assign_department(category)

        title = self._generate_title(
            description,
            category
        )

        return {
            'title': title,
            'category': category,
            'priority': priority,
            'priority_reason': priority_reason,
            'department': department
        }

    # =========================================================
    # TITLE
    # =========================================================

    def _generate_title(
        self,
        description: str,
        category: str
    ) -> str:

        description = description.strip()

        first_sentence = re.split(
            r'[.!?]',
            description
        )[0].strip()

        if len(first_sentence) > 60:

            first_sentence = (
                first_sentence[:60]
                .rsplit(' ', 1)[0]
            )

        if first_sentence:
            return first_sentence

        return category

    # =========================================================
    # CATEGORY DETECTION
    # =========================================================

    def _detect_category(
        self,
        text: str
    ) -> str:

        keywords = {

            'Pothole/Road Damage': [
                'pothole',
                'potholes',
                'pot hole',
                'road damage',
                'broken road',
                'road crack',
                'cracked road',
                'asphalt',
                'pavement',
                'uneven road',
                'damaged road',
                'road repair',
                'broken pavement',
                'road condition'
            ],

            'Garbage/Waste': [
                'garbage',
                'waste',
                'trash',
                'litter',
                'rubbish',
                'dustbin',
                'garbage dump',
                'littered',
                'solid waste',
                'junk',
                'debris',
                'dump'
            ],

            'Streetlight': [
                'streetlight',
                'street light',
                'lighting',
                'lamp',
                'broken light',
                'dark',
                'no light',
                'electricity',
                'bulb',
                'street lamp',
                'light pole'
            ],

            'Water Leakage': [
                'water leak',
                'water leakage',
                'leaking',
                'pipe burst',
                'water pipe',
                'water loss',
                'leakage',
                'water waste',
                'burst pipe',
                'water problem'
            ],

            'Drainage': [
                'drainage',
                'drain',
                'blocked drain',
                'clogged',
                'waterlogging',
                'water accumulation',
                'drain cleaning',
                'stagnant water',
                'water logging',
                'sewage'
            ],

            'Traffic/Safety': [
                'traffic',
                'signal',
                'accident',
                'safety',
                'vehicle',
                'dangerous',
                'hazard',
                'speed breaker',
                'safety concern',
                'traffic jam',
                'road safety'
            ],

            'Public Infrastructure': [
                'park',
                'bench',
                'playground',
                'public facility',
                'infrastructure',
                'building',
                'public space',
                'facility',
                'amenity',
                'monument'
            ]
        }

        for category, keyword_list in keywords.items():

            for keyword in keyword_list:

                if keyword in text:
                    return category

        return 'Other'

    # =========================================================
    # PRIORITY
    # =========================================================

    def _detect_priority(
        self,
        text: str,
        category: str
    ) -> tuple:

        critical_keywords = [
            'accident',
            'death',
            'injury',
            'danger',
            'dangerous',
            'immediate',
            'critical',
            'urgent',
            'emergency',
            'hazard',
            'risk',
            'safety hazard',
            'life threatening'
        ]

        high_keywords = [
            'major',
            'large',
            'severe',
            'significant',
            'blocking',
            'flooding',
            'blocked',
            'overflowing',
            'health',
            'disease',
            'unwell',
            'problem'
        ]

        if any(
            keyword in text
            for keyword in critical_keywords
        ):

            return (
                'Critical',
                'Safety hazard or urgent maintenance needed'
            )

        if category == 'Pothole/Road Damage':

            if any(
                keyword in text
                for keyword in high_keywords
            ):

                return (
                    'High',
                    'Road damage affecting multiple areas or large damage'
                )

            return (
                'Medium',
                'Road damage requiring routine repair'
            )

        elif category == 'Garbage/Waste':

            if (
                'overflowing' in text
                or 'accumulation' in text
            ):

                return (
                    'High',
                    'Health hazard - overflowing garbage'
                )

            return (
                'Medium',
                'Waste management issue'
            )

        elif category == 'Streetlight':

            if (
                'dark' in text
                or 'night' in text
            ):

                return (
                    'High',
                    'Safety concern - dark area at night'
                )

            return (
                'Medium',
                'Lighting maintenance required'
            )

        elif category == 'Water Leakage':

            if (
                'burst' in text
                or 'flooding' in text
            ):

                return (
                    'High',
                    'Resource waste and flooding risk'
                )

            return (
                'Medium',
                'Water loss - routine repair needed'
            )

        elif category == 'Drainage':

            if (
                'waterlogging' in text
                or 'flooding' in text
            ):

                return (
                    'High',
                    'Risk of waterlogging and disease'
                )

            return (
                'Medium',
                'Drainage maintenance required'
            )

        elif category == 'Traffic/Safety':

            return (
                'High',
                'Traffic hazard'
            )

        elif category == 'Public Infrastructure':

            return (
                'Low',
                'Routine maintenance'
            )

        else:

            if any(
                keyword in text
                for keyword in high_keywords
            ):

                return (
                    'High',
                    'Issue requires attention'
                )

            return (
                'Medium',
                'General maintenance needed'
            )

    # =========================================================
    # DEPARTMENT
    # =========================================================

    def _assign_department(
        self,
        category: str
    ) -> str:

        department_map = {

            'Pothole/Road Damage':
                'Roads Department',

            'Garbage/Waste':
                'Sanitation Department',

            'Streetlight':
                'Electrical Department',

            'Water Leakage':
                'Water Department',

            'Drainage':
                'Drainage Department',

            'Traffic/Safety':
                'Traffic Department',

            'Public Infrastructure':
                'General Civic Department',

            'Other':
                'General Civic Department'
        }

        return department_map.get(
            category,
            'General Civic Department'
        )

    # =========================================================
    # GEMINI IMAGE VALIDATION
    # =========================================================

    def _validate_image_with_gemini(
        self,
        image_path: str,
        selected_category: str,
        description: str
    ):

        try:

            import requests

            if not os.path.exists(image_path):

                return (
                    False,
                    'Uploaded image could not be found.'
                )

            # Read image
            with open(
                image_path,
                'rb'
            ) as image_file:

                image_bytes = image_file.read()

            encoded_image = (
                base64.b64encode(
                    image_bytes
                ).decode('utf-8')
            )

            # Determine MIME type
            extension = (
                os.path.splitext(
                    image_path
                )[1].lower()
            )

            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }

            mime_type = mime_types.get(
                extension,
                'image/jpeg'
            )

            prompt = f"""
You are an image verification AI for CivicAI,
a Smart City Complaint Management System.

The citizen selected this complaint category:

{selected_category}

The citizen's complaint description is:

{description}

Look carefully at the uploaded image.

Your job is to determine whether the image
actually shows visual evidence related to the
selected civic complaint category.

CATEGORY RULES:

Pothole/Road Damage:
The image should show a pothole, damaged road,
road crack, broken pavement, or similar road problem.

Garbage/Waste:
The image should show garbage, trash, waste,
litter, garbage piles, or overflowing bins.

Streetlight:
The image should show a streetlight, lamp,
light pole, broken light, or related infrastructure.

Water Leakage:
The image should show leaking water, a leaking
pipe, burst pipe, or visible water escaping from
water infrastructure.

Drainage:
The image should show a drain, blocked drain,
sewage, stagnant water, or waterlogging.

Traffic/Safety:
The image should show a traffic signal,
traffic-related infrastructure, road safety
hazard, damaged sign, or similar civic safety issue.

Public Infrastructure:
The image should show damaged public infrastructure,
public facilities, benches, playground equipment,
public buildings, or similar civic infrastructure.

Other:
Accept only if the image clearly shows a genuine
civic/public problem.

IMPORTANT:

Reject the image if it is:

- A book
- Food
- Restaurant photo
- Selfie
- Personal photo
- Animal
- Pet
- Product
- Shopping item
- Random scenery
- Screenshot
- Meme
- Normal household object
- Unrelated photograph
- Any image that does not provide evidence
  of the selected civic issue

DO NOT decide based on the filename.

Look at the actual image.

Return ONLY valid JSON.

For a matching image:

{{
    "valid": true,
    "reason": "The image clearly shows evidence of the selected civic issue."
}}

For an unrelated image:

{{
    "valid": false,
    "reason": "The uploaded image does not show the selected civic issue."
}}
"""

            url = (
                f"{self.gemini_api_url}/"
                f"{self.gemini_model}:generateContent"
                f"?key={self.api_key}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": encoded_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 200
                }
            }

            response = requests.post(
                url,
                json=payload,
                timeout=30
            )

            print(
                "GEMINI IMAGE STATUS:",
                response.status_code
            )

            print(
                "GEMINI IMAGE RESPONSE:",
                response.text[:1000]
            )

            response.raise_for_status()

            data = response.json()

            text = (
                data['candidates'][0]
                ['content']['parts'][0]['text']
            )

            text = text.strip()

            # Remove markdown code fences
            text = re.sub(
                r'^```json\s*',
                '',
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r'\s*```$',
                '',
                text
            )

            result = json.loads(text)

            valid = bool(
                result.get(
                    'valid',
                    False
                )
            )

            reason = result.get(
                'reason',
                'Image verification completed.'
            )

            return valid, reason

        except Exception as e:

            print(
                f"IMAGE VALIDATION ERROR: {e}"
            )

            # If Gemini fails, reject the image instead
            # of silently accepting an unverified image.

            return (
                False,
                'Image verification failed. Please try again.'
            )

    # =========================================================
    # GEMINI TEXT + IMAGE ANALYSIS
    # =========================================================

    def _analyze_with_gemini(
        self,
        description: str,
        image_path: str = None,
        selected_category: str = None
    ) -> Dict[str, Any]:

        try:

            import requests

            prompt = f"""
Analyze this civic complaint.

Citizen selected category:
{selected_category}

Complaint description:
{description}

Choose the appropriate category from:

Pothole/Road Damage
Garbage/Waste
Streetlight
Water Leakage
Drainage
Traffic/Safety
Public Infrastructure
Other

Determine:

Priority:
Low, Medium, High, or Critical

Priority reason:
Brief explanation

Department:
Appropriate municipal department

Return ONLY valid JSON:

{{
    "title": "...",
    "category": "...",
    "priority": "...",
    "priority_reason": "...",
    "department": "..."
}}
"""

            parts = [
                {
                    "text": prompt
                }
            ]

            # Add image to Gemini analysis if available
            if (
                image_path
                and os.path.exists(image_path)
            ):

                with open(
                    image_path,
                    'rb'
                ) as image_file:

                    image_bytes = image_file.read()

                encoded_image = (
                    base64.b64encode(
                        image_bytes
                    ).decode('utf-8')
                )

                extension = (
                    os.path.splitext(
                        image_path
                    )[1].lower()
                )

                mime_types = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }

                mime_type = mime_types.get(
                    extension,
                    'image/jpeg'
                )

                parts.append(
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encoded_image
                        }
                    }
                )

            payload = {
                "contents": [
                    {
                        "parts": parts
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500
                }
            }

            url = (
                f"{self.gemini_api_url}/"
                f"{self.gemini_model}:generateContent"
                f"?key={self.api_key}"
            )

            response = requests.post(
                url,
                json=payload,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            text = (
                data['candidates'][0]
                ['content']['parts'][0]['text']
            )

            text = text.strip()

            text = re.sub(
                r'^```json\s*',
                '',
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r'\s*```$',
                '',
                text
            )

            result = json.loads(text)

            # Safety defaults
            result.setdefault(
                'title',
                self._generate_title(
                    description,
                    selected_category or 'Other'
                )
            )

            result.setdefault(
                'category',
                selected_category or 'Other'
            )

            result.setdefault(
                'priority',
                'Medium'
            )

            result.setdefault(
                'priority_reason',
                'AI analysis'
            )

            result.setdefault(
                'department',
                self._assign_department(
                    result['category']
                )
            )

            return result

        except Exception as e:

            print(
                f"Gemini analysis error: {e}"
            )

            return self._analyze_with_rules(
                description,
                selected_category
            )


# =============================================================
# GLOBAL ANALYZER
# =============================================================

_analyzer = None


def get_analyzer(
    use_gemini=False,
    api_key=''
):

    global _analyzer

    if _analyzer is None:

        _analyzer = ComplaintAnalyzer(
            use_gemini=use_gemini,
            api_key=api_key
        )

    return _analyzer


# =============================================================
# PUBLIC FUNCTION
# =============================================================

def analyze_complaint(
    description: str,
    image_path: str = None,
    selected_category: str = None
) -> Dict[str, Any]:

    analyzer = get_analyzer()

    return analyzer.analyze_complaint(
        description,
        image_path,
        selected_category
    )