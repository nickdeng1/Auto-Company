#!/usr/bin/env python3
"""
Source Credibility Evaluator
Assesses source quality, credibility, and potential biases
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
import re


@dataclass
class CredibilityScore:
    """Represents source credibility assessment"""
    overall_score: float  # 0-100
    domain_authority: float  # 0-100
    recency: float  # 0-100
    expertise: float  # 0-100
    bias_score: float  # 0-100 (higher = more neutral)
    factors: Dict[str, str]
    recommendation: str  # "high_trust", "moderate_trust", "low_trust", "verify"


class SourceEvaluator:
    """Evaluates source credibility and quality"""

    # Domain reputation tiers
    HIGH_AUTHORITY_DOMAINS = {
        # Academic & Research
        'arxiv.org', 'nature.com', 'science.org', 'cell.com', 'nejm.org',
        'thelancet.com', 'springer.com', 'sciencedirect.com', 'plos.org',
        'ieee.org', 'acm.org', 'pubmed.ncbi.nlm.nih.gov',

        # Government & International Organizations
        'nih.gov', 'cdc.gov', 'who.int', 'fda.gov', 'nasa.gov',
        'gov.uk', 'europa.eu', 'un.org',

        # Established Tech Documentation
        'docs.python.org', 'developer.mozilla.org', 'docs.microsoft.com',
        'cloud.google.com', 'aws.amazon.com', 'kubernetes.io',

        # Reputable News (Fact-check verified)
        'reuters.com', 'apnews.com', 'bbc.com', 'economist.com',
        'nature.com/news', 'scientificamerican.com'
    }

    MODERATE_AUTHORITY_DOMAINS = {
        # Tech News & Analysis
        'techcrunch.com', 'theverge.com', 'arstechnica.com', 'wired.com',
        'zdnet.com', 'cnet.com',

        # Industry Publications
        'forbes.com', 'bloomberg.com', 'wsj.com', 'ft.com',

        # Educational
        'wikipedia.org', 'britannica.com', 'khanacademy.org',

        # Tech Blogs (established)
        'medium.com', 'dev.to', 'stackoverflow.com', 'github.com'
    }

    LOW_AUTHORITY_INDICATORS = [
        'blogspot.com', 'wordpress.com', 'wix.com', 'substack.com'
    ]

    def __init__(self):
        pass

    def evaluate_source(
        self,
        url: str,
        title: str,
        content: Optional[str] = None,
        publication_date: Optional[str] = None,
        author: Optional[str] = None
    ) -> CredibilityScore:
        """Evaluate source credibility"""

        domain = self._extract_domain(url)

        # Calculate component scores
        domain_score = self._evaluate_domain_authority(domain)
        recency_score = self._evaluate_recency(publication_date)
        expertise_score = self._evaluate_expertise(domain, title, author)
        bias_score = self._evaluate_bias(domain, title, content)

        # Calculate overall score (weighted average)
        overall = (
            domain_score * 0.35 +
            recency_score * 0.20 +
            expertise_score * 0.25 +
            bias_score * 0.20
        )

        # Determine factors
        factors = self._identify_factors(
            domain, domain_score, recency_score, expertise_score, bias_score
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(overall)

        return CredibilityScore(
            overall_score=round(overall, 2),
            domain_authority=round(domain_score, 2),
            recency=round(recency_score, 2),
            expertise=round(expertise_score, 2),
            bias_score=round(bias_score, 2),
            factors=factors,
            recommendation=recommendation
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www prefix
        domain = domain.replace('www.', '')
        return domain

    def _evaluate_domain_authority(self, domain: str) -> float:
        """Evaluate domain authority (0-100)"""
        if domain in self.HIGH_AUTHORITY_DOMAINS:
            return 90.0
        elif domain in self.MODERATE_AUTHORITY_DOMAINS:
            return 70.0
        elif any(indicator in domain for indicator in self.LOW_AUTHORITY_INDICATORS):
            return 40.0
        else:
            # Unknown domain - moderate skepticism
            return 55.0

    def _evaluate_recency(self, publication_date: Optional[str]) -> float:
        """Evaluate information recency (0-100)"""
        if not publication_date:
            return 50.0  # Unknown date

        try:
            pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            age = datetime.now() - pub_date

            # Recency scoring
            if age < timedelta(days=90):  # < 3 months
                return 100.0
