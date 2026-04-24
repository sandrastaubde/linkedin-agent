"""
Base Agent - Simplified für Smartphone
6-Komponenten Framework, aber mit Simple Memory statt Google Drive
"""

import os
from anthropic import Anthropic
from datetime import datetime

class BaseAgent:
    """Basis für alle Agents - Smartphone-freundlich"""
    
    def __init__(self, role_card, memory):
        # COMPONENT 1: Role Card
        self.role_card = role_card
        self.name = role_card.get('name', 'Agent')
        self.department = role_card.get('department', 'General')
        
        # COMPONENT 2: Skills (werden von Sub-Klassen definiert)
        self.skills = []
        
        # COMPONENT 3: Memory (Simple File-based)
        self.memory = memory
        
        # COMPONENT 4: Connections
        self.connections = {}
        
        # COMPONENT 5: System Prompt
        self.system_prompt = self._build_system_prompt()
        
        # COMPONENT 6: Governance Rules
        self.governance = role_card.get('governance', {
            'autonomous_decisions': [],
            'requires_approval': [],
            'never_allowed': []
        })
        
        # Claude API
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
    
    def _build_system_prompt(self):
        """Baut System Prompt aus Role Card"""
        
        prompt = f"""You are {self.role_card.get('name')}.

DEPARTMENT: {self.role_card.get('department')}

CORE RESPONSIBILITY:
{self.role_card.get('responsibility')}

VOICE & TONE RULES:
{self.role_card.get('voice_rules', 'Professional and clear')}

GOVERNANCE:
- You can decide autonomously: {', '.join(self.governance.get('autonomous_decisions', []))}
- Requires approval: {', '.join(self.governance.get('requires_approval', []))}
- Never allowed: {', '.join(self.governance.get('never_allowed', []))}

You have persistent memory stored in JSON files.
"""
        return prompt
    
    def load_context(self):
        """Lädt relevanten Kontext aus Memory"""
        return {
            'profile': self.memory.load_profile(),
            'brand_voice': self.memory.load_brand_voice(),
            'preferences': self.memory.load_preferences()
        }
    
    def call_claude(self, user_prompt, max_tokens=2000):
        """Claude API Call"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"❌ Claude API Error: {str(e)}")
            return None
    
    def connect_to(self, agent_name, agent_instance):
        """Verbindet mit anderem Agent"""
        self.connections[agent_name] = agent_instance
    
    def hand_off_to(self, agent_name, task_data):
        """Übergibt Task an anderen Agent"""
        if agent_name in self.connections:
            return self.connections[agent_name].receive_task(self.name, task_data)
        return None
    
    def receive_task(self, from_agent, task_data):
        """Empfängt Task"""
        return {'status': 'received', 'data': task_data}
