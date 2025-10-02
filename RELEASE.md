# Release Guide

This guide explains how to create a new release for finbrain-python.

## Tag Convention

Starting from v0.1.6, we use **`v`-prefixed tags** (e.g., `v0.1.6`, `v0.2.0`, `v1.0.0`).

## Release Process

### 1. Update CHANGELOG.md

Edit `CHANGELOG.md` and move items from `[Unreleased]` to a new version section:

```markdown
## [0.1.6] - 2025-01-15
### Added
- Your new features
### Changed
- Your changes
### Fixed
- Your bug fixes
```

### 2. Create and Push Tag

```bash
git add CHANGELOG.md
git commit -m "Release v0.1.6"
git tag -a v0.1.6 -m "Release v0.1.6: Brief description"
git push origin main
git push origin v0.1.6
```

### 3. GitHub Actions (Automated)

GitHub Actions will automatically:

- Build the wheel and source distribution
- Upload to TestPyPI first
- Upload to production PyPI

### 4. Create GitHub Release (Manual)

1. Go to: <https://github.com/ahmetsbilgin/finbrain-python/releases/new>
2. Select tag: `v0.1.6`
3. Title: `v0.1.6 - Brief Description`
4. Copy the relevant section from `CHANGELOG.md` into the description
5. Click "Publish release"

### 5. Verify

- Check PyPI: <https://pypi.org/project/finbrain-python/>
- Test installation: `pip install finbrain-python==0.1.6`

## How setuptools-scm Works

- Tag `v0.1.6` → Package version `0.1.6`
- The `v` prefix is automatically stripped

### Previous Tag Convention

Earlier releases used tags without the `v` prefix (e.g., `0.1.0`, `0.1.4`). Both formats work with setuptools-scm, but going forward we standardize on `v`-prefixed tags for consistency with common practices.

### Workflow Trigger

The GitHub Actions release workflow triggers on: `tags: ['v[0-9]*']`

This matches:

- ✅ `v0.1.0`
- ✅ `v1.2.3`
- ✅ `v10.20.30`
- ❌ `0.1.0` (old format, won't trigger)
- ❌ `version-0.1.0` (won't trigger)

### Version Scheme

We follow **Semantic Versioning** (semver):

- `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Examples

```bash
# Patch release (bug fixes)
git tag -a v0.1.5 -m "Fix retry logic in async client"

# Minor release (new features)
git tag -a v0.2.0 -m "Add async support"

# Major release (breaking changes)
git tag -a v1.0.0 -m "Stable API release"

# Push the tag
git push origin <tag-name>
```

### Checking Current Version

```bash
# See all tags
git tag -l

# See latest tag
git describe --tags --abbrev=0

# Check what version setuptools-scm will generate
python -m setuptools_scm
```
