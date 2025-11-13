# SaaS Market Sizing Example: AI-Powered Email Marketing for E-Commerce

Complete TAM/SAM/SOM calculation for a B2B SaaS startup using bottom-up and top-down methodologies.

## Company Overview

**Product:** AI-powered email marketing automation platform
**Target:** E-commerce companies with $1M+ annual revenue
**Geography:** North America (initial), global expansion planned
**Pricing:** $500/month average (scales by email volume)
**Timeline:** 3-5 year market opportunity

## Methodology 1: Bottom-Up Analysis (Primary)

### Step 1: Define Target Customer Segments

**Segment Criteria:**

- E-commerce companies (D2C and marketplace sellers)
- $1M+ in annual revenue
- North America based
- Currently using email marketing

**Segment Breakdown:**

| Segment               | Annual Revenue | Count  | ACV     | Priority |
| --------------------- | -------------- | ------ | ------- | -------- |
| Small E-commerce      | $1M-$5M        | 85,000 | $3,600  | High     |
| Mid-Market E-commerce | $5M-$50M       | 18,000 | $9,600  | High     |
| Enterprise E-commerce | $50M+          | 2,500  | $24,000 | Medium   |

**Data Sources:**

- U.S. Census Bureau: E-commerce business counts
- Shopify, BigCommerce, WooCommerce: Published merchant counts
- Statista: E-commerce market statistics
- LinkedIn Sales Navigator: Company search validation

### Step 2: Calculate TAM (Total Addressable Market)

**Formula:**

```
TAM = Σ (Segment Count × Annual Contract Value)
```

**Calculation:**

```
Small E-commerce:   85,000 × $3,600  = $306M
Mid-Market:         18,000 × $9,600  = $173M
Enterprise:          2,500 × $24,000 = $60M
                                      --------
TAM (North America):                  $539M
```

**Global Expansion Multiplier:**

- North America = 35% of global e-commerce market
- Global TAM = $539M / 0.35 = $1.54B

**TAM = $1.54B globally, $539M North America**

### Step 3: Calculate SAM (Serviceable Available Market)

**Filters Applied:**

1. **Geographic Filter: North America Only (Year 1-2)**
   - Base TAM: $539M
   - Filter: 100% (starting in North America)
   - Result: $539M

2. **Product Capability Filter: AI-Ready Customers**
   - Customers ready to adopt AI email marketing
   - Excludes: Companies with basic email needs only
   - Filter: 45% (based on survey data)
   - Result: $539M × 0.45 = $242M

3. **Current Tool Filter: Addressable Switching Market**
   - Customers using incumbent tools who would switch
   - Excludes: Recently switched, custom built solutions
   - Filter: 70% (typical B2B SaaS switching market)
   - Result: $242M × 0.70 = $169M

**SAM = $169M**

**SAM Breakdown by Segment:**

```
Small E-commerce:   $306M × 0.45 × 0.70 = $96M (57%)
Mid-Market:         $173M × 0.45 × 0.70 = $54M (32%)
Enterprise:         $60M × 0.45 × 0.70  = $19M (11%)
```

### Step 4: Calculate SOM (Serviceable Obtainable Market)

**Market Share Assumptions:**

**Year 3 Target: 2.5% of SAM**

- Typical new entrant market share
- Requires strong product-market fit
- Assumes $10M in funding for GTM

**Year 5 Target: 5% of SAM**

- Achievable with scale and brand
- Requires effective sales and marketing
- Assumes additional funding for growth

**Calculation:**

```
SOM (Year 3) = $169M × 2.5% = $4.2M ARR
SOM (Year 5) = $169M × 5.0% = $8.5M ARR
```

**SOM by Segment (Year 5):**

```
Small E-commerce:   $96M × 5% = $4.8M ARR (565 customers)
Mid-Market:         $54M × 5% = $2.7M ARR (281 customers)
Enterprise:         $19M × 5% = $1.0M ARR (42 customers)
                                --------
Total:                          $8.5M ARR (888 customers)
```

### Bottom-Up Summary

| Metric           | North America | Notes                                  |
| ---------------- | ------------- | -------------------------------------- |
| **TAM**          | $539M         | All e-commerce $1M+ revenue            |
| **SAM**          | $169M         | AI-ready, addressable switching market |
| **SOM (Year 3)** | $4.2M         | 2.5% market share, 495 customers       |
| **SOM (Year 5)** | $8.5M         | 5% market share, 888 customers         |

## Methodology 2: Top-Down Analysis (Validation)

### Step 1: Identify Total Market Category

**Market Category:** Email Marketing Software
**Source:** Gartner Market Share Report (2024)

**Global Email Marketing Software Market:**

- Market Size: $7.5B (2024)
- Growth Rate: 12% CAGR
- Geography: Worldwide

**Data Source:** Gartner, "Market Share: Email Marketing Software, Worldwide, 2024"

### Step 2: Apply Geographic Filter

**North America Market Share:**

- North America = 40% of global software spending
- Email Marketing NA = $7.5B × 0.40 = $3.0B

### Step 3: Apply Segment Filters

**E-Commerce Focus:**

- E-commerce email marketing = 25% of total email marketing
- E-commerce segment = $3.0B × 0.25 = $750M

**$1M+ Revenue Filter:**

- Companies with $1M+ revenue = 65% of e-commerce market
- TAM = $750M × 0.65 = $488M

**AI-Powered Subset:**

- AI-powered email marketing = 35% of market (growing rapidly)
- SAM = $488M × 0.35 = $171M

### Top-Down Summary

| Metric  | Amount | Calculation                        |
| ------- | ------ | ---------------------------------- |
| **TAM** | $488M  | NA e-commerce email marketing $1M+ |
| **SAM** | $171M  | AI-powered subset                  |

## Triangulation and Validation

### Comparing Methodologies

| Metric  | Bottom-Up | Top-Down | Variance |
| ------- | --------- | -------- | -------- |
| **TAM** | $539M     | $488M    | +10%     |
| **SAM** | $169M     | $171M    | -1%      |

**Validation Result:** ✅ Excellent alignment (< 2% variance on SAM)

**Why alignment matters:**

- Bottom-up and top-down within 10% gives high confidence
- SAM alignment of 1% is exceptional
- Use bottom-up as primary (more granular)
- Reference top-down for validation

### Public Company Validation

**Klaviyo (Public, KVYO):**

- 2024 Revenue: ~$700M
- Focus: E-commerce email/SMS marketing
- Market Share: ~46% of our SAM
- Validates large e-commerce email market exists

**Mailchimp (Intuit-owned):**

- 2024 Revenue: ~$800M (estimated)
- Broader focus, includes SMBs
- Significant e-commerce customer base

**Validation:** Market leaders have $700M-$800M revenue, supporting $1.5B+ global TAM

### Sanity Checks

**Customer Count Check:**
✅ 888 customers at Year 5 (5% market share) = reasonable
✅ Implies ~14,000 total addressable customers
✅ Aligns with estimated 105,000 e-commerce cos $1M+ in NA

**Average Revenue Check:**
✅ $8.5M ARR / 888 customers = $9,571 ACV
✅ Within expected range of $3.6K-$24K by segment
✅ Weighted average makes sense given segment mix

**Market Share Check:**
✅ 5% market share in Year 5 is achievable for well-funded startup
✅ Lower than Klaviyo (46%), appropriate for new entrant
✅ Room for growth beyond Year 5

## Growth Projections

### Market Growth Assumptions

**Email Marketing Market CAGR: 12%**

- Source: Gartner market forecast
- Drivers: E-commerce growth, marketing automation adoption

**AI Subset Growth: 25% CAGR**

- Higher than overall market
- AI adoption accelerating in marketing
- More companies seeking AI-powered tools

### SAM Evolution (5-Year Forecast)

| Year | SAM   | Growth | Notes                      |
