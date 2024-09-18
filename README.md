# Publishing Packages on PyPI with Rye and GitHub Actions

This space documents my learning around how to develop python packages using Rye and automate publishing on PyPI using GitHub Actions.

## Getting Started

Lets start by creating a new repository using `gh` command line tool
```bash
gh repo create geotest --private --add-readme -d "A test repository for learning how to automate python package development using GitHub Actions"
```

Clone repo and initialise a Rye project
```bash
gh repo clone geovicco-dev/geotest && cd geotest && rye init . && rye pin 3.10 && rye sync
```

Create first commit
```bash
git add . && git commit -m "initial commit" && git push -u origin main
```

Edit `pyproject.toml` to specify the configuration settings used during publishing to PyPI
```toml
# pyproject.toml
[project]
name = "geotest"
version = "0.0.1"
description = "This is a test package for automated package deployment using github actions"
authors = [
{ name = "geovicco-dev", email = "geovicco.dev@gmail.com" }
]
dependencies = []
readme = "README.md"
requires-python = ">= 3.8"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.rye]
managed = true
dev-dependencies = []

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.build.targets.wheel]
packages = ["src/geotest"]
```
## Development

Lets install the Typer package for creating a command line app.
```bash
rye add typer
```

After installation, the `dependencies` section inside `pyproject.toml` will be updated.

Next, create a `__main__.py` inside src/geotest
```shell
touch src/geotest/__main__.py
```

Edit `__main__.py` as below: 
```python
# src/geotest/__main__.py
import geotest
import sys
sys.exit(geotest.main())
```

The entire logic of the CLI application will be written inside `__init__.py` file
```python
# src/geotest/__init__.py
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
```

In order for the app commands to be executable from the command line, we need to edit `pyproject.toml` and specify the function call to the project script.
```toml
[project.scripts]
"geotest" = "geotest:main"
```

Sync project using `rye sync` and try executing the two available commands from the command line using `geotest hello --name user` | `geotest year-born`

Once this is all good and working, we need to commit our changes
```bash
git commit -a -m "added project.scripts in pyproject.toml and updated cli app with new commands"
git push -u origin main
```

Lets finish our development phase by generating docs using the `typer utils` command
```bash
typer geotest utils docs --output README.md --name geotest
```

Finally, commit the changes
```bash
git commit -a -m "updated README" && git push -u origin main
```
## Publishing on PyPI

Once we have a working CLI application, it is ready for the world! We will do this by publishing our package on PyPI which is where all python packages must be registered in order to be pip installable.
### Create GitHub Actions Workflow

Create a `.github/workflows` directory in your repository
```bash
mkdir -p .github/workflows && touch .github/workflows/publish.yaml
```

Edit `publish.yaml`

> At the time of working on this, there was an [issue](https://github.com/astral-sh/rye/issues/1180) with `rye publish` command and it was fixed by adding the `Patch Rye` section in the workflows.

```yaml
# .github/workflows/publish.yaml

name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.x"
      - name: Setup Rye
        uses: eifinger/setup-rye@v3
      - name: Patch Rye
        run: |
          echo "Patching Rye with Twine 5.1.1"
          $RYE_HOME/self/bin/pip install twine==5.1.1
      - name: Install dependencies
        run: rye pin 3.10 && rye sync
      - name: Build package
        run: rye build --clean
      - name: Publish to PyPI
        env:
          PYPI_USERNAME: ${{ secrets.PYPI_USERNAME }}
          PYPI_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: |
          echo $PYPI_PASSWORD
          rye publish --username $PYPI_USERNAME --token $PYPI_PASSWORD --yes --verbose
```

After creating and editing `.github/workflows/publish.yaml`, we need to commit and push these changes to our repository so that GitHub can use this workflow when we create a release.
```bash
# Stage the new workflow file
git add .github/workflows/publish.yaml

# Commit the changes
git commit -m "Add GitHub Actions workflow for PyPI publishing"

# Push the changes to the main branch
git push origin main
```
### Configure GitHub Actions

Change the GitHub Actions settings in your repository to allow read and write operations:

-   Go to your repository on GitHub.
-   Click on `Settings` > `Actions` > `General` > `Workflow permissions`.
-   Change the settings to allow **read and write operations**.
### Create an API Token on PyPI

-   Visit [pypi.org](https://pypi.org) and log in or create an account.
-   Navigate to `Account Settings` > `API Tokens`.
-   Create a new API token. Select `Entire account` as the scope. Copy the token.
### Add GitHub Repository Secrets

Add your PyPI credentials as secrets in your GitHub repository:

-   Go to your repository on GitHub.
-   Click on `Settings` > `Secrets` > `New repository secret`.
-   Add `PYPI_USERNAME` as a secret. Use `__token__` as the value.
-   Add `PYPI_PASSWORD` as a secret. Use the API token created above as the password.
### Create New Release

We have written some code that works and is already up-to-date on the main branch of the remote repository. Next thing we want is to create a release that triggers the GitHub Workflow as defined on the `publish.yaml` above.

Lets create a release using `gh release` command
```bash
gh release create v0.0.1 --generate-notes
```
### Changing Versions and Pushing Changes to PyPI
Assume that you have introduced new features to the CLI application and would like to automatically update the newest release of the package on PyPI. This is where `gh release` and `rye version bump` commands will be used.

Lets increase our model version from 0.0.1 to 0.0.2 - representing a patch upgrade
	**NOTE**: Versions are always represented in {*Major*}.{*Minor*}.*{Patch}* format.
```bash
rye version --bump patch
```

Alternatively, if you know what version to set you can just use **`rye version {version}`** 

Create a new release with the updated version
```bash
gh release create v0.0.2 --generate-notes
```
### Deleting a release

Delete an existing tag from local repository
```bash
git tag -d v0.0.2
```

Delete an existing tag from remote
```bash
git push --delete origin v0.0.2
```

Delete an existing release from remote
```bash
gh release delete v0.0.2
```

## Resources
- [Rye Building and Publishing Guide](https://rye.astral.sh/guide/publish/)
- [Typer Building a Package Guide](https://typer.tiangolo.com/tutorial/package/)
- [PyPI Python Packaging User Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Publishing Packages on PyPI Automated Deployment - Video Lecture by Qiusheng Wu](https://youtu.be/J0ClmuAbiMA?si=F5P4uRtqSawVKH5p)
