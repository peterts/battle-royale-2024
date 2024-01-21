from dotenv import load_dotenv
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from http.server import BaseHTTPRequestHandler, HTTPServer
import random
import string

import json
from openai import AzureOpenAI
from functools import lru_cache
import requests
import html2text

hostName = "localhost"
serverPort = 8080


load_dotenv()

CHATGPT_CLIENT = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://bildegeneratorf1.openai.azure.com/",
    api_key=os.environ["CHATGPT_API_KEY"],
)

DALLE_CLIENT = AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint="https://oai-test-swedencentral3.openai.azure.com/",
    api_key=os.environ["DALLE_API_KEY"],
)

HTML = None
RESULTS_DIR = Path(__file__).parents[1] / "results"


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(HTML, "utf-8"))


def render_template(template_path, context) -> str:
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template_path)
    output = template.render(context)
    return output


def add_images_to_cartoon_json(results: dict) -> dict:
    for item in results["Bilder"]:
        image_description = item.pop("Bildebeskrivelse")
        item["Bildelenke"] = generate_image_url(image_description)
    return results


def generate_cartoon_content_from_news_article_as_json(news_article_text: str):
    cartoon_json_str = generate_cartoon_content_from_news_article(news_article_text)
    print("Converting cartoon json-str to json")
    return json.loads(cartoon_json_str)


def generate_cartoon_content_from_news_article(news_article_text: str) -> str:
    print("Generating cartoon json-str")
    response = CHATGPT_CLIENT.chat.completions.create(
        model="Artikkelparser",
        messages=[{"role": "user", "content": news_article_text}],
    )
    return response.choices[0].message.content


def generate_image_url(image_description: str) -> str:
    print("Generating image")
    response = DALLE_CLIENT.images.generate(
        model="Dalle3", prompt=image_description, n=1
    )
    return response.data[0].url


@lru_cache()
def get_run_id():
    return generate_random_string(10)


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def fetch_news_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = True
        return text_maker.handle(response.text)
    except requests.RequestException as e:
        return f"Error: An exception occurred while fetching the webpage: {e}"


def create_prompt_including_news_article():
    prompt = Path("./prompt.txt").read_text()
    news_article_text = fetch_news_content(input("Url: "))
    return prompt + news_article_text.rstrip() + "\n\n===\n\nOutput:"


def run():
    global HTML

    run_id = get_run_id()

    print(f"Run {run_id} started")

    results_text_only_json_path = RESULTS_DIR / f"result-mid-{run_id}.json"
    results_with_images_json_path = RESULTS_DIR / f"result-{run_id}.json"
    results_html_file_path = RESULTS_DIR / f"result-{run_id}.html"

    if results_with_images_json_path.is_file():
        results_with_images = json.loads(results_with_images_json_path.read_text())
    else:
        prompt = create_prompt_including_news_article()

        results_text_only = generate_cartoon_content_from_news_article_as_json(prompt)
        results_text_only_json_path.write_text(json.dumps(results_text_only, indent=4))

        results_with_images = add_images_to_cartoon_json(results_text_only)
        results_with_images_json_path.write_text(
            json.dumps(results_with_images, indent=4)
        )

    HTML = render_template("cartoon.html.j2", results_with_images)
    Path(results_html_file_path).write_text(HTML)

    web_server = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    run()
