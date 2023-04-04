import openai
import os
import subprocess
import ast
import shutil
import sys
import json
from pathlib import Path
import time
import multiprocessing

openai.api_key = os.environ.get("OPENAI_API_KEY")

possible_actions = """
reason - Takes a fully formed question or prompt and returns a reasonable response.
improve_self - Takes an idea for improving this script a returns code
"""

def reason(prompt, temperature=0.5):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=prompt, 
            max_tokens=2000, 
            n=1, 
            stop=None, 
            temperature=temperature,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while querying OpenAI: {e}")
        return ""

def process_request(user_request):
    prompt = f"Given the following user request:\n\n{user_request}\n\nDetermine the best action to take. The only possible action includes:\n\n{possible_actions} Which of the above do you choose and what is the query you'll send as an argument? Return a JSON string with the action and the text query string. For example: {{\"action\": \"reason\", \"query\": \"What is the meaning of life?\"}}"
    response_text = reason(prompt, 0)
    
    # Check if the response is a valid JSON string
    try:
        response = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
        return

    function = globals()[response['action']]
    start_time = time.time()
    pool = multiprocessing.Pool()
    result = pool.apply_async(function, (response['query'],))
    pool.close()
    pool.join()
    result = result.get()
    end_time = time.time()
    print(f"Processing time: {end_time - start_time} seconds")
    return result


def commit_change(commit_message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "origin", "master"], check=True)

def improve_self(idea):
    current_script = Path(__file__).read_text()
    improved_script = reason(f"You are a python script that continuously improves itself. Your current code looks like this:\n\n{current_script}\n\nMake the following improvement to your code:\n\n{idea}\n\nOnly use packages available in a standard Python install. New and improved Python script:", 0)
    if not ast.parse(improved_script): return
    Path(__file__).write_text(improved_script)
    try:
        subprocess.Popen(["python", str(Path(__file__))], stdin=sys.stdin)
        commit_change(f"AI: {idea}")
    except subprocess.CalledProcessError:
        commit_change("Revert to latest working version")
        shutil.copyfile(f"{__file__}.bak", __file__)
    os._exit(0)

def main():
    if not Path(".git").exists():
        subprocess.run(["git", "init"], check=True)
        commit_change("Initial commit")

    while True:
        shutil.copyfile(__file__, f"{__file__}.bak")
        start_time = time.time()
        request = input("What can I do for you?\n")
        print(process_request(request))
        end_time = time.time()
        print(f"Total processing time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()