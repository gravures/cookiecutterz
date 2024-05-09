# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/gravures/cookiecutterz/blob/python-coverage/htmlcov/index.html)

| Name                              |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/cookiecutterz/\_\_init\_\_.py |       44 |        8 |       18 |        0 |     81% |75-77, 88-90, 101-102 |
| src/cookiecutterz/cruft.py        |        8 |        8 |        0 |        0 |      0% |     16-28 |
| src/cookiecutterz/extensions.py   |       37 |       24 |       10 |        0 |     28% |33, 37, 42, 47-52, 57-96 |
| src/cookiecutterz/main.py         |        8 |        8 |        0 |        0 |      0% |     16-27 |
| src/cookiecutterz/pdm.py          |       40 |       40 |       12 |        0 |      0% |    16-101 |
|                         **TOTAL** |  **137** |   **88** |   **40** |    **0** | **36%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/gravures/cookiecutterz/python-coverage/badge.svg)](https://htmlpreview.github.io/?https://github.com/gravures/cookiecutterz/blob/python-coverage/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/gravures/cookiecutterz/python-coverage/endpoint.json)](https://htmlpreview.github.io/?https://github.com/gravures/cookiecutterz/blob/python-coverage/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fgravures%2Fcookiecutterz%2Fpython-coverage%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/gravures/cookiecutterz/blob/python-coverage/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.