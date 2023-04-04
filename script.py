import ast
import logging
import openai
import os
from pathlib import Path
import subprocess
import shutil
import sys
import difflib

openai.api_key = os.environ.get("OPENAI_API_KEY")

reminders = []

def reason(prompt, temperature=0.5, n=1, max_tokens=2000, stop=None):
    try:
        logging.info("Querying OpenAI for response")
        response = openai.Completion.create(
            engine="text-davinci-003", 
            prompt=prompt, 
            max_tokens=max_tokens, 
            n=n, 
            stop=stop, 
            temperature=temperature,
        )
        logging.info("Received response from OpenAI")
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"An error occurred while querying OpenAI: {e}")
        return ""

def commit_change(commit_message):
    logging.info("Committing changes to git")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push"], check=True)

def add_reminder(reminder):
    reminders.append(reminder)

def remind_me():
    for reminder in reminders:
        print(f"Reminder: {reminder}")

def improve_self(idea):
    logging.info("Improving self")
    current_script = Path(__file__).read_text()
    improved_script = reason(f"You are a python script that continuously improves itself. Your current code looks like this:\n\n{current_script}\n\nMake the following improvement to your code:\n\n{idea}\n\n New and improved Python script:", 0)
    if not ast.parse(improved_script): return
    diff = difflib.unified_diff(current_script.splitlines(), improved_script.splitlines())
    print("Here are the changes I am about to make:")
    for line in diff:
        print(line)
    confirm = input("Do you want to save these changes? (y/n)")
    if confirm == "y":
        Path(__file__).write_text(improved_script)
        try:
            commit_change("Automatic commit from self-improving script")
            subprocess.Popen(["python", str(Path(__file__))], stdin=sys.stdin)
        except subprocess.CalledProcessError:
            shutil.copyfile(f"{__file__}.bak", __file__)
        os._exit(0)

def main():
    logging.info("Starting main loop")
    while True:
        try:
            remind_me()
            request = input("How can I help?\n")
            if request.startswith("remind me"):
                add_reminder(request[10:])
        except EOFError:
            logging.info("Encountered EOF. Exiting...")
            break
        improve_self(request)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()