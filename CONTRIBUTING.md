# Contributing to SRT Translator

First off, thank you for considering contributing to SRT Translator! It's people like you that make SRT Translator such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that the problem has already been reported or fixed.

When you are creating a bug report, please include as many details as possible:
* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include SRT snippets if possible.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/fam007e/SRT_Trans/issues).

When creating an enhancement suggestion, please include:
* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps** or use cases.
* **Explain why this enhancement would be useful** to most users.

### Pull Requests

* Fill in the [PULL_REQUEST_TEMPLATE](.github/PULL_REQUEST_TEMPLATE.md).
* Ensure the test suite passes by running `make check`.
* Follow the existing code style (monitored by Ruff and MyPy).
* Document any change in behavior.

## Development Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`.
3. Activate it:
   - Linux/macOS: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
4. Run setup: `make setup`.
5. Run all checks: `make check`.

## Styleguides

### Python Styleguide

All Python code is linted with **Ruff** and type-checked with **MyPy**.
* Check linting: `make lint`
* Check types: `make type-check`
* Run all validations: `make check`

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown/).
* Use descriptive titles for sections.
* Include code blocks for examples.

## License

By contributing, you agree that your contributions will be licensed under its [MIT License](LICENSE).
