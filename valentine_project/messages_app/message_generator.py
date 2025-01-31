import requests
from datetime import datetime

class ValentineMessageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.templates = {
    'spouse': [
        "**My beloved {recipient_name},💖**\n\n"
        "**After all our time together, my love for you only grows stronger. 🌹**"
        "**{personalized_content}**\n\n"
        "**You are my soulmate, my best friend, and my everything. 💑**"
        "**Thank you for being the most amazing spouse.**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**Forever yours,**\n{sender_name}",

        "**To my wonderful {recipient_name},💕**\n\n"
        "**Every day with you feels like Valentine's Day. {personalized_content}**\n\n"
        "**Our love story is my favorite story, and I'm blessed to write new chapters with you every day. 📖**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**All my love,**\n{sender_name}"
    ],
    
    'girlfriend': [
        "**Dear {recipient_name},💖**\n\n"
        "**You bring so much joy and beauty to my life. {personalized_content}**\n\n"
        "**Every moment with you is precious, and I'm so grateful to have you in my life. 💎**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**With all my heart,**\n{sender_name}",

        "**My dearest {recipient_name},💕**\n\n"
        "**{personalized_content}**\n\n"
        "**You make my heart skip a beat every time I see you. ❤️**"
        "**Thank you for being the amazing person you are.**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**Love always,**\n{sender_name}"
    ],
    
    'boyfriend': [
        "**Dear {recipient_name},💖**\n\n"
        "**You make every day brighter just by being in it. {personalized_content}**\n\n"
        "**I feel so lucky to have you in my life, and I cherish every moment we share. 🌟**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**With love,**\n{sender_name}",

        "**To my amazing {recipient_name},💕**\n\n"
        "**{personalized_content}**\n\n"
        "**You're everything I could have ever wished for and more. 🌠**"
        "**Thank you for being you.**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**All my love,**\n{sender_name}"
    ],
    
    'crush': [
        "**Dear {recipient_name},💖**\n\n"
        "**I've wanted to tell you how special you are to me. {personalized_content}**\n\n"
        "**You bring sunshine to my days just by being you. ☀️**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**Happy Valentine's Day,**\n{sender_name}",

        "**Hi {recipient_name},👋**\n\n"
        "**{personalized_content}**\n\n"
        "**I hope this message brings a smile to your face, **"
        "**just like you always bring to mine. 😊**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**Warmly,**\n{sender_name}"
    ],
    
    'friend': [
        "**Dear {recipient_name},🤗**\n\n"
        "**Friendship like yours is one of life's greatest gifts. {personalized_content}**\n\n"
        "**Thank you for being such an amazing friend. 💛**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**With appreciation,**\n{sender_name}",

        "**To my dear friend {recipient_name},👫**\n\n"
        "**{personalized_content}**\n\n"
        "**Your friendship means the world to me, and I'm grateful to have you in my life. 🌍**\n\n"
        "**HAPPY VALENTINE'S DAY! 💕**\n\n"
        "**Best wishes,**\n{sender_name}"
    ]
}
    def _generate_personalized_content(self, description, relationship):
        """
        Use Grok API to generate personalized content based on the description
        """
        prompt = f"""Based on this description of what someone loves about their {relationship}:
        "{description}"
        
        Generate 2-3 heartfelt sentences that incorporate these specific details in a romantic and personal way.
        The content should flow naturally within a Valentine's message.
        Don't use generic phrases - focus on the specific details provided.
        """

        try:
            response = requests.post(
                "https://api.grok.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-1",
                    "messages": [
                        {"role": "system", "content": "You are a romantic content writer focusing on personal details."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                }
            )
            
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            print(f"Error generating personalized content: {e}")
            # Fallback to using the description directly
            return f"I love how {description.lower()}"

    def generate_message(self, sender_name, recipient_name, relationship, description):
        """
        Generate a complete Valentine's message using templates and personalized content
        """
        import random

        # Get templates for the relationship type, fallback to friend if not found
        templates = self.templates.get(relationship, self.templates['friend'])
        
        # Select random template
        template = random.choice(templates)
        
        # Generate personalized content using Grok
        personalized_content = self._generate_personalized_content(description, relationship)
        
        # Fill in the template
        message = template.format(
            sender_name=sender_name,
            recipient_name=recipient_name,
            personalized_content=personalized_content
        )
        
        return message
