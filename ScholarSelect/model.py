import subprocess
import json

def get_college_recommendation(user_input, college_data):
    # Create readable chunks for the model
    formatted_data = ""
    for college in college_data:
        formatted_data += (
            f"institution: {college['institution']}, "
            f"location: {college['location']}, "
            f"ar score: {college['ar score']}, "
            f"fsr score: {college['fsr score']}, "
            f"overall score: {college['score scaled']}\n"
        )

    # Prompt to Ollama
    prompt = f"""
You are an expert college guidance counselor.

Here is the student profile:
{user_input}

Below is a list of colleges with relevant metrics:
{formatted_data}

Based on this, recommend 3 colleges that best match the student's interests and academic potential. Explain your recommendation briefly.

Output JSON like:
[
  {{"college": "XYZ", "location": "ABC", "reason": "Short reason"}},
  ...
]
"""

    result = subprocess.run(
        ["ollama", "run", "gemma3:12b", prompt],
        capture_output=True,
        text=True
    )

    response = result.stdout.strip()

    try:
        start = response.find('[')
        end = response.rfind(']') + 1
        json_part = response[start:end]
        return json.loads(json_part)
    except Exception as e:
        return [{"error": "Invalid output", "details": str(e)}]
