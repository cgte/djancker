import time
import json

from bottle import route, run, template, response, get, post, request, Bottle

app = Bottle()


@app.get("/text")
def text_form():
    return """
            Votre code:
        <form action="/text" method="post">
            <textarea name="code" rows="50" cols="100">
def mafonction(n):
    #votre code ici
    return None
            </textarea>
            <input value="Ajouter" type="submit" />
        </form>
        """


from importlib import import_module
from itertools import count

template_name = "tcode_%s"
counter = count()

dockerfile_template = """
FROM python:3.7-alpine
RUN python3 -m pip install bottle
COPY . /app
WORKDIR /app


#RUN service nginx start
EXPOSE {port}
CMD ["python","applauncher.py", "{port}"]

"""


@app.post("/text")  # or @route('/login', method='POST')
def process_text():
    code = request.forms.get("code") or request.json.get("kind")
    number = next(counter)
    port = number
    dirname = f"{template_name}" % number
    import shutil

    os.mkdir(dirname)

    shutil.copyfile("applauncher.py", f"{dirname}/applauncher.py")
    os.chdir(dirname)
    # module_name = f"{template_name}" % number
    with open(f"app.py", "w") as f:
        f.write(code)
    port = str(8000 + number)
    with open(f"Dockerfile", "w") as f:
        f.write(dockerfile_template.format(**{"port": port}))
    import subprocess
    import shlex

    for x in str(
        subprocess.check_output(shlex.split(f"docker build -t demo_{number} .")).decode(
            "utf-8"
        )
    ).split("\n"):
        yield "%s<br/>" % x

    subprocess.call(shlex.split(f"docker run -p {port}:{port} -d demo_{number}"))


if __name__ == "__main__":
    import os

    os.system("rm -r tcode_*")
    app.run(host="localhost", port=8080, debug=True)
