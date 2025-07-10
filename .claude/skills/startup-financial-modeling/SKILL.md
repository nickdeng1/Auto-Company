---
name: startup-financial-modeling
description: This skill should be used when the user asks to "create financial projections", "build a financial model", "forecast revenue", "calculate burn rate", "estimate runway", "model cash flow", or requests 3-5 year financial planning for a startup.
version: 1.0.0
---

# Startup Financial Modeling

Build comprehensive 3-5 year financial models with revenue projections, cost structures, cash flow analysis, and scenario planning for early-stage startups.

## Overview

Financial modeling provides the quantitative foundation for startup strategy, fundraising, and operational planning. Create realistic projections using cohort-based revenue modeling, detailed cost structures, and scenario analysis to support decision-making and investor presentations.

## Core Components

### Revenue Model

**Cohort-Based Projections:**
Build revenue from customer acquisition and retention by cohort.

**Formula:**

```
MRR = Σ (Cohort Size × Retention Rate × ARPU)
ARR = MRR × 12
```

**Key Inputs:**

- Monthly new customer acquisitions
- Customer retention rates by month
- Average revenue per user (ARPU)
- Pricing and packaging assumptions
- Expansion revenue (upsells, cross-sells)

### Cost Structure

**Operating Expenses Categories:**

1. **Cost of Goods Sold (COGS)**
   - Hosting and infrastructure
   - Payment processing fees
   - Customer support (variable portion)
   - Third-party services per customer

2. **Sales & Marketing (S&M)**
   - Customer acquisition cost (CAC)
   - Marketing programs and advertising
   - Sales team compensation
   - Marketing tools and software

3. **Research & Development (R&D)**
   - Engineering team compensation
   - Product management
   - Design and UX
   - Development tools and infrastructure

4. **General & Administrative (G&A)**
   - Executive team
   - Finance, legal, HR
   - Office and facilities
   - Insurance and compliance

### Cash Flow Analysis

**Components:**

- Beginning cash balance
- Cash inflows (revenue, fundraising)
- Cash outflows (operating expenses, CapEx)
- Ending cash balance
- Monthly burn rate
- Runway (months of cash remaining)

**Formula:**

```
Runway = Current Cash Balance / Monthly Burn Rate
Monthly Burn = Monthly Revenue - Monthly Expenses
```

### Headcount Planning

**Role-Based Hiring Plan:**
Track headcount by department and role.

**Key Metrics:**

- Fully-loaded cost per employee
- Revenue per employee
- Headcount by department (% of total)

**Typical Ratios (Early-Stage SaaS):**

- Engineering: 40-50%
- Sales & Marketing: 25-35%
- G&A: 10-15%
- Customer Success: 5-10%

## Financial Model Structure

### Three-Scenario Framework

**Conservative Scenario (P10):**

- Slower customer acquisition
- Lower pricing or conversion
- Higher churn rates
- Extended sales cycles
- Used for cash management

**Base Scenario (P50):**

- Most likely outcomes
- Realistic assumptions
- Primary planning scenario
- Used for board reporting

**Optimistic Scenario (P90):**

- Faster growth
- Better unit economics
- Lower churn
