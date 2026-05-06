# Streamlit Deployment

## App

- App name: `Portfolio Action Console`
- Repository: `zzddddzz/MSDS498`
- Branch: `main`
- Entrypoint: `streamlit_app.py`
- Python version: `3.12`
- Secrets required: none

## Dependencies

Community Cloud should use:

- `project/msds498-capstone-team54/requirements.txt`

The app ships with segment-level demo data so no private workbook needs to be uploaded for public deployment.

## Rollback

Original source checkpoint in the private working repo before this app was added:

- `checkpoint/msds498-pre-streamlit-20260506-151503`
- SHA: `b72aa44d73c53022c4dce7a8bbab9461069edcd9`

To undo only the app commit after it is merged to `main`, use `git revert <app_commit_sha>`. To return the repo to the exact pre-app checkpoint in a local throwaway branch, use:

```bash
git fetch origin --tags
git switch -c restore-msds498-streamlit checkpoint/msds498-pre-streamlit-20260506-151503
```

## Streamlit Community Cloud Fields

When creating the app at `share.streamlit.io`:

- Repository: `zzddddzz/MSDS498`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Custom subdomain suggestion: `msds498-portfolio-action`
