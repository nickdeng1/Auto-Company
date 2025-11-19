---
name: user-persona-creation
description: Create detailed user personas based on research and data. Develop realistic representations of target users to guide product decisions and ensure user-centered design.
---

# User Persona Creation

## Overview

User personas synthesize research into realistic user profiles that guide design, development, and marketing decisions.

## When to Use

- Starting product design
- Feature prioritization
- Marketing messaging
- User research synthesis
- Team alignment on users
- Journey mapping
- Success metrics definition

## Instructions

### 1. **Research & Data Collection**

```python
# Gather data for persona development

class PersonaResearch:
    def conduct_interviews(self, target_sample_size=12):
        """Interview target users"""
        interview_guide = {
            'demographics': [
                'Age, gender, location',
                'Job title, industry, company size',
                'Experience level, education',
                'Salary range, purchasing power'
            ],
            'goals': [
                'What are you trying to achieve?',
                'What's most important to you?',
                'What does success look like?'
            ],
            'pain_points': [
                'What frustrates you about current solutions?',
                'What takes too long or is complicated?',
                'What prevents you from achieving goals?'
            ],
            'behaviors': [
                'How do you currently solve this problem?',
                'What tools do you use?',
                'How do you learn about new solutions?'
            ],
            'preferences': [
                'How do you prefer to communicate?',
                'What communication channels do you use?',
                'When are you most responsive?'
            ]
        }

        return {
            'sample_size': target_sample_size,
            'interview_guide': interview_guide,
            'output': 'Interview transcripts, notes, recordings'
        }

    def analyze_survey_data(self, survey_data):
        """Synthesize survey responses"""
        return {
            'demographics': self.segment_demographics(survey_data),
            'pain_points': self.extract_pain_points(survey_data),
            'goals': self.identify_goals(survey_data),
            'needs': self.map_needs(survey_data),
            'frequency_distribution': self.calculate_frequencies(survey_data)
        }

    def analyze_user_data(self):
        """Use product analytics data"""
        return {
            'feature_usage': 'Which features are most used',
            'user_segments': 'Behavioral groupings',
            'conversion_paths': 'How users achieve goals',
            'churn_patterns': 'Why users leave',
            'usage_frequency': 'Active vs inactive users'
        }

    def synthesize_data(self, interview_data, survey_data, usage_data):
        """Combine all data sources"""
        return {
            'primary_personas': self.identify_primary_personas(interview_data),
            'secondary_personas': self.identify_secondary_personas(survey_data),
            'persona_groups': self.cluster_similar_users(usage_data),
            'confidence_level': 'Based on data sources and sample size'
        }
```

### 2. **Persona Template**

```yaml
User Persona: Premium SaaS Buyer

---

## Demographics

Name: Sarah Chen
Age: 34
Location: San Francisco, CA
Job Title: VP Product Management
Company: Series B SaaS startup (50 employees)
Experience: 8 years in product management
Education: MBA from Stanford, BS in Computer Science
Income: $180K salary + 0.5% equity

---

## Professional Context

Industry: B2B SaaS (Project Management)
Company Size: 50-200 employees
Budget Authority: Can approve purchases up to $50K
Buying Process: 60% solo decisions, 40% committee
Evaluation Time: 4-6 weeks average

---

## Goals & Motivations

Primary Goals:
  1. Improve team productivity by 25%
  2. Reduce project delivery time by 30%
  3. Increase visibility into project status
  4. Improve team collaboration across remote locations

Success Definition:
  - Team using tool daily
  - 20% reduction in status meetings
  - Faster decision-making
  - Higher team satisfaction

---

## Pain Points

Current Challenges:
  - Existing tool is slow and outdated
  - Poor mobile experience
  - Limited reporting capabilities
  - Difficult to customize for company needs
  - Vendor is unresponsive to feature requests

Frustrations:
  - Wasting time in status update meetings
  - Lack of real-time visibility into project health
  - Can't easily identify bottlenecks
  - Integration with other tools is difficult

---

## Behaviors & Preferences

Daily Tools:
  - Slack: Constant communication
  - Google Workspace: Document collaboration
  - Jira: Technical work tracking
  - Spreadsheets: Status reporting (workaround)

Work Patterns:
  - Typically works 8am-6pm Pacific
  - Checks email every 15 minutes
  - In meetings 50% of day
  - Works 20% of time outside office hours

Information Gathering:
  - Reads G2/Capterra reviews: High trust
  - Asks for peer recommendations: Very influential
  - Requests demos: Hands-on evaluation
  - Wants to see case studies: Similar companies

Decision Drivers:
  - ROI and measurable impact: 40%
  - User adoption potential: 30%
  - Ease of implementation: 20%
  - Price: 10%

---

## Technology Comfort

Tech Savviness: High (uses 15+ tools daily)
Mobile Usage: 40% of work on mobile
Prefers: Intuitive UI, minimal training
Adoption Speed: Fast (new tools in 1-2 weeks)
Integration Importance: Very high

---

## Customer Journey

Awareness: Product recommendations from peers
Consideration: Reviews, demos, talk to customers
Decision: Cost-benefit analysis, team input
Onboarding: Expects self-service + minimal support
Ongoing: Wants regular feature updates, responsive support

---

## Communication Preferences

Prefers: Email and Slack (avoid calls)
Response Time: 4-24 hours typical
Best Time: Tuesday-Thursday mornings
Frequency: Weekly updates during evaluation
Format: Data-driven, executive summaries preferred

---

## Key Quotes

"I need something that my team will actually use, not something
I have to force them to adopt."

"Show me the data on time savings, not just promises."

"Our tool should work as hard as we do - seamlessly across
all our devices and workflows."

---

## Persona Importance

Primary Persona: YES (key decision maker)
Frequency in User Base: 35% of customers
Influence: High (recommends to peers)
Revenue Impact: $30K ARR average

---

## Marketing & Sales Strategy

Messaging:
  - Emphasize productivity gains and ROI
  - Highlight ease of adoption
  - Show mobile-first experience
  - Demonstrate integrations

Sales Approach:
  - Provide customer references (similar companies)
  - Offer flexible demo (self-service + guided)
  - Focus on time-to-value
  - Provide ROI calculator

Success Metrics:
  - 50% adoption within 2 months
  - Net Promoter Score >50
  - Upsell to higher tier within 6 months
```

### 3. **Multiple Personas**

```javascript
// Create persona set for comprehensive coverage

class PersonaFramework {
  createPersonaSet(research_data) {
    return {
      primary_personas: [
        {
          name: 'Sarah (VP Product)',
          percentage: '35%',
          influence: 'High',
          role: 'Decision maker'
        },
        {
          name: 'Mike (Team Lead)',
          percentage: '40%',
          influence: 'High',
          role: 'Daily user, key influencer'
        },
        {
          name: 'Lisa (Admin)',
          percentage: '25%',
          influence: 'Medium',
          role: 'Setup and management'
        }
      ],
      secondary_personas: [
        {
          name: 'John (Executive)',
          percentage: '10%',
