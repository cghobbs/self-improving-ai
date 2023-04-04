import ast
import logging
import openai
import os
from pathlib import Path
import subprocess
import shutil
import sys

openai.api_key = os.environ.get("OPENAI_API_KEY")

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

def improve_self(idea):
    logging.info("Improving self")
    current_script = Path(__file__).read_text()
    improved_script = reason(f"You are a python script that continuously improves itself. Your current code looks like this:\n\n{current_script}\n\nMake the following improvement to your code:\n\n{idea}\n\n New and improved Python script:", 0)
    if not ast.parse(improved_script): return
    print("Here are the changes I am about to make:")
    print(improved_script)
    confirm = input("Do you want to save these changes? (y/n)")
    if confirm == "y":
        Path(__file__).write_text(improved_script)
        try:
            commit_change("Automatic commit from self-improving script")
            subprocess.Popen(["python", str(Path(__file__))], stdin=sys.stdin)
        except subprocess.CalledProcessError:
            shutil.copyfile(f"{__file__}.bak", __file__)
        os._exit(0)

def process_request(request):
    response = reason(f"Given the following request: {request}, which of your existing functions should you use to process the request?", 0)
    if response == "":
        logging.error("No response received from OpenAI")
        return
    logging.info(f"Received response from OpenAI: {response}")
    try:
        eval(response)(request)
    except Exception as e:
        logging.error(f"An error occurred while processing the request: {e}")

def main():
    logging.info("Starting main loop")
    while True:
        try:
            request = input("How can I help?\n")
        except EOFError:
            logging.info("Encountered EOF. Exiting...")
            break
        process_request(request)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()