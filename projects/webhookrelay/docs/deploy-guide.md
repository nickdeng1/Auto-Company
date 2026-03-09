# Deployment Guide - WebhookRelay Landing Page

## Quick Deploy Options

### Option 1: Cloudflare Pages (Recommended)

```bash
# Install wrangler if not already installed
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy from project directory
cd projects/webhookrelay
wrangler pages deploy public --project-name=webhookrelay
```

### Option 2: GitHub Pages

```bash
# Create a new repository
git init
git add public/
git commit -m "Initial landing page"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/webhookrelay.git
git push -u origin main

# Enable GitHub Pages in repository settings
# Settings → Pages → Source: main branch → /public folder
```

### Option 3: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd projects/webhookrelay
netlify deploy --prod --dir=public
```

### Option 4: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd projects/webhookrelay
vercel --prod
```

---

## Manual Deployment Checklist

- [ ] Choose deployment platform
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (automatic on most platforms)
- [ ] Configure environment variables (if needed)
- [ ] Test deployed URL
- [ ] Update DNS records (if using custom domain)

---

## Post-Deployment

### Verify Deployment

```bash
# Check if site is accessible
curl -I https://your-deployed-url.com

# Expected: HTTP 200 OK
```

### Set Up Analytics (Optional)

1. Google Analytics 4
2. Cloudflare Web Analytics
3. Plausible Analytics

### Set Up Monitoring (Optional)

1. Uptime monitoring (UptimeRobot, Pingdom)
2. Error tracking (Sentry)

---

## Custom Domain Setup

### Cloudflare Pages

1. Go to your Pages project settings
2. Add custom domain
3. Update DNS records as instructed
4. Wait for SSL certificate provisioning

### DNS Records Example

```
Type: CNAME
Name: www
Content: webhookrelay.pages.dev
Proxy: Yes (Cloudflare proxy)
```

---

## Troubleshooting

### Common Issues

1. **Build fails**: Check if all files are in the `public/` directory
2. **404 errors**: Ensure `index.html` is in the root of `public/`
3. **CSS not loading**: Check if Tailwind CDN is accessible
4. **Form not working**: This is expected - form uses localStorage for demo

### Support

- Cloudflare Docs: https://developers.cloudflare.com/pages/
- GitHub Pages Docs: https://docs.github.com/en/pages
- Netlify Docs: https://docs.netlify.com/
- Vercel Docs: https://vercel.com/docs