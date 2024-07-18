import typer

app = typer.Typer()

@app.command()
def hello() -> str:
    return "Hello from geotest!"

def main():
    app()