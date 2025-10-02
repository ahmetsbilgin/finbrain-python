# Release Guide

## Tag Convention

Starting from the next release, we use **`v`-prefixed tags** (e.g., `v0.2.0`, `v1.0.0`).

### Creating a New Release

1. **Update version and create tag:**

   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0: Add async support"
   git push origin v0.2.0
   ```

2. **GitHub Actions will automatically:**
   - Build the wheel and source distribution
   - Upload to TestPyPI first
   - Then upload to production PyPI

3. **setuptools-scm will:**
   - Automatically strip the `v` prefix
   - Tag `v0.2.0` → Package version `0.2.0`

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
