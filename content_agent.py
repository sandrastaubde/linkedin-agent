"""
Content Agent - Generiert LinkedIn Posts
"""

import json
from agents.base_agent import BaseAgent
from datetime import datetime
import random

class ContentAgent(BaseAgent):
    def __init__(self, memory):
        role_card = {
            'name': 'Content Agent',
            'department': 'Marketing',
            'responsibility': 'Generate LinkedIn posts in brand voice',
            'voice_rules': 'Match user brand voice exactly',
            'governance': {
                'autonomous_decisions': ['Generate post drafts'],
                'requires_approval': ['All posts before publishing'],
                'never_allowed': ['Publish without approval', 'Off-brand content']
            }
        }
        
        super().__init__(role_card, memory)
        self.skills = ['post_generation', 'linkedin_optimization']
    
    def generate_proposals(self, research_data, count=5):
        """Generiert mehrere Post-Vorschläge"""
        
        context = self.load_context()
        profile = context.get('profile', {})
        brand_voice = context.get('brand_voice', {})
        
        topics = [
            profile.get('topic_1', ''),
            profile.get('topic_2', ''),
            profile.get('topic_3', '')
        ]
        
        # Nutze Research Insights
        angles = research_data.get('content_angles', [])[:count]
        hooks = research_data.get('hooks', [])
        
        proposals = []
        
        for i, angle in enumerate(angles):
            hook = hooks[i] if i < len(hooks) else {"hook": "Interesting insight..."}
            
            proposal = self._generate_single_post(
                angle=angle,
                hook=hook,
                topics=topics,
                profile=profile,
                brand_voice=brand_voice
            )
            
            if proposal:
                proposal['id'] = f"post_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                proposal['status'] = 'pending'
                
                # Speichere in Memory
                self.memory.save_proposal(proposal)
                proposals.append(proposal)
        
        return proposals
    
    def _generate_single_post(self, angle, hook, topics, profile, brand_voice):
        """Generiert einen einzelnen Post"""
        
        prompt = f"""Erstelle einen LinkedIn Post.

PROFIL:
- Name: {profile.get('name', 'User')}
- Rolle: {profile.get('role', '')}
- Zielgruppe: {profile.get('target_audience', '')}
- Positionierung: {profile.get('positioning', '')}

HAUPTTHEMEN: {', '.join(topics)}

BRAND VOICE:
- Tonalität: {brand_voice.get('tone', 'professional')}
- Stil: {brand_voice.get('writing_style', 'clear')}
- Unique Voice: {brand_voice.get('unique_voice', '')}

CONTENT ANGLE: {angle.get('angle', '')}
FORMAT: {angle.get('format', 'opinion')}
HOOK: {hook.get('hook', '')}

ANFORDERUNGEN:
- Länge: 150-200 Wörter (MAX 3000 Zeichen - LinkedIn Limit!)
- Hook in ersten 1-2 Zeilen
- Konkreter Mehrwert
- LinkedIn-optimiert (Absätze, klar strukturiert)
- Passt zu einem der 3 Hauptthemen
- In der Brand Voice

OUTPUT als JSON:
{{
    "post_text": "Der Post (MAX 3000 Zeichen!)",
    "hook_line": "Erste Zeile",
    "hashtags": ["#Tag1", "#Tag2", "#Tag3"],
    "topic": "tema_1/2/3",
    "format": "{angle.get('format', 'opinion')}",
    "posting_time": "09:00",
    "estimated_engagement_score": 7,
    "reasoning": "Warum dieser Post funktioniert",
    "character_count": 0
}}
"""
        
        response = self.call_claude(prompt, max_tokens=2500)
        
        if not response:
            return None
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            
            post = json.loads(response)
            
            # Validiere LinkedIn Limit
            char_count = len(post.get('post_text', ''))
            if char_count > 3000:
                post['post_text'] = post['post_text'][:2950] + '...'
                post['character_count'] = 2953
            else:
                post['character_count'] = char_count
            
            post['generated_at'] = str(datetime.now())
            
            return post
            
        except Exception as e:
            print(f"❌ Content Gen Error: {str(e)}")
            return None
