"""
Simple JSON File Memory - Smartphone-freundlich
Keine Google Drive API nötig, alles in lokalen JSON files
Später upgradeabel auf Google Drive
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SimpleMemory:
    """Einfaches File-basiertes Memory System"""
    
    def __init__(self):
        # Erstelle Memory-Ordner
        self.base_path = Path('agent_memory')
        self.base_path.mkdir(exist_ok=True)
        
        # Sub-Ordner
        (self.base_path / 'memory').mkdir(exist_ok=True)
        (self.base_path / 'proposals').mkdir(exist_ok=True)
        (self.base_path / 'analytics').mkdir(exist_ok=True)
        
        print("✅ Simple Memory System initialized")
    
    def _save_json(self, folder, filename, data):
        """Speichert JSON in Datei"""
        path = self.base_path / folder / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_json(self, folder, filename):
        """Lädt JSON aus Datei"""
        path = self.base_path / folder / filename
        if not path.exists():
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # HIGH-LEVEL API
    
    def save_brand_voice(self, brand_voice):
        """Speichert Brand Voice"""
        self._save_json('memory', 'brand_voice.json', brand_voice)
    
    def load_brand_voice(self):
        """Lädt Brand Voice"""
        return self._load_json('memory', 'brand_voice.json')
    
    def save_profile(self, profile):
        """Speichert User Profile"""
        self._save_json('memory', 'profile.json', profile)
    
    def load_profile(self):
        """Lädt User Profile"""
        return self._load_json('memory', 'profile.json')
    
    def save_preferences(self, preferences):
        """Speichert gelernte Präferenzen"""
        self._save_json('memory', 'preferences.json', preferences)
    
    def load_preferences(self):
        """Lädt Präferenzen"""
        prefs = self._load_json('memory', 'preferences.json')
        if not prefs:
            # Default preferences
            prefs = {
                "preferred_formats": [],
                "preferred_topics": [],
                "preferred_tone": "professional",
                "avoid_topics": [],
                "avoid_formats": [],
                "optimal_posting_times": [],
                "learning_confidence": 0
            }
        return prefs
    
    def save_proposal(self, proposal):
        """Speichert einzelnen Proposal"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        proposal_id = proposal.get('id', timestamp)
        filename = f'proposal_{timestamp}_{proposal_id}.json'
        
        self._save_json('proposals', filename, proposal)
        return proposal_id
    
    def load_all_proposals(self):
        """Lädt alle Proposals"""
        proposals_dir = self.base_path / 'proposals'
        proposals = []
        
        if proposals_dir.exists():
            for file in sorted(proposals_dir.glob('proposal_*.json'), reverse=True):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        proposals.append(json.load(f))
                except:
                    pass
        
        return proposals
    
    def get_pending_proposals(self):
        """Holt nur pending Proposals"""
        all_proposals = self.load_all_proposals()
        return [p for p in all_proposals if p.get('status') == 'pending']
    
    def update_proposal_status(self, proposal_id, status, reason=''):
        """Updated Status eines Proposals"""
        proposals_dir = self.base_path / 'proposals'
        
        for file in proposals_dir.glob(f'proposal_*_{proposal_id}.json'):
            with open(file, 'r', encoding='utf-8') as f:
                proposal = json.load(f)
            
            proposal['status'] = status
            proposal['decision_at'] = str(datetime.now())
            if reason:
                proposal['rejection_reason'] = reason
            
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(proposal, f, indent=2, ensure_ascii=False)
            
            return True
        
        return False
    
    def save_writing_samples(self, samples):
        """Speichert Schreibproben"""
        self._save_json('memory', 'writing_samples.json', {
            'samples': samples,
            'saved_at': str(datetime.now())
        })
    
    def load_writing_samples(self):
        """Lädt Schreibproben"""
        data = self._load_json('memory', 'writing_samples.json')
        return data.get('samples', []) if data else []
    
    def save_json(self, folder, filename, data):
        """Public method für direktes Speichern"""
        self._save_json(folder, filename, data)
    
    def load_json(self, folder, filename):
        """Public method für direktes Laden"""
        return self._load_json(folder, filename)
    
    def get_stats(self):
        """Berechnet Statistiken aus Proposals"""
        proposals = self.load_all_proposals()
        
        if not proposals:
            return {
                'total': 0,
                'approved': 0,
                'rejected': 0,
                'pending': 0,
                'approval_rate': 0
            }
        
        approved = len([p for p in proposals if p.get('status') == 'approved'])
        rejected = len([p for p in proposals if p.get('status') == 'rejected'])
        pending = len([p for p in proposals if p.get('status') == 'pending'])
        
        approval_rate = (approved / len(proposals) * 100) if proposals else 0
        
        return {
            'total': len(proposals),
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'approval_rate': round(approval_rate, 1)
        }
