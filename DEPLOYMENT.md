# Deployment Guide

## GitHub Pages Deployment

This website is ready for immediate deployment to GitHub Pages with zero configuration required.

### Quick Start

1. Go to your repository on GitHub
2. Click on **Settings**
3. Navigate to **Pages** in the left sidebar
4. Under "Source", select the branch: `copilot/recreate-portfolio-website` (or your preferred branch)
5. Keep the folder as `/ (root)`
6. Click **Save**
7. Wait a few minutes for GitHub to build and deploy
8. Your site will be available at: `https://yourusername.github.io/Tech-Blog/`

### Custom Domain (Optional)

To use a custom domain:

1. In the Pages settings, enter your custom domain
2. Add a CNAME file to the repository root with your domain name
3. Configure DNS with your domain provider:
   - Add a CNAME record pointing to `yourusername.github.io`
   - Or add A records pointing to GitHub Pages IPs

### Verification

Once deployed, verify that:
- [ ] All pages load correctly
- [ ] Dark mode toggle works
- [ ] Mobile menu functions properly
- [ ] Smooth scrolling works on all sections
- [ ] All links are functional
- [ ] Images load properly (when added)

### Troubleshooting

**Site not loading?**
- Check that GitHub Pages is enabled in settings
- Verify the correct branch is selected
- Wait 5-10 minutes after enabling Pages

**CSS not loading?**
- Ensure all files are committed and pushed
- Check browser console for errors
- Clear browser cache

**JavaScript errors?**
- Check browser console for specific errors
- Verify all script files are properly linked
- Ensure no external CDN dependencies are blocked

### Performance

The site is optimized for performance:
- No external dependencies
- Minimal file sizes (< 70KB total)
- Lazy loading support
- Efficient CSS and JavaScript

### Security

✅ CodeQL security scan passed with 0 vulnerabilities
✅ No external script injection
✅ No hardcoded credentials
✅ Safe localStorage usage

### Maintenance

To update content:
1. Edit `index.html` for text content
2. Edit `style.css` for styling changes
3. Edit `script.js` for functionality changes
4. Commit and push changes
5. GitHub Pages will automatically rebuild

### Support

For issues or questions:
- Check the README.md for documentation
- Review the code comments for guidance
- Test locally before deploying changes

---

Built with ❤️ for GitHub Pages
