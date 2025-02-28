from fastapi import FastAPI
from typing import Union, Annotated
from fastapi import Request
from fastapi import Depends
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi import Form

from markata.hookspec import hook_impl
import typer
import uvicorn
import markata

MARKATA = markata.Markata()


def set_markata(request: Request) -> None:
    request.markata = MARKATA


app = FastAPI(dependencies=[Depends(set_markata)])


@app.get("/{slug}")
def read_root(request: Request, slug: str):
    if slug == "":
        index = request.markata.config["output_dir"] / "index.html"
        return HTMLResponse(index.read_text())
    if slug.endswith(".css"):
        css = request.markata.config["output_dir"] / slug
        return FileResponse(css)

    posts = request.markata.map("post", filter=f"slug=='{slug}'")
    if len(posts) == 0:
        return HTMLResponse("<h1>Not found</h1>")
    if len(posts) > 1:
        return HTMLResponse("<h1>Multiple matches</h1>")
    post = posts[0]
    html = post.html
    return HTMLResponse(html)


@app.get("/edit/{slug}")
def read_item(request: Request, slug: str):
    posts = request.markata.map("post", filter=f"slug=='{slug}'")
    if len(posts) == 0:
        return HTMLResponse("<h1>Not found</h1>")
    if len(posts) > 1:
        return HTMLResponse("<h1>Multiple matches</h1>")
    post = posts[0]
    md = post.path.read_text()
    template = request.markata.config["output_dir"] / "edit.html"
    html = template.read_text().replace("{{ content }}", md).replace("{{ slug }}", slug)

    return HTMLResponse(html)


@app.patch("/edit/{slug}")
def patch_post(request: Request, slug: str, content: Annotated[str, Form()]):
    return content


@hook_impl()
def cli(app: typer.Typer, markata: markata.Markata) -> None:
    """
    Markata hook to implement base cli commands.
    """

    server_app = typer.Typer()
    app.add_typer(server_app)

    @server_app.callback()
    def server():
        ...

    @server_app.command()
    def start():
        markata.app = app
        uvicorn.run(app, host="0.0.0.0", port=8000)

    # app: str = "fokais.api.api:app"
    # port: int = 5000
    # reload: bool = True
    # log_level: str = "info"
    # host: str = "0.0.0.0"
    # workers: int = 1
    # forwarded_allow_ips: str = "*"
    # proxy_headers: bool = True
    config = {
        "app": "plugins.server:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info",
        "workers": 1,
        "forwarded_allow_ips": "*",
        "proxy_headers": True,
    }
    uvicorn.run(**config)
