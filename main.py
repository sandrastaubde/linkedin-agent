"""
LinkedIn Agent - Smartphone Edition
Kein Google Drive nötig - läuft komplett standalone
"""

import os
from flask import Flask, render_template, request, jsonify, redirect
from memory.simple_memory import SimpleMemory
from agents.research_agent import ResearchAgent
from agents.content_agent import ContentAgent

app = Flask(__name__)

# Initialize Memory (Simple File-based)
memory = SimpleMemory()

# Initialize Agents
research_agent = ResearchAgent(memory)
content_agent = ContentAgent(memory)

# Connect Agents
research_agent.connect_to('content_agent', content_agent)


@app.route('/')
def dashboard():
    """Main Dashboard"""
    profile = memory.load_profile()
    if not profile:
        return redirect('/onboarding')
    
    proposals = memory.get_pending_proposals()
    stats = memory.get_stats()
    
    return render_template('dashboard.html',
                         proposals=proposals,
                         stats=stats,
                         profile=profile)


@app.route('/onboarding')
def onboarding():
    """Onboarding Wizard"""
    profile = memory.load_profile()
    if profile:
        return redirect('/')
    
    return render_template('onboarding.html')


@app.route('/onboarding/submit', methods=['POST'])
def submit_onboarding():
    """Process Onboarding"""
    try:
        profile_data = {
            'name': request.form.get('name'),
            'role': request.form.get('role'),
            'industry': request.form.get('industry'),
            'target_audience': request.form.get('target_audience'),
            'positioning': request.form.get('positioning'),
            'topic_1': request.form.get('topic_1'),
            'topic_2': request.form.get('topic_2'),
            'topic_3': request.form.get('topic_3')
        }
        
        memory.save_profile(profile_data)
        
        # Writing samples
        writing_samples = request.form.get('writing_samples', '')
        if writing_samples:
            samples = [s.strip() for s in writing_samples.split('\n\n') if s.strip()]
            
            if len(samples) >= 3:
                brand_voice = research_agent.analyze_brand_voice(samples)
                memory.save_brand_voice(brand_voice)
                memory.save_writing_samples(samples)
        
        return jsonify({'success': True, 'redirect': '/'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/generate', methods=['POST'])
def generate_proposals():
    """Generate new content proposals"""
    try:
        # 1. Research
        print("🔍 Research Agent...")
        research_data = research_agent.gather_insights()
        
        # 2. Content Generation
        print("✍️ Content Agent...")
        proposals = content_agent.generate_proposals(research_data, count=5)
        
        print(f"✅ {len(proposals)} Vorschläge erstellt!")
        return jsonify({
            'success': True,
            'count': len(proposals),
            'message': f'{len(proposals)} neue Vorschläge erstellt!'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/approve/<proposal_id>', methods=['POST'])
def approve_proposal(proposal_id):
    """Approve proposal"""
    try:
        memory.update_proposal_status(proposal_id, 'approved')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/reject/<proposal_id>', methods=['POST'])
def reject_proposal(proposal_id):
    """Reject proposal"""
    try:
        reason = request.json.get('reason', '') if request.is_json else ''
        memory.update_proposal_status(proposal_id, 'rejected', reason)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    return jsonify(memory.get_stats())


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 LinkedIn Agent - Smartphone Edition")
    print("="*60)
    print("✅ Simple Memory System (No Google Drive needed)")
    print("✅ Works on Free Replit")
    print("✅ Upgradeable to Google Drive later")
    print("="*60 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
