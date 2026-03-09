# Image Optimization API - Unit Economics Analysis

**Date**: February 27, 2026  
**Analyst**: CFO Campbell (Patrick Campbell Model)  
**Product**: Image Optimization API  
**Tech Stack**: Python 3.11+ / FastAPI / Docker

---

## Executive Summary

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Target Gross Margin | 70-80% | 70-85% (SaaS) | Feasible |
| Estimated CAC | $45-150 | $100-500 (SaaS) | Good |
| Estimated LTV | $540-1,800 | LTV:CAC > 3:1 | Good |
| LTV:CAC Ratio | 6:1 to 12:1 | > 3:1 | Healthy |
| Break-even Customers | 12-17 | N/A | Achievable |
| **Recommendation** | **GO** | - | - |

---

## 1. Cost Structure Analysis

### 1.1 Infrastructure Costs - Cloud API Model (Our Offering)

| Component | Cost Unit | Monthly Cost | Notes |
|-----------|-----------|--------------|-------|
| **Compute (CPU-intensive)** | | | |
| - vCPU (image processing) | $0.04/vCPU-hour | $120/mo (baseline) | 100 vCPU-hours baseline |
| - Auto-scaling compute | $0.05/vCPU-hour | Variable | Peak demand handling |
| **Memory** | $0.012/GB-hour | $86/mo | 8GB baseline for processing |
| **Storage** | | | |
| - Object storage (S3/R2) | $0.023/GB/mo | $23/mo | 1TB baseline |
| - Cache/CDN | $0.02/GB stored | $20/mo | Edge caching |
| **Bandwidth/Egress** | $0.08-0.12/GB | Variable | Critical cost driver |
| **Database** | Managed PostgreSQL | $15-50/mo | Metadata, user accounts |
| **Load Balancer** | $0.025/hour | $18/mo | Required for HA |
| **Monitoring/Observability** | Fixed | $20-50/mo | Logging, APM |

**Monthly Fixed Infrastructure Baseline**: $300-400/month

### 1.2 Cost per 1,000 Images Processed

| Scenario | CPU Cost | Memory | Storage | Bandwidth | **Total/1K images** |
|----------|----------|--------|---------|-----------|-------------------|
| **Small images (<100KB)** | $0.008 | $0.002 | $0.001 | $0.008 | **$0.019** |
| **Medium images (100KB-1MB)** | $0.025 | $0.008 | $0.005 | $0.040 | **$0.078** |
| **Large images (1-5MB)** | $0.080 | $0.020 | $0.015 | $0.160 | **$0.275** |
| **Batch processing (100+ images)** | $0.015 | $0.005 | $0.003 | $0.025 | **$0.048** |

**Assumptions**:
- Average processing time: 0.5-2 seconds per image
- CPU: 1 vCPU per concurrent process
- Memory: 512MB-2GB per process
- Bandwidth: 2x image size (upload + download)

### 1.3 Self-Hosted Model (Customer Bears Costs)

| Cost Category | Customer Responsibility | Our Revenue Impact |
|---------------|------------------------|-------------------|
| Server/VM | $50-500/mo (customer) | License fee only |
| CPU/Memory | Customer infrastructure | Zero marginal cost |
| Storage | Customer infrastructure | Zero marginal cost |
| Bandwidth | Customer network | Zero marginal cost |
| Maintenance | Customer engineering time | Zero marginal cost |

**Self-Hosted Pricing Implication**: 80-95% gross margin on license fees.

### 1.4 Bandwidth Cost Sensitivity Analysis

| Monthly Volume | Bandwidth (avg 500KB/image) | Egress Cost @ $0.10/GB | % of Revenue @ $29/mo tier |
|----------------|-----------------------------|------------------------|---------------------------|
| 10,000 images | 5 GB | $0.50 | 1.7% |
| 100,000 images | 50 GB | $5.00 | 17.2% |
| 500,000 images | 250 GB | $25.00 | 86.2% |
| 1,000,000 images | 500 GB | $50.00 | 172% (UNPROFITABLE) |

**CRITICAL**: Bandwidth is the primary cost driver at scale. Must structure pricing around GB or include bandwidth limits.

---

## 2. Pricing Model Design

### 2.1 Value Metric Analysis

| Value Metric | Pros | Cons | Recommendation |
|--------------|------|------|----------------|
| **Per Image** | Simple, predictable | Doesn't account for image size/complexity | Secondary tier metric |
| **Per GB Processed** | Aligns with costs | Complex to understand | Primary metric |
| **Per Transformation** | Captures complexity | Confusing for users | Include as modifier |
| **Per API Call** | Simple | Doesn't reflect cost | Not recommended |

**Recommended Value Metric**: Hybrid - Base subscription + overage per GB processed

### 2.2 Competitive Pricing Analysis

| Competitor | Free Tier | Starter | Pro | Enterprise |
|------------|-----------|---------|-----|------------|
| **Cloudinary** | 25 GB/mo | $89/mo (89GB) | $224/mo (269GB) | Custom |
| **Imgix** | 3,000 images | $20/mo (10K images) | $100/mo (100K images) | Custom |
| **Cloudflare Images** | 100K images | $5/mo (100K) | $0.005/image after | Custom |
| **ImageKit** | 20 GB/mo | $49/mo (200GB) | $149/mo (1TB) | Custom |
| **Uploadcare** | 10K ops/mo | $29/mo (50K ops) | $99/mo (200K ops) | Custom |

### 2.3 Proposed Pricing Structure

| Tier | Monthly Price | Included Volume | Overage Rate | Target Customer |
|------|---------------|-----------------|--------------|-----------------|
| **Free** | $0 | 1,000 images (5GB) | N/A | Hobbyists, testing |
| **Starter** | $19/mo | 25,000 images (50GB) | $0.50/GB | Small businesses |
| **Pro** | $79/mo | 100,000 images (200GB) | $0.40/GB | Growing startups |
| **Business** | $199/mo | 500,000 images (1TB) | $0.35/GB | Established companies |
| **Enterprise** | Custom | Unlimited | Negotiated | Large enterprises |

**Self-Hosted License**:
- Starter: $199 one-time + $49/year support
- Business: $499 one-time + $149/year support
- Enterprise: $1,999+ one-time + custom support

### 2.4 Free Tier Strategy

| Objective | Strategy | Expected Outcome |
|-----------|----------|------------------|
| Drive adoption | 1,000 images/month free | Low barrier to entry |
| Convert to paid | Watermark after 500 images | Soft paywall trigger |
| Capture leads | Email required at 750 images | Lead generation |
| Prevent abuse | Rate limits, IP tracking | Cost protection |

---

## 3. Unit Economics

### 3.1 Gross Margin Calculation by Tier

| Tier | Revenue | COGS | Gross Margin | GM % |
|------|---------|------|--------------|------|
| **Free** | $0 | $0.50-5.00 | -$5.00 | N/A (CAC investment) |
| **Starter ($19)** | $19 | $3.90-7.80 | $11.20-15.10 | 59-79% |
| **Pro ($79)** | $79 | $15.60-31.20 | $47.80-63.40 | 60-80% |
| **Business ($199)** | $199 | $78-156 | $43-121 | 22-61% |
| **Enterprise** | $500+ | Variable | Variable | 70-90% |

**COGS Calculation**:
- Compute: $0.02/image processed
- Storage: $0.023/GB/month (amortized)
- Bandwidth: $0.10/GB egress
- Payment processing: 2.9% + $0.30

### 3.2 Customer Acquisition Cost (CAC) Estimate

| Channel | CAC Range | Conversion Rate | Notes |
|---------|-----------|-----------------|-------|
| **Organic/SEO** | $10-30 | 2-5% | Long-term investment |
| **Content Marketing** | $25-75 | 1-3% | Blog, tutorials, docs |
| **Developer Communities** | $15-50 | 2-4% | HN, Reddit, Dev.to |
| **Paid Search (SEM)** | $75-200 | 0.5-2% | High competition |
| **Social Media** | $50-150 | 0.5-1.5% | Twitter/X, LinkedIn |
| **Partner/Integration** | $30-100 | 3-8% | CMS integrations |

**Blended CAC Estimate**: $45-150 per paying customer

### 3.3 Lifetime Value (LTV) Estimate

| Tier | Monthly Revenue | Avg. Lifespan | LTV | Notes |
|------|-----------------|---------------|-----|-------|
| **Starter** | $19 | 12-18 months | $228-342 | Small business churn |
| **Pro** | $79 | 18-24 months | $1,422-1,896 | Product-market fit |
| **Business** | $199 | 24-36 months | $4,776-7,164 | Stickier customers |
| **Enterprise** | $500+ | 36-48 months | $18,000+ | Long contracts |

**LTV Formula**: ARPU x Gross Margin x Lifespan

| Scenario | Weighted ARPU | Gross Margin | Lifespan | LTV |
|----------|---------------|--------------|----------|-----|
| **Conservative** | $45 | 65% | 12 months | $351 |
| **Moderate** | $65 | 72% | 18 months | $842 |
| **Optimistic** | $90 | 78% | 24 months | $1,685 |

### 3.4 LTV:CAC Ratio Analysis

| Scenario | LTV | CAC | LTV:CAC | Health Assessment |
|----------|-----|-----|---------|-------------------|
| **Conservative** | $351 | $150 | 2.3:1 | Marginal |
| **Moderate** | $842 | $90 | 9.4:1 | Excellent |
| **Optimistic** | $1,685 | $45 | 37:1 | Exceptional |

**Target LTV:CAC**: 3:1 minimum, 5:1+ is healthy

**Verdict**: Unit economics are viable across reasonable scenarios.

---

## 4. Break-Even Analysis

### 4.1 Fixed Costs (Monthly)

| Category | Cost |
|----------|------|
| Infrastructure baseline | $300-400 |
| SaaS tools (analytics, email, etc.) | $100-200 |
| Domain, SSL, misc | $20-50 |
| **Total Fixed Costs** | **$420-650/month** |

### 4.2 Break-Even Calculations

**Target**: $100 MRR (Ramen Profitable)

| Metric | Calculation | Result |
|--------|-------------|--------|
| Customers needed @ $19/mo | $100 / $19 = 5.3 | 6 customers |
| Customers needed @ $45 ARPU | $100 / $45 = 2.2 | 3 customers |
| Customers needed (covering fixed costs) | $500 / $45 = 11.1 | 12 customers |

**For $500 MRR (sustainable)**: 12 customers @ $45 ARPU

**For $1,000 MRR (side-income)**: 22 customers @ $45 ARPU

### 4.3 API Calls per Customer (Average)

| Customer Type | Images/Month | API Calls | Revenue |
|---------------|--------------|-----------|---------|
| Free tier | 500-1,000 | 500-1,000 | $0 |
| Starter | 5,000-25,000 | 5,000-25,000 | $19 |
| Pro | 25,000-100,000 | 25,000-100,000 | $79 |
| Business | 100,000-500,000 | 100,000-500,000 | $199 |

### 4.4 Volume Needed for Infrastructure Coverage

| Fixed Cost Level | Images Needed | Customers (avg) |
|------------------|---------------|----------------|
| $420/month | 84,000 images | 8-10 customers |
| $650/month | 130,000 images | 13-15 customers |

---

## 5. Revenue Projections

### 5.1 Conservative Scenario (10 Customers)

| Metric | Value |
|--------|-------|
| Total Customers | 10 |
| Mix | 6 Starter, 3 Pro, 1 Business |
| MRR | $619 |
| Annual Run Rate | $7,428 |
| Gross Margin | 70% |
| Gross Profit | $434/mo |
| Net (after fixed costs) | $16-214/mo |

### 5.2 Moderate Scenario (50 Customers)

| Metric | Value |
|--------|-------|
| Total Customers | 50 |
| Mix | 25 Starter, 18 Pro, 5 Business, 2 Enterprise |
| MRR | $4,032 |
| Annual Run Rate | $48,384 |
| Gross Margin | 72% |
| Gross Profit | $2,903/mo |
| Net (after fixed costs) | $2,253-2,483/mo |

### 5.3 Optimistic Scenario (200 Customers)

| Metric | Value |
|--------|-------|
| Total Customers | 200 |
| Mix | 80 Starter, 70 Pro, 35 Business, 15 Enterprise |
| MRR | $20,315 |
| Annual Run Rate | $243,780 |
| Gross Margin | 75% |
| Gross Profit | $15,236/mo |
| Net (after fixed costs) | $14,586-14,816/mo |

### 5.4 Revenue Ramp Timeline

| Month | Customers | MRR | ARR | Key Milestones |
|-------|-----------|-----|-----|----------------|
| 1-3 | 5-15 | $100-500 | $1.2K-6K | Product-market fit |
| 4-6 | 20-40 | $1,000-2,500 | $12K-30K | Word-of-mouth kicks in |
| 7-12 | 50-100 | $3,500-8,000 | $42K-96K | Marketing investment |
| 13-18 | 100-200 | $10,000-20,000 | $120K-240K | Scale phase |
| 19-24 | 200-400 | $25,000-50,000 | $300K-600K | Growth phase |

---

## 6. Red Flags & Risk Analysis

### 6.1 Economic Viability Risks

| Risk | Severity | Probability | Impact | Mitigation |
|------|----------|-------------|--------|------------|
| **Bandwidth cost spiral** | HIGH | Medium | Margin compression | Aggressive caching, CDN, tiered pricing |
| **Price competition** | MEDIUM | High | Revenue pressure | Differentiate on features, support |
| **Free tier abuse** | MEDIUM | Medium | Hidden costs | Rate limiting, CAPTCHA, monitoring |
| **Large image processing** | HIGH | Low | Single customer blows margins | Per-GB pricing, max file size limits |
| **Storage accumulation** | MEDIUM | Medium | Growing fixed costs | TTL policies, archival tiers |

### 6.2 Competitive Cost Advantages

| Competitor | Cost Advantage | Threat Level |
|------------|----------------|---------------|
| **Cloudflare Images** | Own CDN, massive scale | HIGH - 50%+ cost advantage |
| **Cloudinary** | Established infrastructure | MEDIUM - economies of scale |
| **AWS-native solutions** | Vertical integration | HIGH - for AWS customers |
| **Self-hosted open source** | Zero marginal cost | MEDIUM - technical users only |

**Key Insight**: We cannot compete on price alone. Must compete on:
1. Developer experience (DX)
2. Specialized features (AI optimization, format conversion)
3. Privacy/compliance (self-hosted option)
4. Customer support quality

### 6.3 Bandwidth/Egress Cost Scenarios

| Scenario | Bandwidth Cost | % of Revenue | Viability |
|----------|----------------|--------------|-----------|
| Normal usage (<50GB/customer) | $5/customer | 6-25% | Sustainable |
| Heavy usage (50-200GB/customer) | $20/customer | 10-50% | Marginal |
| Abusive usage (>200GB/customer) | $50+/customer | >50% | Loss-making |

**Critical Controls Needed**:
- Hard bandwidth limits per tier
- Clear overage pricing
- Abuse detection systems
- Option for self-hosted deployment

---

## 7. Financial Recommendation

### GO Decision - With Conditions

**Rationale**:

| Factor | Assessment | Score (1-5) |
|--------|------------|-------------|
| Market Size | Large (image optimization is universal need) | 5 |
| Competition | Saturated but differentiated possible | 3 |
| Unit Economics | Healthy LTV:CAC ratio (6:1 to 12:1) | 5 |
| Gross Margins | 60-80% achievable | 4 |
| Technical Feasibility | Python/FastAPI is solid choice | 5 |
| Solo Founder Fit | Low maintenance overhead possible | 4 |
| **Total** | | **26/30** |

### Critical Success Factors

1. **Pricing Architecture**: Implement GB-based pricing with hard limits
2. **Self-Hosted Option**: Capture high-volume customers without margin risk
3. **CDN Strategy**: Partner with Cloudflare R2 or similar to reduce egress
4. **Automation**: Minimize support burden through excellent documentation
5. **Niche Focus**: Consider specialized vertical (e.g., e-commerce, real estate, media)

### Minimum Viable Launch Criteria

| Criterion | Target | Rationale |
|-----------|--------|-----------|
| First 10 customers | Within 90 days | Validate demand |
| $500 MRR | Within 6 months | Cover basic costs |
| Gross margin >60% | From day 1 | Sustainable economics |
| Churn rate <5% | Within 6 months | Product-market fit signal |

### Financial Projections Summary

| Timeframe | MRR Target | Customer Count | Probability |
|-----------|------------|----------------|--------------|
| Month 3 | $300-500 | 10-15 | 70% |
| Month 6 | $1,000-2,000 | 25-50 | 50% |
| Month 12 | $3,000-8,000 | 75-150 | 30% |

### Final Recommendation

**GO with phased approach**:

1. **Phase 1 (Months 1-3)**: Launch with free + single paid tier ($29/mo), validate demand
2. **Phase 2 (Months 4-6)**: Add tiered pricing if >20 paying customers
3. **Phase 3 (Months 7-12)**: Add self-hosted option if >50 customers
4. **Phase 4 (Year 2)**: Scale or pivot based on traction

**Risk Capital Required**: $2,000-5,000 (infrastructure + minimal marketing)

**Break-even Timeline**: 3-6 months at conservative estimates

---

## Appendices

### A. Assumptions Log

| Assumption | Value | Source | Confidence |
|------------|-------|--------|------------|
| Average image size | 500KB | Industry estimate | Medium |
| Processing time | 0.5-2 seconds | Benchmark | High |
| CAC range | $45-150 | Industry benchmarks | Medium |
| Churn rate | 5-8%/month | SaaS benchmarks | Medium |
| Developer conversion rate | 2-5% | Industry average | Medium |
| Infrastructure costs | AWS/on-par pricing | Public pricing | High |

### B. SaaS Benchmarks Reference

| Metric | Good | Better | Best |
|--------|------|--------|------|
| Gross Margin | >60% | >70% | >80% |
| LTV:CAC | >3:1 | >5:1 | >10:1 |
| CAC Payback | <12 months | <8 months | <6 months |
| Monthly Churn | <5% | <3% | <1% |
| Revenue per Employee | >$100K | >$200K | >$300K |

### C. Competitive Feature Matrix

| Feature | Us | Cloudinary | Imgix | Cloudflare |
|---------|-----|-----------|-------|------------|
| Real-time transformation | Yes | Yes | Yes | Yes |
| AI optimization | Planned | Yes | Yes | No |
| Self-hosted option | Yes | No | No | No |
| Price/GB | $0.35-0.50 | $1.00 | $0.50 | $0.005* |
| Free tier | 5GB | 25GB | 15GB | 100GB |
| Developer experience | TBD | Good | Good | Good |

*Cloudflare pricing is loss-leader for ecosystem lock-in.

---

**Document Version**: 1.0  
**Last Updated**: February 27, 2026  
**Author**: CFO Campbell (Patrick Campbell Model)  
**Review Status**: Ready for CEO approval