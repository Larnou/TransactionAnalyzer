from invoke import task


@task
def flake8(ctx):
    # запуск: inv flake8
    ctx.run("poetry run flake8 src/")
    ctx.run("poetry run flake8 tests/")


@task
def black(ctx):
    # запуск: inv black
    ctx.run("poetry run black src/")
    ctx.run("poetry run black tests/")


@task
def mypy(ctx):
    # запуск: inv mypy
    ctx.run("poetry run mypy src/")
    ctx.run("poetry run mypy tests/")


@task
def isort(ctx):
    # запуск: inv isort
    ctx.run("poetry run isort src/")
    ctx.run("poetry run isort tests/")


@task
def report(ctx):
    ctx.run("poetry run pytest --cov=src --cov-report=html")


@task
def test(ctx):
    """Запуск тестов с кодировкой UTF-8"""
    ctx.run("pytest -v")
