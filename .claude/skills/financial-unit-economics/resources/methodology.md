# Financial Unit Economics Methodology

Advanced techniques for calculating, analyzing, and optimizing unit economics.

## Table of Contents
1. [Customer Acquisition Cost (CAC)](#1-customer-acquisition-cost-cac)
2. [Lifetime Value (LTV)](#2-lifetime-value-ltv)
3. [Contribution Margin Analysis](#3-contribution-margin-analysis)
4. [Cohort Analysis](#4-cohort-analysis)
5. [Interpreting Unit Economics](#5-interpreting-unit-economics)
6. [Advanced Topics](#6-advanced-topics)

---

## 1. Customer Acquisition Cost (CAC)

### Fully-Loaded CAC Components

**Formula**: CAC = (Total S&M Costs) ÷ New Customers Acquired

**Sales & Marketing (S&M) Costs to include**:
- **Marketing spend**: Paid ads (Google, Facebook, LinkedIn), content marketing, SEO tools, events, sponsorships
- **Sales team compensation**: Base salaries, commissions, bonuses, benefits, taxes
- **Marketing team compensation**: Marketers, designers, writers, contractors
- **Sales tools**: CRM (Salesforce, HubSpot), sales engagement (Outreach, SalesLoft), analytics
- **Marketing tools**: Marketing automation (Marketo, Pardot), analytics (Google Analytics, Mixpanel), advertising platforms
- **Overhead allocation**: Portion of office space, admin support, IT costs attributable to S&M teams
- **Agency/consultant fees**: External agencies, freelancers, consultants for marketing or sales

**What NOT to include** (not acquisition costs):
- Engineering/product development (build the product, not acquire customers)
- Customer success/support (retain customers, not acquire)
- General & administrative (not directly related to acquisition)

### Time Period for CAC

**Match costs to revenue period**: If calculating monthly CAC, use monthly S&M costs and monthly new customers.

**Lag effect**: CAC spent today may yield customers next month. Adjust if significant lag (e.g., long sales cycles). Use 1-3 month lag for enterprise sales.

**Example**:
- Month 1: $50k S&M spend, 100 customers acquired → CAC = $500
- But if customers from Month 1 spend came from ads run in Month 0, adjust accordingly.

### CAC by Channel

Breaking down CAC by channel reveals which channels are efficient vs. inefficient.

**Method**: Track spend and new customers per channel.

**Example**:

| Channel | S&M Spend | New Customers | CAC | LTV | LTV/CAC |
|---------|-----------|---------------|-----|-----|---------|
| Paid Search | $30k | 100 | $300 | $900 | 3.0 |
| Organic | $10k | 100 | $100 | $1,200 | 12.0 |
| Referral | $5k | 50 | $100 | $1,500 | 15.0 |
| Paid Social | $20k | 50 | $400 | $700 | 1.75 |

**Insight**: Organic and Referral have best economics (low CAC, high LTV). Paid Social is unprofitable (LTV/CAC <2:1). Action: Increase organic/referral investment, pause paid social.

### CAC Trends Over Time

**Monitor CAC trends**: Is CAC increasing or decreasing over time?

**Causes of rising CAC**:
- Market saturation (exhausted easy channels)
- Increased competition (competitors bidding up ad costs)
- Product-market fit weakening (harder to acquire customers)
- Inefficient spend (poor targeting, low conversion rates)

**Causes of falling CAC**:
- Improved conversion rates (better landing pages, messaging)
- Brand awareness (more direct/organic traffic)
- Product-led growth (virality, word-of-mouth)
- Channel optimization (focusing on best-performing channels)

---

## 2. Lifetime Value (LTV)

### LTV Calculation Methods

**Method 1: Simple LTV (Subscription)**

```
LTV = ARPU × Gross Margin % ÷ Monthly Churn Rate
```

**When to use**: Early-stage SaaS, limited data, need quick estimate.

**Example**:
- ARPU = $50/month
- Gross Margin = 80%
- Monthly Churn = 5%
- LTV = $50 × 80% ÷ 0.05 = $50 × 80% × 20 months = $800

**Method 2: Cohort-Based LTV (More Accurate)**

Track actual retention by cohort, sum revenue over observed periods.

```
LTV = ARPU × Gross Margin × Σ(Retention at month i)
```

**Example Cohort** (acquired Jan 2024):

| Month | Retention % | Revenue (ARPU × Retention) | Cumulative |
|-------|-------------|----------------------------|------------|
| 0 | 100% | $50 × 1.0 = $50 | $50 |
| 1 | 95% | $50 × 0.95 = $47.50 | $97.50 |
| 2 | 88% | $50 × 0.88 = $44 | $141.50 |
| 3 | 80% | $50 × 0.80 = $40 | $181.50 |
| 6 | 60% | $50 × 0.60 = $30 | ~$280 |
| 12 | 40% | $50 × 0.40 = $20 | ~$450 |

LTV = $450 × 80% gross margin = **$360**

Note: This is more conservative than simple LTV ($800) because early churn is higher than average.

**Method 3: Predictive LTV (Machine Learning)**

Use historical data to predict future retention and spending patterns. Advanced approach for companies with large datasets.

**Inputs**: Customer attributes (demographics, behavior, acquisition channel), historical purchase/churn data.
