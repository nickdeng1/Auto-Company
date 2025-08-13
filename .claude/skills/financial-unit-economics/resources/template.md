# Financial Unit Economics Templates

Quick-start templates for calculating CAC, LTV, contribution margin, and cohort analysis.

## Unit Definition Template

**Business model**: [Subscription / Transactional / Marketplace / Freemium / Enterprise]

**Unit of analysis**: [What are you measuring?]
- Customer (entire relationship)
- Subscription (per subscription period)
- Transaction (per purchase)
- Product SKU (per product sold)
- User (active user)

**Time period**: [Monthly / Quarterly / Annual cohorts]

**Segments** (if analyzing by segment):
- [ ] Acquisition channel (paid search, organic, referral, etc.)
- [ ] Customer type (B2B vs B2C, SMB vs Enterprise)
- [ ] Geography (US, EU, APAC)
- [ ] Product tier (Free, Pro, Enterprise)

---

## CAC Calculation Template

**Customer Acquisition Cost (CAC)** = Total acquisition costs ÷ New customers acquired

### Fully-Loaded CAC

**Sales & Marketing Costs** (period: [Month/Quarter/Year])

| Cost Category | Amount | Notes |
|---------------|--------|-------|
| **Marketing spend** | $[X] | Paid ads, content marketing, events, tools |
| **Sales team salaries** | $[X] | Base + commission + benefits |
| **Sales tools & software** | $[X] | CRM, sales engagement, analytics |
| **Marketing team salaries** | $[X] | Marketers, designers, contractors |
| **Overhead allocation** | $[X] | % of office, admin costs attributable to S&M |
| **Other** | $[X] | [Specify] |
| **Total S&M Cost** | **$[X]** | Sum of above |

**New customers acquired** (same period): [N]

**CAC = $[Total Cost] ÷ [N customers] = $[CAC per customer]**

### CAC by Channel

Break down CAC by acquisition channel to identify most/least efficient channels.

| Channel | S&M Spend | New Customers | CAC | Notes |
|---------|-----------|---------------|-----|-------|
| Paid Search | $[X] | [N] | $[X/N] | [Google Ads, Bing] |
| Paid Social | $[X] | [N] | $[X/N] | [Facebook, LinkedIn, etc.] |
| Content/SEO | $[X] | [N] | $[X/N] | [Organic, blog, SEO tools] |
| Referral | $[X] | [N] | $[X/N] | [Referral program costs] |
| Direct | $[X] | [N] | $[X/N] | [Type-in, brand awareness] |
| Other | $[X] | [N] | $[X/N] | [Specify] |
| **Total** | **$[X]** | **[N]** | **$[Blended CAC]** | Fully-loaded blended CAC |

**Insight**: [Which channels are most/least efficient? Where to increase/decrease spend?]

---

## LTV Calculation Template

**Lifetime Value (LTV)** = Revenue over customer lifetime × Gross margin %

Choose calculation method based on business model:

### LTV (Subscription Model)

```
LTV = ARPU × Gross Margin % ÷ Monthly Churn Rate
```

**Inputs**:
- **ARPU** (Average Revenue Per User): $[X]/month
- **Gross Margin %**: [X]% (Revenue - COGS) ÷ Revenue
- **Monthly Churn Rate**: [X]% (customers lost ÷ starting customers)

**Calculation**:
- **Customer Lifetime** = 1 ÷ Churn Rate = 1 ÷ [X]% = [Y] months
- **LTV** = $[ARPU] × [Y months] × [Gross Margin %] = **$[LTV]**

### LTV (Transactional Model)

```
LTV = AOV × Purchase Frequency × Gross Margin % × Customer Lifetime (years)
```

**Inputs**:
- **AOV** (Average Order Value): $[X] per transaction
- **Purchase Frequency**: [Y] purchases/year
- **Gross Margin %**: [Z]%
- **Customer Lifetime**: [N] years

**Calculation**:
- **Annual Revenue per Customer** = $[AOV] × [Frequency] = $[X]/year
- **LTV** = $[Annual Revenue] × [Lifetime years] × [Gross Margin %] = **$[LTV]**

### LTV (Marketplace / Platform)

```
LTV = GMV per user × Take Rate × Gross Margin % ÷ Churn Rate
```

**Inputs**:
- **GMV per user** (monthly): $[X]
- **Take Rate**: [Y]% (platform's % of GMV)
- **Gross Margin %**: [Z]% (after variable costs)
- **Monthly Churn Rate**: [C]%

**Calculation**:
- **Monthly Revenue per User** = $[GMV] × [Take Rate] = $[X]/month
- **Customer Lifetime** = 1 ÷ [Churn] = [Y] months
- **LTV** = $[Monthly Rev] × [Lifetime] × [Gross Margin %] = **$[LTV]**

### LTV by Cohort (Observed Retention)

More accurate: Use actual retention data from cohorts.

**Example Cohort Retention Table** (% of customers remaining):

| Month | Cohort Jan | Cohort Feb | Cohort Mar | Average |
|-------|------------|------------|------------|---------|
| 0 | 100% | 100% | 100% | 100% |
| 1 | 95% | 94% | 96% | 95% |
| 2 | 88% | 86% | 89% | 88% |
| 3 | 80% | 78% | 82% | 80% |
| 6 | 65% | 62% | - | 64% |
| 12 | 45% | - | - | 45% |

**LTV Calculation**:
- Sum: Month 0 revenue + (Month 1 retention × revenue) + (Month 2 retention × revenue) + ...
- **LTV** = ARPU × Gross Margin × Σ(retention %) = **$[X]**

---

## Contribution Margin Template

**Contribution Margin %** = (Revenue - Variable Costs) ÷ Revenue

### Revenue & Variable Costs

| Item | Per Unit | Notes |
|------|----------|-------|
| **Revenue** | $[X] | Subscription fee / Sale price / Transaction value |
| **Variable Costs:** | | (costs that scale with each unit) |
| - COGS | $[X] | Product cost, manufacturing |
| - Hosting / Infrastructure | $[X] | Per-user server costs |
| - Payment processing | $[X] | Stripe/PayPal fees (~2-3%) |
| - Support | $[X] | Per-customer support time |
| - Shipping | $[X] | Fulfillment, delivery |
