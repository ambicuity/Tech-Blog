# Tech Blog - Portfolio Website

A modern, responsive portfolio website built with HTML5, CSS3, and vanilla JavaScript. Features a clean design, dark mode toggle, smooth animations, and full accessibility support.

## 🌟 Features

- **Modern Design**: Clean, professional layout with gradient accents
- **Fully Responsive**: Optimized for mobile, tablet, and desktop devices
- **Dark Mode**: Toggle between light and dark themes with localStorage persistence
- **Smooth Animations**: Fade-in effects, smooth scrolling, and interactive hover states
- **Accessibility**: Semantic HTML5, ARIA labels, keyboard navigation
- **Performance**: No external dependencies, optimized CSS and JavaScript
- **SEO Ready**: Proper meta tags and semantic structure

## 📁 Project Structure

```
Tech-Blog/
├── index.html          # Main HTML file
├── style.css           # Custom CSS styles (standalone, no dependencies)
├── script.js           # Interactive JavaScript features
├── assets/             # Directory for images and icons
│   ├── images/
│   └── icons/
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🚀 Getting Started

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/ambicuity/Tech-Blog.git
cd Tech-Blog
```

2. Open `index.html` in your browser or start a local server:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Using PHP
php -S localhost:8000
```

3. Visit `http://localhost:8000` in your browser

### Deployment to GitHub Pages

This site is ready for GitHub Pages deployment:

1. Go to your repository Settings
2. Navigate to Pages section
3. Select the branch (e.g., `main` or `copilot/recreate-portfolio-website`)
4. Select root directory
5. Save and wait for deployment

Your site will be available at: `https://yourusername.github.io/Tech-Blog/`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Updating Your Site

Once deployed, you can easily update your site content regularly. Any changes pushed to your deployed branch will automatically update your live site within 1-2 minutes.

See [UPDATING.md](UPDATING.md) for a complete guide on:
- Making content updates (bio, projects, skills, contact info)
- Changing colors and themes
- Adding images
- Best practices for regular updates
- Quick reference guide for common changes

## 🎨 Customization

### Colors

The color palette is defined in CSS variables in `style.css`:

```css
:root {
    --primary-500: #0ea5e9;
    --primary-600: #0284c7;
    --blue-600: #2563eb;
    /* ... more colors */
}
```

### Content

Edit `index.html` to customize:
- Personal information and bio
- Project descriptions
- Skills and technologies
- Contact information and social links

### Styling

Modify `style.css` to adjust:
- Typography and spacing
- Colors and gradients
- Animations and transitions
- Responsive breakpoints

## 🔧 Technical Stack

- **HTML5**: Semantic markup
- **CSS3**: Custom styles with flexbox and grid
- **JavaScript (ES6+)**: Vanilla JS for interactions
- **No frameworks or libraries**: Lightweight and fast

## ✨ Key Sections

1. **Header/Navigation**: Fixed header with smooth scroll links
2. **Hero Section**: Landing section with call-to-action buttons
3. **About**: Professional introduction and competencies
4. **Projects**: Featured portfolio projects showcase
5. **Skills**: Technical skills organized by category
6. **Contact**: Multiple contact methods and social links
7. **Footer**: Copyright and navigation

## 🌙 Dark Mode

The site includes a fully functional dark mode that:
- Toggles with a button in the header
- Saves preference in localStorage
- Respects system color scheme preference
- Provides smooth transitions between themes

## ♿ Accessibility

- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation support
- Focus indicators
- Sufficient color contrast
- Responsive text sizing
- Reduced motion support

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

For questions or feedback, please reach out through the contact form on the website.

---

Built with ❤️ for GitHub Pages