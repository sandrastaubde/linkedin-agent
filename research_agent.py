"""
Research Agent - Smartphone Version
"""

import json
from agents.base_agent import BaseAgent
from datetime import datetime

class ResearchAgent(BaseAgent):
    def __init__(self, memory):
        role_card = {
            'name': 'Research Agent',
            'department': 'Marketing',
            'responsibility': 'Gather trends and insights for LinkedIn',
            'voice_rules': 'Analytical and concise',
            'governance': {
                'autonomous_decisions': ['Identify trends', 'Generate reports'],
                'requires_approval': ['Change methodology'],
                'never_allowed': ['Publish content']
            }
        }
        
        super().__init__(role_card, memory)
        self.skills = ['trend_analysis', 'content_angles', 'brand_voice_analysis']
    
    def gather_insights(self):
        """Sammelt Trends"""
        context = self.load_context()
        profile = context.get('profile', {})
        
        topics = [
            profile.get('topic_1', 'AI & Business'),
            profile.get('topic_2', 'Social Media'),
            profile.get('topic_3', 'Growth')
        ]
        
        prompt = f"""Analysiere aktuelle Trends für LinkedIn Content.

HAUPTTHEMEN: {', '.join(topics)}
ZIELGRUPPE: {profile.get('target_audience', 'Professionals')}

Erstelle einen Research Report als JSON:
{{
    "trending_topics": [
        {{"topic": "...", "theme": "tema_1/2/3", "why_trending": "...", "interest": "high/medium"}}
    ],
    "content_angles": [
        {{"angle": "...", "format": "story/how-to/opinion", "engagement": "high/medium"}}
    ],
    "hooks": [{{"hook": "...", "theme": "..."}}],
    "tips": [{{"tip": "...", "actionability": "immediate"}}]
}}
"""
        
        response = self.call_claude(prompt, max_tokens=3000)
        
        if not response:
            return self._fallback_insights(topics)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            
            insights = json.loads(response)
            
            # Speichere in Memory
            self.memory.save_json('analytics', 'research_latest.json', {
                'insights': insights,
                'generated_at': str(datetime.now()),
                'topics': topics
            })
            
            print(f"✅ Research: {len(insights.get('trending_topics', []))} Trends")
            return insights
            
        except Exception as e:
            print(f"❌ Parse Error: {str(e)}")
            return self._fallback_insights(topics)
    
    def _fallback_insights(self, topics):
        """Fallback"""
        return {
            "trending_topics": [
                {"topic": f"{topics[0]} in Business", "theme": "tema_1", 
                 "why_trending": "High adoption", "interest": "high"}
            ],
            "content_angles": [
                {"angle": f"How {topics[0]} changes work", "format": "how-to", "engagement": "high"}
            ],
            "hooks": [{"hook": f"Most are using {topics[0]} wrong", "theme": topics[0]}],
            "tips": [{"tip": f"Start with one {topics[0]} tool", "actionability": "immediate"}]
        }
    
    def analyze_brand_voice(self, samples):
        """Analysiert Schreibstil"""
        prompt = f"""Analysiere diese LinkedIn Posts:

{chr(10).join([f"{i+1}. {s[:200]}..." for i, s in enumerate(samples[:5])])}

OUTPUT als JSON:
{{
    "tone": "...",
    "writing_style": "...",
    "key_themes": ["..."],
    "typical_phrases": ["..."],
    "unique_voice": "...",
    "rules_for_content_gen": ["..."]
}}
"""
        
        response = self.call_claude(prompt, max_tokens=1500)
        
        if not response:
            return {"tone": "professional", "writing_style": "clear"}
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            return json.loads(response)
        except:
            return {"tone": "professional", "writing_style": "clear"}
