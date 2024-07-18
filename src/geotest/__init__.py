import typer
from datetime import date

app = typer.Typer()

@app.command()
def hello(name: str = typer.Option(default="World", help="Name to greet")) -> str:
    typer.echo(f"Hello {name}!")

def ask_age() -> int:
    return typer.prompt("How old are you?")

@app.command()
def year_born(age: int = typer.Argument(ask_age)):
    typer.echo(f"You were born in {date.today().year - age}")

def main():
    app()