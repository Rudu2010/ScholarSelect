from flask import Flask, render_template, request
import pandas as pd
from model import get_college_recommendation

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':
        user_input = request.form['profile']
    
        # Read and parse your updated CSV format
        df = pd.read_csv('data/colleges_cleaned.csv')

        # Clean and limit to top 20 for prompt context
        selected_cols = [
            'institution', 'location', 'ar score', 'ar score',
            'fsr score', 'score scaled'
        ]
        df = df[selected_cols].dropna()
        sample_data = df.head(20).to_dict(orient='records')

        recommendations = get_college_recommendation(user_input, sample_data)
        df.columns = df.columns.str.replace(r'\ufeff', '', regex=True).str.strip()


    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
