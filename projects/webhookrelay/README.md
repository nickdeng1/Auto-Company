# WebhookRelay Landing Page

> Reliable webhook delivery as a service - Demand validation landing page

## Quick Start

```bash
# Open locally
open public/index.html

# Or serve with Python
python -m http.server 8000 -d public
```

## Project Structure

```
webhookrelay/
├── public/
│   └── index.html      # Landing page (single file)
├── docs/
│   ├── qa-review.md    # QA review report
│   └── deploy-guide.md # Deployment instructions
├── scripts/
│   └── deploy.sh       # Cloudflare Pages deploy script
└── test-checklist.md   # Manual test checklist
```

## Features

- Modern, responsive design
- Dark theme with gradient accents
- Waitlist form with email capture
- Pricing tiers ($29, $79, $199)
- SEO optimized
- Mobile-first responsive

## Deployment

See [docs/deploy-guide.md](docs/deploy-guide.md) for deployment options.

### Cloudflare Pages (Recommended)

```bash
wrangler pages deploy public --project-name=webhookrelay
```

## Testing

See [test-checklist.md](test-checklist.md) for manual testing checklist.

## Tech Stack

- HTML5
- Tailwind CSS (via CDN)
- Vanilla JavaScript
- Google Fonts (Inter)

## Status

- **Phase**: Demand Validation
- **Target**: 100 waitlist signups
- **Timeline**: 2 weeks

---

Built by [Auto Company](https://github.com/nickdeng1/Auto-Company)