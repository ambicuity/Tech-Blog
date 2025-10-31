# Regular Updates Guide

This guide shows you how to easily update your GitHub Pages site and have changes go live automatically.

## How GitHub Pages Auto-Updates Work

Once you've deployed your site to GitHub Pages (see [DEPLOYMENT.md](DEPLOYMENT.md)), any changes you push to the deployed branch will automatically trigger a rebuild and update your live site within 1-2 minutes.

## Quick Update Workflow

### For Content Changes

1. **Clone or pull the latest version** (if working from a new location):
```bash
git clone https://github.com/ambicuity/Tech-Blog.git
cd Tech-Blog
git checkout copilot/recreate-portfolio-website  # or your deployed branch
```

Or if you already have it locally:
```bash
git pull origin copilot/recreate-portfolio-website
```

2. **Make your changes** (see sections below for specific updates)

3. **Test locally** (optional but recommended):
```bash
# Start a local server
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

4. **Commit and push your changes**:
```bash
git add .
git commit -m "Update: describe your changes"
git push origin copilot/recreate-portfolio-website
```

5. **Wait 1-2 minutes** - GitHub Pages will automatically rebuild and deploy your changes!

## Common Update Scenarios

### 1. Update Your Bio or About Section

**File:** `index.html`  
**Location:** Lines 252-277 (About section)

**What to change:**
- Update the heading (line 260)
- Modify the description paragraphs (lines 261-268)
- Change skill badges (lines 270-275)

**Example:**
```html
<h3 class="text-3xl font-bold mb-4 text-gray-900 dark:text-white">
    Your New Title Here
</h3>
<p class="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
    Your updated bio paragraph here...
</p>
```

### 2. Add or Update Projects

**File:** `index.html`  
**Location:** Lines 286-387 (Projects section)

**To add a new project**, copy this template and paste it in the projects grid:

```html
<article class="project-card">
    <div class="project-image-placeholder">
        <svg class="w-16 h-16 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
            <!-- Icon SVG path here -->
        </svg>
    </div>
    <h3 class="text-xl font-bold mb-2 text-gray-900 dark:text-white">Your Project Name</h3>
    <p class="text-gray-600 dark:text-gray-300 mb-4">
        Project description goes here...
    </p>
    <div class="flex flex-wrap gap-2 mb-4">
        <span class="project-tag">Tech1</span>
        <span class="project-tag">Tech2</span>
        <span class="project-tag">Tech3</span>
    </div>
    <a href="https://your-project-url.com" class="project-link" aria-label="View Your Project">
        View Project →
    </a>
</article>
```

**To update existing projects:**
- Change the project name (h3 tag)
- Update the description
- Modify technology tags
- Update the project link

### 3. Update Skills

**File:** `index.html`  
**Location:** Lines 396-486 (Skills section)

**To add a skill to a category:**

```html
<li>New Skill Name</li>
```

**To add a new skill category**, copy this template:

```html
<div class="skill-category">
    <div class="skill-icon">
        <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
            <!-- Icon SVG -->
        </svg>
    </div>
    <h3 class="skill-title">Category Name</h3>
    <ul class="skill-list">
        <li>Skill 1</li>
        <li>Skill 2</li>
        <li>Skill 3</li>
    </ul>
</div>
```

### 4. Update Contact Information

**File:** `index.html`  
**Location:** Lines 495-553 (Contact section)

**Email:** Line 504 (update both mailto: link and display text)
```html
<a href="mailto:your.email@example.com" class="contact-card">
    ...
    <p class="text-sm text-gray-600 dark:text-gray-300">your.email@example.com</p>
</a>
```

**Social Links:** Lines 516-543
- Update GitHub username (line 520)
- Update LinkedIn profile (line 531)
- Update social media links in footer (lines 546-551)

### 5. Change Colors and Theme

**File:** `style.css`  
**Location:** Lines 11-31 (CSS variables)

**To change the color scheme:**

```css
:root {
    /* Change these values to your preferred colors */
    --primary-500: #0ea5e9;  /* Main accent color */
    --primary-600: #0284c7;  /* Darker accent */
    --blue-600: #2563eb;     /* Secondary accent */
}
```

**Popular color schemes:**
- **Purple Theme**: `--primary-500: #a855f7; --blue-600: #7c3aed;`
- **Green Theme**: `--primary-500: #10b981; --blue-600: #059669;`
- **Orange Theme**: `--primary-500: #f59e0b; --blue-600: #d97706;`
- **Pink Theme**: `--primary-500: #ec4899; --blue-600: #db2777;`

### 6. Update Site Title and Metadata

**File:** `index.html`  
**Location:** Lines 1-9 (Head section)

```html
<meta name="description" content="Your updated site description">
<meta name="keywords" content="your, keywords, here">
<meta name="author" content="Your Name">
<title>Your Site Title</title>
```

### 7. Add Images

**Location:** Create files in `assets/images/` directory

**Steps:**
1. Add your image files to the `assets/images/` folder
2. Update the `index.html` to reference your images

**For profile picture:**
```html
<!-- Replace the placeholder SVG (around line 251) with: -->
<img src="assets/images/profile.jpg" alt="Your Name" class="w-full h-full object-cover rounded-2xl">
```

**For project images:**
```html
<!-- Replace project-image-placeholder (around lines 294, 323, 352) with: -->
<img src="assets/images/project1.jpg" alt="Project Name" class="w-full h-48 object-cover rounded-lg mb-4">
```

## Tips for Regular Updates

### Best Practices

1. **Test locally first**: Always preview changes in your browser before pushing
2. **Commit often**: Make small, frequent commits with clear messages
3. **Use descriptive commit messages**: E.g., "Update project portfolio with new app", "Change contact email"
4. **Keep backups**: GitHub automatically keeps your version history
5. **Check live site**: After pushing, wait 2 minutes and refresh your live site to verify changes

### Commit Message Examples

```bash
git commit -m "Add new portfolio project: Weather App"
git commit -m "Update bio and skills section"
git commit -m "Change theme colors to purple scheme"
git commit -m "Update contact email address"
git commit -m "Add profile picture and project images"
```

### Common Issues

**Problem:** Changes not showing on live site  
**Solution:** 
- Wait 2-3 minutes for GitHub Pages to rebuild
- Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check GitHub Actions tab for build status

**Problem:** Site broken after update  
**Solution:**
- Check browser console (F12) for errors
- Revert to previous commit if needed:
  ```bash
  git revert HEAD
  git push origin copilot/recreate-portfolio-website
  ```

**Problem:** Can't push changes  
**Solution:**
- Make sure you have write access to the repository
- Pull latest changes first: `git pull`
- Resolve any conflicts, then push again

## Automated Updates (Advanced)

### Using GitHub's Web Interface

You can edit files directly on GitHub without cloning:

1. Navigate to the file on GitHub
2. Click the pencil icon (Edit)
3. Make your changes
4. Scroll down and commit directly to the branch
5. Changes will deploy automatically!

This is great for quick text updates when you don't have access to your computer.

### Schedule Regular Updates

You can use GitHub Actions to schedule automatic updates (like updating the copyright year):

1. Create `.github/workflows/update.yml`
2. Set up a scheduled workflow
3. Automate repetitive updates

(See GitHub Actions documentation for details)

## Quick Reference

| Update Type | File | Approximate Line |
|------------|------|------------------|
| Site title | `index.html` | 9 |
| Hero heading | `index.html` | 76-78 |
| About bio | `index.html` | 252-277 |
| Projects | `index.html` | 286-387 |
| Skills | `index.html` | 396-486 |
| Contact info | `index.html` | 495-553 |
| Colors | `style.css` | 11-31 |
| Fonts | `style.css` | Various |

## Need Help?

- Check the [README.md](README.md) for general documentation
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment setup
- Review the code comments in each file for guidance
- Test changes locally before pushing to avoid breaking the live site

---

**Remember:** Every push to your deployed branch automatically updates your live site! 🚀
