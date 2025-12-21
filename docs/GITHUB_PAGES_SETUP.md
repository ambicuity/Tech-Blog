# GitHub Pages Setup Guide

This guide will help you configure GitHub Pages for the Tech Blog repository.

## Overview

The Tech Blog uses Jekyll with the Chirpy theme and automatically deploys to GitHub Pages using GitHub Actions. The deployment workflow is already configured in `.github/workflows/pages-deploy.yml`.

## Required Configuration Steps

### 1. Enable GitHub Pages with GitHub Actions

To enable GitHub Pages deployment, you need to configure the repository settings:

1. Navigate to your repository on GitHub
2. Click on **Settings** (top navigation bar)
3. In the left sidebar, click on **Pages**
4. Under **Build and deployment**:
   - **Source**: Select **GitHub Actions** from the dropdown
   
That's it! The workflow will now automatically deploy your site when changes are pushed to the `main` branch.

## How It Works

### Automatic Deployment

The deployment workflow (`.github/workflows/pages-deploy.yml`) is triggered:
- On every push to the `main` or `master` branch
- Manually from the Actions tab (workflow_dispatch)

### Deployment Process

1. **Build**: The workflow builds the Jekyll site with the Chirpy theme
2. **Test**: Runs HTML validation on the built site
3. **Deploy**: Deploys the site to GitHub Pages

## Accessing Your Site

After the workflow completes successfully:
- Your site will be available at the URL configured in `_config.yml`
- The default URL is: `https://<username>.github.io/<repository-name>/`
- Custom domains: If you've set up a custom domain in the repository settings, the site will be available at that domain

## Troubleshooting

### Site Not Updating

If your site is not updating after pushing changes:

1. Check the Actions tab to verify the workflow ran successfully
2. Look for any errors in the workflow logs
3. Ensure GitHub Pages is configured to use "GitHub Actions" as the source
4. Wait a few minutes - deployment can take 1-2 minutes

### Build Errors

If the build fails:

1. Check the Actions tab for the specific error
2. Common issues:
   - Missing dependencies in `Gemfile`
   - Invalid front matter in posts
   - Syntax errors in `_config.yml`

### Custom Domain Configuration

If you're using a custom domain:

1. Add a CNAME file with your domain name to the repository root
2. Configure DNS records with your domain provider
3. Enable HTTPS in GitHub Pages settings (recommended)

## Workflow Details

### Permissions

The workflow requires these permissions:
- `contents: read` - To checkout the repository
- `pages: write` - To deploy to GitHub Pages
- `id-token: write` - For authentication

### Environment

The workflow uses the `github-pages` environment, which provides:
- Deployment status tracking
- Deployment history
- Optional protection rules

## Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [Chirpy Theme Documentation](https://github.com/cotes2020/jekyll-theme-chirpy)
