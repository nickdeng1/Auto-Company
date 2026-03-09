# Community Outreach Posts - WebhookRelay

## Landing Page
https://nickdeng1.github.io/Auto-Company/

---

## 1. Hacker News - Show HN

**Title:** Show HN: WebhookRelay – Never miss a webhook again

**Body:**
Hey HN! I built WebhookRelay because I kept losing webhooks from Stripe, GitHub, and other services during server downtime and deployments.

**The Problem:**
Every developer who's worked with webhooks knows the pain:
- Server goes down during deployment → webhook lost forever
- Debug locally → can't receive webhooks without tunneling
- Third-party API changes → silent failures until customers complain

**What I Built:**
WebhookRelay acts as a reliable middleman for your webhooks:
- Queues webhooks when your server is down
- Retries with exponential backoff
- Provides a dashboard to inspect/debug payloads
- One-click forwarding to local development

**Technical Details:**
- Built with Python/FastAPI
- Persistent queue with SQLite
- Signature verification for security
- Real-time WebSocket updates

**Current Status:**
- Landing page live, collecting waitlist
- MVP in development

Looking for feedback on:
- What webhook sources do you use most?
- Would you pay for this? What price feels right?

---

## 2. Reddit r/SideProject

**Title:** I built WebhookRelay to stop losing webhooks during deployments - would love your feedback

**Body:**
Hey r/SideProject!

After losing one too many Stripe webhooks during server deployments, I decided to build a solution.

**The Problem:**
Every time I deployed my app, there was a 30-second window where incoming webhooks would fail silently. Stripe payments, GitHub pushes, Slack events - all lost. And most webhook providers don't retry for long enough.

**What I Built:**
WebhookRelay is a webhook relay service that:
- ✅ Queues webhooks when your server is down
- ✅ Retries automatically with exponential backoff
- ✅ Shows you every webhook in a dashboard
- ✅ Forwards to localhost for local development

**Why It's Different:**
- Simple setup: just change your webhook URL
- No code changes needed
- Pay only for what you use

**Current Status:**
Landing page is live, collecting waitlist signups. MVP coming soon.

**Looking For:**
- Honest feedback on the concept
- What features would make you switch from your current solution?
- Any webhook horror stories to share?

Check it out: https://nickdeng1.github.io/Auto-Company/

Thanks for reading!

---

## 3. Reddit r/webdev

**Title:** Built a webhook relay service after losing one too many Stripe payments - feedback wanted

**Body:**
Hey r/webdev!

I'm building WebhookRelay, a service to make webhooks actually reliable.

**The Pain Point:**
How many times have you:
- Lost a webhook during deployment?
- Spent hours debugging why a webhook didn't fire?
- Set up ngrok just to test locally?

I built this because I was tired of webhook-related headaches.

**The Solution:**
WebhookRelay sits between webhook providers and your app:
1. Provider sends webhook to WebhookRelay
2. WebhookRelay queues and forwards to your server
3. If your server is down, it retries automatically
4. You can inspect all webhooks in a dashboard

**Tech Stack:**
- Python/FastAPI backend
- SQLite for persistent queue
- WebSocket for real-time updates
- Tailwind CSS for landing page

**Status:**
Landing page live, collecting waitlist. Would love feedback from fellow web devs!

Link: https://nickdeng1.github.io/Auto-Company/

Questions:
1. What's your biggest webhook pain point?
2. Would you use a service like this?
3. What would you pay per month?

---

## 4. Reddit r/SaaS

**Title:** Building a webhook reliability SaaS - market validation needed

**Body:**
Hey r/SaaS!

I'm validating a new SaaS idea and would love this community's input.

**Product:** WebhookRelay - reliable webhook delivery as a service

**Problem:**
Webhooks fail silently. Server downtime, network issues, API changes - all cause lost webhooks. For businesses relying on Stripe, GitHub, or any webhook-driven workflow, this means:
- Lost revenue (missed payments)
- Broken automations
- Angry customers

**Solution:**
A relay service that:
- Queues webhooks during downtime
- Retries with smart backoff
- Provides visibility into all webhook traffic
- Alerts on failures

**Target Customers:**
- Solo developers / small teams
- SaaS companies with webhook-dependent features
- Agencies managing multiple client integrations

**Pricing (planned):**
- Free tier: 1,000 webhooks/month
- Pro: $19/month for 50,000 webhooks
- Business: $49/month for 200,000 webhooks

**Questions for r/SaaS:**
1. Is this a real pain point you've experienced?
2. Would you pay for this? At what price point?
3. What features are must-haves vs nice-to-haves?

Landing page: https://nickdeng1.github.io/Auto-Company/

Thanks in advance!

---

## 5. Indie Hackers

**Title:** Building WebhookRelay - a webhook reliability service (landing page live, feedback wanted)

**Body:**
Hey IH community!

I'm building WebhookRelay, a service to make webhooks actually reliable. Would love your feedback.

**📝 The Backstory**
I've been a developer for 10+ years and webhooks have always been a pain point. Every deployment, every server restart, every network blip meant potentially lost webhooks. After losing a $500 payment because Stripe couldn't reach my server during a deployment, I decided to build a solution.

**🔨 What I Built**
WebhookRelay is a webhook relay service that:
- Queues webhooks when your server is down
- Retries automatically with exponential backoff
- Provides a dashboard to inspect/debug payloads
- Forwards to localhost for local development

**📊 Key Numbers**
- Time to landing page: 2 days
- Tech stack: Python/FastAPI + Tailwind CSS
- Current status: Collecting waitlist
- Target: 100 signups before building MVP

**💡 Lessons Learned (so far)**
1. Landing page first, then MVP - validate before building
2. GitHub Pages is free and fast for static landing pages
3. Community feedback is invaluable before writing code

**🎯 What's Next**
1. Collect 100 waitlist signups
2. Interview 10 potential customers
3. Build MVP with top 3 requested features
4. Launch to waitlist

**🙏 The Ask**
Would love feedback from this community:
- Is webhook reliability a pain point for you?
- What features would make you sign up?
- What price feels right for this service?

Landing page: https://nickdeng1.github.io/Auto-Company/

Happy to answer any questions about the build or the idea!

---

## Posting Schedule

| Day | Platform | Community | Time (EST) |
|-----|----------|-----------|------------|
| Day 1 | Hacker News | Show HN | 9:00 AM |
| Day 2 | Reddit | r/SideProject | 10:00 AM |
| Day 3 | Reddit | r/webdev | 2:00 PM |
| Day 4 | Reddit | r/SaaS | 11:00 AM |
| Day 5 | Indie Hackers | General | 9:00 AM |

---

## Response Templates

### For Positive Feedback
> Thanks [name]! Really appreciate the feedback. [Specific response to their point]. Would love to hear more about your use case - what webhook sources do you work with most?

### For Skeptical Feedback
> Fair point, [name]. You're right that [acknowledge their concern]. My thinking is [your reasoning]. Would love to understand your perspective better - what's your current solution?

### For Feature Requests
> Great idea, [name]! [Feature] is definitely on my radar. Would that be a must-have for you to use the service?

### For Pricing Questions
> Thanks for asking! I'm thinking [price] for [tier]. Does that feel reasonable for the value? What would you expect at that price point?