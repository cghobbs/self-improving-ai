import ast
import openai
import os
from pathlib import Path
import subprocess
import shutil
import sys

openai.api_key = os.environ.get("OPENAI_API_KEY")

def reason(prompt, temperature=0.5, n=1, max_tokens=2000, stop=None):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=prompt, 
            max_tokens=max_tokens, 
            n=n, 
            stop=stop, 
            temperature=temperature,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while querying OpenAI: {e}")
        return ""

def improve_self(idea):
    current_script = Path(__file__).read_text()
    improved_script = reason(f"You are a python script that continuously improves itself. Your current code looks like this:\n\n{current_script}\n\nMake the following improvement to your code:\n\n{idea}\n\n New and improved Python script:", 0)
    if not ast.parse(improved_script): return
    Path(__file__).write_text(improved_script)
    try:
        subprocess.Popen(["python", str(Path(__file__))], stdin=sys.stdin)
    except subprocess.CalledProcessError:
        shutil.copyfile(f"{__file__}.bak", __file__)
    os._exit(0)

def main():
    while True:
        try:
            request = input("How can I improve?\n")
        except EOFError:
            print("Encountered EOF. Exiting...")
            break
        improve_self(request)

if __name__ == "__main__":
    main()

