# main.py
from flask import Flask, render_template, request, jsonify
import subprocess
import json
import sys
import os

app = Flask(__name__)

def run_ollama_model(prompt):
    """Run the Ollama model with the given prompt"""
    try:
        # Run the Ollama model using subprocess
        result = subprocess.run(
            ["ollama", "run", "kimi-k2:1t-cloud"],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            timeout=120  # 2 minutes timeout
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama: {e}")
        return None
    except subprocess.TimeoutExpired:
        print("Ollama request timed out")
        return None
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def generate_prompt(preferences):
    """Generate a prompt for the Ollama model based on user preferences"""
    # Handle missing fields with default values
    college_preference = preferences.get('collegePreference', 'indian')
    math = preferences.get('math', '3')
    science = preferences.get('science', '3')
    literature = preferences.get('literature', '3')
    social = preferences.get('social', '3')
    art = preferences.get('art', '3')
    tech = preferences.get('tech', '3')
    business = preferences.get('business', '3')
    hands_on = preferences.get('handsOn', '3')
    career_focus = preferences.get('careerFocus', 'General')
    location = preferences.get('location', 'Any')
    college_type = preferences.get('collegeType', 'University')
    
    prompt = f"""
    Based on the following student preferences, recommend suitable college streams and institutions:
    
    Preferences:
    - College Preference: {college_preference.capitalize()} Colleges
    - Mathematics: {math}/5
    - Science: {science}/5
    - Literature: {literature}/5
    - Social Sciences: {social}/5
    - Arts/Creative: {art}/5
    - Technology: {tech}/5
    - Business: {business}/5
    - Hands-on Work: {hands_on}/5
    - Career Focus: {career_focus}
    - Location Preference: {location}
    - College Type: {college_type}
    
    Please provide recommendations in the following JSON format:
    {{
        "streams": ["Stream 1", "Stream 2", "Stream 3"],
        "colleges": ["College Type 1", "College Type 2"],
        "careers": ["Career Path 1", "Career Path 2", "Career Path 3"],
        "institutions": ["Institution 1", "Institution 2", "Institution 3"]
    }}
    
    Ensure the response is valid JSON and nothing else.
    """
    return prompt

def parse_ollama_response(response):
    """Parse the Ollama response and extract JSON"""
    if not response:
        return None
    
    try:
        # Try to parse the entire response as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # If that fails, try to find JSON in the response
        try:
            # Look for JSON between curly braces
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # If all parsing fails, return None
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get preferences from request
        preferences = request.get_json()
        
        # Validate required fields
        if not preferences:
            return jsonify({'error': 'Invalid request data'}), 400
        
        # Generate prompt for Ollama
        prompt = generate_prompt(preferences)
        
        # Run Ollama model
        response = run_ollama_model(prompt)
        
        if not response:
            return jsonify({'error': 'Failed to get recommendations from Ollama'}), 500
        
        # Parse response
        recommendations = parse_ollama_response(response)
        
        if not recommendations:
            return jsonify({'error': 'Failed to parse recommendations from Ollama'}), 500
        
        # Ensure all required keys are present
        required_keys = ['streams', 'colleges', 'careers', 'institutions']
        for key in required_keys:
            if key not in recommendations:
                recommendations[key] = []
        
        return jsonify(recommendations)
    
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Check if index.html exists in current directory
    if os.path.exists('index.html'):
        # Copy index.html to templates directory
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Remove the original index.html file
        os.remove('index.html')
    else:
        # Create a basic template if index.html doesn't exist
        basic_html = """
<!DOCTYPE html>
<html>
<head>
    <title>College Recommendation System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #4361ee; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #4361ee; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
        button:hover { background: #3a56e4; }
        .results { margin-top: 30px; padding: 20px; background: #e8f4ff; border-radius: 5px; }
        .error { color: red; margin: 20px 0; padding: 15px; background: #ffe8e8; border-radius: 5px; }
        .loading { text-align: center; display: none; }
        .college-options { display: flex; gap: 20px; margin-bottom: 20px; }
        .college-option { flex: 1; text-align: center; padding: 15px; border: 2px solid #ddd; border-radius: 5px; cursor: pointer; }
        .college-option.active { border-color: #4361ee; background: #e8f0ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>College Recommendation System</h1>
        <form id="preferenceForm">
            <div class="form-group">
                <label>College Preference</label>
                <div class="college-options">
                    <div class="college-option" data-type="indian">
                        <h3>Indian Colleges</h3>
                        <p>IITs, NITs, State Universities</p>
                    </div>
                    <div class="college-option" data-type="foreign">
                        <h3>Foreign Colleges</h3>
                        <p>Universities Abroad</p>
                    </div>
                </div>
                <input type="hidden" id="collegePreference" name="collegePreference" required>
            </div>
            
            <div class="form-group">
                <label for="math">Mathematics (1-5)</label>
                <input type="number" id="math" name="math" min="1" max="5" value="3" required>
            </div>
            
            <div class="form-group">
                <label for="science">Science (1-5)</label>
                <input type="number" id="science" name="science" min="1" max="5" value="3" required>
            </div>
            
            <div class="form-group">
                <label for="literature">Literature (1-5)</label>
                <input type="number" id="literature" name="literature" min="1" max="5" value="3" required>
            </div>
            
            <div class="form-group">
                <label for="careerFocus">Career Focus</label>
                <input type="text" id="careerFocus" name="careerFocus" placeholder="e.g., Engineering, Medicine" required>
            </div>
            
            <div class="form-group">
                <label for="location">Location Preference</label>
                <input type="text" id="location" name="location" placeholder="e.g., Urban, Rural">
            </div>
            
            <div class="form-group">
                <label for="collegeType">College Type</label>
                <select id="collegeType" name="collegeType">
                    <option value="">Select College Type</option>
                    <option value="University">University</option>
                    <option value="Liberal Arts">Liberal Arts College</option>
                    <option value="Technical">Technical College</option>
                    <option value="Specialized">Specialized Institution</option>
                </select>
            </div>
            
            <button type="submit">Get Recommendations</button>
        </form>
        
        <div class="loading" id="loading">
            <p>Processing your preferences...</p>
        </div>
        
        <div class="error" id="error" style="display: none;"></div>
        
        <div class="results" id="results" style="display: none;">
            <h2>Recommendations</h2>
            <div id="recommendationsContent"></div>
        </div>
    </div>

    <script>
        // College preference selection
        document.querySelectorAll('.college-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.college-option').forEach(opt => opt.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('collegePreference').value = this.dataset.type;
            });
        });
        
        // Form submission
        document.getElementById('preferenceForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate college preference
            if (!document.getElementById('collegePreference').value) {
                showError('Please select your college preference');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            
            // Collect form data
            const formData = new FormData(this);
            const preferences = {};
            for (let [key, value] of formData.entries()) {
                preferences[key] = value;
            }
            
            // Send to backend
            fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(preferences)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                
                if (data.error) {
                    showError(data.error);
                    return;
                }
                
                // Display recommendations
                displayRecommendations(data);
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                showError('Error: ' + error.message);
            });
        });
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        function displayRecommendations(data) {
            const content = document.getElementById('recommendationsContent');
            content.innerHTML = `
                <h3>Academic Streams</h3>
                <ul>${data.streams.map(s => `<li>${s}</li>`).join('')}</ul>
                
                <h3>College Types</h3>
                <ul>${data.colleges.map(c => `<li>${c}</li>`).join('')}</ul>
                
                <h3>Career Paths</h3>
                <ul>${data.careers.map(c => `<li>${c}</li>`).join('')}</ul>
                
                <h3>Recommended Institutions</h3>
                <ul>${data.institutions.map(i => `<li>${i}</li>`).join('')}</ul>
            `;
            document.getElementById('results').style.display = 'block';
        }
    </script>
</body>
</html>
        """
        with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write(basic_html)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
