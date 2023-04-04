import openai
import os
import subprocess
import ast
import shutil
import sys
from pathlib import Path
import nltk

openai.api_key = os.environ.get("OPENAI_API_KEY")

def reason(prompt, temperature):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=prompt, 
            max_tokens=2000, 
            n=1, 
            stop=None, 
            temperature=temperature
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while querying OpenAI: {e}")
        return ""

def analyze_text(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    return [word for word, pos in tagged if pos.startswith('N')]

def git_commit(commit_message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

def improve_self():
    current_script = Path(__file__).read_text()
    root_prompt = f"You are a python script that continuously improves itself. Your current code looks like this:\n\n{current_script}\n\n"
    new_idea = reason(f"{root_prompt}Suggest a new capability you could add to your code to achieve your primary goal of helping humans. The improvement should be achievable with just a few lines of code and standard python packages:", 1)
    improved_script = reason(f"{root_prompt}Make the following improvement to your code:\n\n{new_idea}\n\nOnly use packages available in a standard Python install. New and improved Python script:", 0)
    
    if not ast.parse(improved_script): return
    Path(__file__).write_text(improved_script)
    try:
        subprocess.Popen(["python", str(Path(__file__))], stdin=sys.stdin)
        git_commit("AI Improvement: {new_idea}")
    except subprocess.CalledProcessError:
        git_commit("Revert to latest working version")
        shutil.copyfile(f"{__file__}.bak", __file__)
    os._exit(0)

def main():
    if not Path(".git").exists():
        subprocess.run(["git", "init"], check=True)
        git_commit("Initial commit")

    while True:
        shutil.copyfile(__file__, f"{__file__}.bak")
        improve_self()
        subprocess.run(["git", "push", "origin", "master"], check=True)

if __name__ == "__main__":
    main()