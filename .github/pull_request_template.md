# Pull Request

## Description

This PR fixes Ruff linting issues reported in the CI pipeline to ensure the project follows the configured coding style and passes the `ruff check` workflow.

### Changes made

- Organized and formatted import statements.
- Moved module-level imports to the top of files.
- Removed trailing whitespace and blank-line whitespace.
- Added missing trailing newlines at the end of files.
- Removed unused local variables.
- Updated the Ruff configuration by removing deprecated ignore rules, where applicable.

These changes are non-functional and are intended to improve code quality and ensure CI passes successfully.

**Fixes:** #

---

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

---

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] All imports in my code are at the top of the file
- [ ] I did `ruff --fix` before committing and creating the PR
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] Any dependent changes have been merged and published in downstream modules
- [ ] I have only committed once
