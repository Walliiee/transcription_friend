## Description

<!-- Provide a brief description of your changes -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing

<!-- Describe the tests you ran and how to reproduce them -->

- [ ] Tested locally
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Tested on GPU (if applicable)
- [ ] Tested on CPU fallback (if applicable)

### Test Commands Run

```bash
# Example:
pytest -v
pytest -v -m "not slow"
python transcribe_faster_gpu.py test.m4a
```

## Code Quality Checklist

<!-- Check all that have been completed -->

- [ ] Code follows the project's style guidelines (ruff/black formatting)
- [ ] Self-review completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated (if needed)
- [ ] No new warnings introduced
- [ ] Type hints added (for new functions/methods)

## Pre-commit Checks

<!-- These should run automatically via pre-commit hooks -->

- [ ] `pre-commit run --all-files` passes
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Formatting is correct (`ruff format .` or `black .`)
- [ ] Type checking passes (`mypy .`) or type errors are acceptable

## Boy Scout Rule

<!-- Did you leave the code better than you found it? -->

- [ ] Modified files have been cleaned up (formatting, imports, etc.)
- [ ] Removed unused imports/variables
- [ ] Improved clarity of existing code (if touched)
- [ ] Added tests for modified code (if applicable)

## Dependencies

<!-- Check if applicable -->

- [ ] No new dependencies added
- [ ] New dependencies added and documented in `requirements.txt`
- [ ] Dependencies are compatible with project requirements (e.g., CUDA version)

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

N/A

## Related Issues

<!-- Link to related issues using #issue-number -->

Closes #
Related to #

## Screenshots / Logs

<!-- If applicable, add screenshots or example output -->

<details>
<summary>Click to expand logs/output</summary>

```
Paste relevant logs or output here
```

</details>

## Reviewer Notes

<!-- Anything specific you want reviewers to focus on? -->

-
-

## Deployment Notes

<!-- Any special deployment considerations? -->

N/A

---

## Checklist for Reviewers

<!-- For reviewers to check during review -->

- [ ] Code is readable and maintainable
- [ ] Tests are adequate and pass
- [ ] No security vulnerabilities introduced
- [ ] Performance implications considered
- [ ] Documentation is clear and accurate
- [ ] Breaking changes are clearly documented
