#!/usr/bin/env python3
"""Generate simulated audit reports for the GraphRAG corpus.

Creates 50 realistic internal audit reports for Brazilian financial
institutions, covering 8 areas with varying severities and regulatory
references. Uses Claude API (Haiku) for generation.

Usage:
    # Generate all 50 reports
    python generate_audit_reports.py --output-dir implementacao/data/audit_reports/

    # Generate a subset for testing
    python generate_audit_reports.py --count 5 --output-dir /tmp/test_audit

    # Dry run (show plan without generating)
    python generate_audit_reports.py --dry-run

    # Generate with template only (no API calls)
    python generate_audit_reports.py --template-only --output-dir /tmp/test_audit
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Distribution of 50 audit reports across areas
REPORT_CONFIGS = [
    # Capital Adequacy (8 reports)
    {"area": "capital_adequacy", "topic": "CET1 Ratio Compliance", "regulations": ["Basel III Pillar 1", "BCB Resolucao 4.193"], "severity_mix": ["High", "Medium", "Medium"]},
    {"area": "capital_adequacy", "topic": "Leverage Ratio Assessment", "regulations": ["Basel III Leverage Framework", "BCBS d424"], "severity_mix": ["Medium", "Low"]},
    {"area": "capital_adequacy", "topic": "Stress Testing Framework", "regulations": ["Basel III Pillar 2", "BCB Circular 3.846"], "severity_mix": ["Critical", "High", "Medium"]},
    {"area": "capital_adequacy", "topic": "Capital Buffer Requirements", "regulations": ["Basel III CCoB", "D-SIB buffer"], "severity_mix": ["Medium", "Medium", "Low"]},
    {"area": "capital_adequacy", "topic": "RWA Calculation Accuracy", "regulations": ["Basel III SA-CR", "BCB Circular 3.644"], "severity_mix": ["High", "Medium"]},
    {"area": "capital_adequacy", "topic": "ICAAP Review", "regulations": ["Basel III Pillar 2", "BCB Resolucao 4.557"], "severity_mix": ["Medium", "Low", "Low"]},
    {"area": "capital_adequacy", "topic": "Capital Planning Process", "regulations": ["Basel III", "CMN Resolucao 4.966"], "severity_mix": ["High", "Medium"]},
    {"area": "capital_adequacy", "topic": "Countercyclical Buffer Assessment", "regulations": ["Basel III CCyB", "BCB Comunicado 33.040"], "severity_mix": ["Low", "Low"]},

    # Credit Risk (8 reports)
    {"area": "credit_risk", "topic": "PD/LGD Model Validation", "regulations": ["Basel III IRB", "BCB Circular 3.648"], "severity_mix": ["High", "High", "Medium"]},
    {"area": "credit_risk", "topic": "Provisioning Adequacy (IFRS 9)", "regulations": ["CMN Resolucao 4.966", "IFRS 9 ECL"], "severity_mix": ["Critical", "High"]},
    {"area": "credit_risk", "topic": "Credit Portfolio Quality Review", "regulations": ["BCB Resolucao 2.682", "Basel III SA-CR"], "severity_mix": ["Medium", "Medium", "Low"]},
    {"area": "credit_risk", "topic": "Concentration Risk Management", "regulations": ["Basel III Pillar 2", "BCB Resolucao 4.557"], "severity_mix": ["High", "Medium"]},
    {"area": "credit_risk", "topic": "Collateral Valuation Process", "regulations": ["Basel III CRM", "BCB Circular 3.644"], "severity_mix": ["Medium", "Low"]},
    {"area": "credit_risk", "topic": "Counterparty Credit Risk (CVA)", "regulations": ["Basel III CVA", "BCBS d325"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "credit_risk", "topic": "Credit Risk Appetite Framework", "regulations": ["Basel III Pillar 2", "BCB Resolucao 4.557"], "severity_mix": ["Medium", "Low"]},
    {"area": "credit_risk", "topic": "Large Exposure Monitoring", "regulations": ["BCBS Large Exposures", "BCB Resolucao 4.677"], "severity_mix": ["High", "Medium"]},

    # Market Risk (5 reports)
    {"area": "market_risk", "topic": "VaR Backtesting Results", "regulations": ["Basel III FRTB", "BCB Circular 3.646"], "severity_mix": ["High", "Medium"]},
    {"area": "market_risk", "topic": "FRTB Readiness Assessment", "regulations": ["BCBS d457", "Basel III Market Risk"], "severity_mix": ["Critical", "High", "Medium"]},
    {"area": "market_risk", "topic": "Trading Book Boundary Review", "regulations": ["Basel III FRTB", "BCBS d352"], "severity_mix": ["Medium", "Medium"]},
    {"area": "market_risk", "topic": "Interest Rate Risk in Banking Book", "regulations": ["BCBS IRRBB", "BCB Circular 3.876"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "market_risk", "topic": "Market Risk Limits Framework", "regulations": ["Basel III Pillar 2", "BCB Resolucao 4.557"], "severity_mix": ["Medium", "Low"]},

    # Operational Risk (7 reports)
    {"area": "operational_risk", "topic": "SMA Implementation Review", "regulations": ["Basel III SMA", "BCB Resolucao 356"], "severity_mix": ["High", "Medium"]},
    {"area": "operational_risk", "topic": "Incident Management Process", "regulations": ["BCB Resolucao 4.893", "BCBS 195"], "severity_mix": ["Medium", "Medium", "Low"]},
    {"area": "operational_risk", "topic": "Business Continuity Planning", "regulations": ["BCB Resolucao 4.893", "ISO 22301"], "severity_mix": ["High", "Medium"]},
    {"area": "operational_risk", "topic": "Third-Party Risk Management", "regulations": ["BCB Resolucao 4.893", "BCBS d240"], "severity_mix": ["Critical", "High"]},
    {"area": "operational_risk", "topic": "Fraud Risk Assessment", "regulations": ["BCB Circular 3.978", "COSO 2013"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "operational_risk", "topic": "Operational Risk Data Quality", "regulations": ["BCBS 239", "BCB Resolucao 4.557"], "severity_mix": ["Medium", "Low"]},
    {"area": "operational_risk", "topic": "Key Risk Indicator Framework", "regulations": ["Basel III Pillar 2", "IIA Standards"], "severity_mix": ["Medium", "Low"]},

    # Compliance / AML (7 reports)
    {"area": "compliance_aml", "topic": "KYC Process Effectiveness", "regulations": ["BCB Circular 3.978", "FATF Recommendations"], "severity_mix": ["High", "High", "Medium"]},
    {"area": "compliance_aml", "topic": "PLD/FT Transaction Monitoring", "regulations": ["Lei 9.613/1998", "BCB Circular 3.978"], "severity_mix": ["Critical", "High"]},
    {"area": "compliance_aml", "topic": "Sanctions Screening Review", "regulations": ["BCB Circular 3.978", "OFAC/UN Sanctions"], "severity_mix": ["High", "Medium"]},
    {"area": "compliance_aml", "topic": "Suspicious Activity Reporting", "regulations": ["BCB Circular 3.978", "COAF Instrucoes"], "severity_mix": ["Medium", "Medium", "Low"]},
    {"area": "compliance_aml", "topic": "AML Training Program Assessment", "regulations": ["BCB Circular 3.978", "FATF R.18"], "severity_mix": ["Medium", "Low"]},
    {"area": "compliance_aml", "topic": "Correspondent Banking Due Diligence", "regulations": ["BCB Circular 3.978", "FATF R.13"], "severity_mix": ["High", "Medium"]},
    {"area": "compliance_aml", "topic": "Beneficial Ownership Verification", "regulations": ["BCB Circular 3.978", "FATF R.10"], "severity_mix": ["High", "Medium", "Low"]},

    # Data Protection (5 reports)
    {"area": "data_protection", "topic": "LGPD Compliance Assessment", "regulations": ["Lei 13.709/2018 (LGPD)", "ANPD Resolutions"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "data_protection", "topic": "Data Governance Framework", "regulations": ["LGPD Art. 46-51", "BCBS 239"], "severity_mix": ["Medium", "Medium"]},
    {"area": "data_protection", "topic": "Data Breach Response Readiness", "regulations": ["LGPD Art. 48", "BCB Resolucao 4.893"], "severity_mix": ["Critical", "High"]},
    {"area": "data_protection", "topic": "Data Subject Rights Processing", "regulations": ["LGPD Art. 17-22", "ANPD Resolution 2"], "severity_mix": ["High", "Medium"]},
    {"area": "data_protection", "topic": "Privacy Impact Assessment Process", "regulations": ["LGPD Art. 38", "ANPD Guidelines"], "severity_mix": ["Medium", "Low"]},

    # Cybersecurity (5 reports)
    {"area": "cybersecurity", "topic": "Penetration Testing Results", "regulations": ["BCB Resolucao 4.893", "ISO 27001"], "severity_mix": ["Critical", "High", "Medium"]},
    {"area": "cybersecurity", "topic": "Access Control Review", "regulations": ["BCB Resolucao 4.893 Art. 3", "NIST CSF"], "severity_mix": ["High", "Medium"]},
    {"area": "cybersecurity", "topic": "Cloud Security Assessment", "regulations": ["BCB Resolucao 4.893 Art. 12-15", "CSA CCM"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "cybersecurity", "topic": "Security Incident Response", "regulations": ["BCB Resolucao 4.893 Art. 6", "ISO 27035"], "severity_mix": ["Medium", "Medium"]},
    {"area": "cybersecurity", "topic": "Cybersecurity Awareness Program", "regulations": ["BCB Resolucao 4.893", "NIST CSF PR.AT"], "severity_mix": ["Medium", "Low"]},

    # IT General Controls (5 reports)
    {"area": "it_controls", "topic": "Change Management Process", "regulations": ["BCB Resolucao 4.893", "COBIT 5"], "severity_mix": ["High", "Medium"]},
    {"area": "it_controls", "topic": "BCP/DR Testing Results", "regulations": ["BCB Resolucao 4.893", "ISO 22301"], "severity_mix": ["High", "Medium", "Low"]},
    {"area": "it_controls", "topic": "SDLC Security Review", "regulations": ["BCB Resolucao 4.893", "OWASP SAMM"], "severity_mix": ["Medium", "Medium"]},
    {"area": "it_controls", "topic": "Database Security Assessment", "regulations": ["BCB Resolucao 4.893", "LGPD Art. 46"], "severity_mix": ["High", "Medium"]},
    {"area": "it_controls", "topic": "IT Asset Management Review", "regulations": ["BCB Resolucao 4.893", "NIST CSF ID.AM"], "severity_mix": ["Medium", "Low"]},
]

AUDIT_TEMPLATE = """# Audit Report: {area_display} - {topic}

## Executive Summary

This internal audit report covers the assessment of {topic} at the institution.
The audit was conducted in accordance with International Standards for the
Professional Practice of Internal Auditing (IIA Standards) and evaluated
compliance with {regulations_str}.

**Overall Rating**: {overall_rating}

## Scope

- **Period**: January 2024 - December 2024
- **Areas Reviewed**: {topic}
- **Methodology**: Risk-based audit approach, document review, interviews,
  process walkthroughs, data analytics, and sample testing
- **Regulatory Framework**: {regulations_str}

## Findings

{findings_text}

## Control Assessment

| Control Area | Rating | Key Gaps |
|-------------|--------|----------|
{controls_table}

## Recommendations Summary

{recommendations_text}

## Management Action Plan

Management has committed to addressing the findings within the established
deadlines. Progress will be monitored through quarterly follow-up reviews.

## Distribution

- Chief Risk Officer
- Chief Compliance Officer
- Head of Internal Audit
- Board Audit Committee
"""

FINDING_TEMPLATE = """### Finding {n}: {title}

- **Severity**: {severity}
- **Category**: {category}
- **Description**: {description}
- **Root Cause**: {root_cause}
- **Regulation Reference**: {regulation}
- **Recommendation**: {recommendation}
- **Management Response**: Agreed. Remediation plan in progress.
- **Remediation Deadline**: {deadline}
"""

AREA_DISPLAY = {
    "capital_adequacy": "Capital Adequacy",
    "credit_risk": "Credit Risk",
    "market_risk": "Market Risk",
    "operational_risk": "Operational Risk",
    "compliance_aml": "Compliance / AML",
    "data_protection": "Data Protection",
    "cybersecurity": "Cybersecurity",
    "it_controls": "IT General Controls",
}


def generate_findings(config: dict) -> str:
    """Generate finding sections based on severity mix.

    Args:
        config: Report configuration dict.

    Returns:
        Markdown text with all findings.
    """
    findings = []
    severity_mix = config["severity_mix"]
    topic = config["topic"]
    regulations = config["regulations"]

    finding_templates_by_severity = {
        "Critical": {
            "title": f"Significant gap in {topic}",
            "description": f"The audit identified a critical deficiency in the {topic.lower()} "
                          f"process that could lead to material regulatory non-compliance.",
            "root_cause": "Inadequate process design and insufficient management oversight.",
            "recommendation": "Immediate remediation required. Implement enhanced controls "
                            "and establish a dedicated task force.",
            "deadline": "Q1 2025",
        },
        "High": {
            "title": f"Material weakness in {topic} controls",
            "description": f"Testing revealed that key controls related to {topic.lower()} "
                          f"are not operating effectively.",
            "root_cause": "Lack of formalized procedures and insufficient training.",
            "recommendation": "Formalize procedures, enhance training program, and implement "
                            "automated monitoring.",
            "deadline": "Q2 2025",
        },
        "Medium": {
            "title": f"Process improvement needed for {topic}",
            "description": f"The current {topic.lower()} process has areas that could be "
                          f"strengthened to better align with regulatory expectations.",
            "root_cause": "Evolving regulatory requirements not fully reflected in current processes.",
            "recommendation": "Update policies and procedures to reflect current regulatory "
                            "requirements and industry best practices.",
            "deadline": "Q3 2025",
        },
        "Low": {
            "title": f"Minor documentation gap in {topic}",
            "description": f"Documentation related to {topic.lower()} could be improved "
                          f"for completeness and clarity.",
            "root_cause": "Documentation standards not consistently applied.",
            "recommendation": "Enhance documentation standards and implement periodic reviews.",
            "deadline": "Q4 2025",
        },
    }

    for i, severity in enumerate(severity_mix, 1):
        template = finding_templates_by_severity[severity]
        category = config["area"].replace("_", " ").title()
        regulation = regulations[i % len(regulations)]

        findings.append(FINDING_TEMPLATE.format(
            n=i,
            title=template["title"],
            severity=severity,
            category=category,
            description=template["description"],
            root_cause=template["root_cause"],
            regulation=regulation,
            recommendation=template["recommendation"],
            deadline=template["deadline"],
        ))

    return "\n".join(findings)


def generate_controls_table(config: dict) -> str:
    """Generate controls assessment table.

    Args:
        config: Report configuration dict.

    Returns:
        Markdown table rows.
    """
    has_critical = "Critical" in config["severity_mix"]
    has_high = "High" in config["severity_mix"]

    if has_critical:
        overall = "Ineffective"
        gaps = "Critical control gaps identified"
    elif has_high:
        overall = "Needs Improvement"
        gaps = "Material weaknesses in key controls"
    else:
        overall = "Effective"
        gaps = "Minor improvements recommended"

    rows = [
        f"| {config['topic']} | {overall} | {gaps} |",
        f"| Documentation | {'Needs Improvement' if has_high else 'Effective'} | "
        f"{'Policy updates required' if has_high else 'Adequately maintained'} |",
        f"| Monitoring | {'Needs Improvement' if has_critical else 'Effective'} | "
        f"{'Enhanced monitoring needed' if has_critical else 'Regular reviews in place'} |",
    ]
    return "\n".join(rows)


def generate_recommendations(config: dict) -> str:
    """Generate recommendations summary.

    Args:
        config: Report configuration dict.

    Returns:
        Markdown list of recommendations.
    """
    recs = [
        f"1. Address all {len(config['severity_mix'])} findings within established deadlines",
        f"2. Enhance {config['topic'].lower()} documentation and procedures",
        f"3. Implement regular monitoring and reporting mechanisms",
        f"4. Ensure alignment with {', '.join(config['regulations'])}",
    ]
    return "\n".join(recs)


def generate_report(config: dict, index: int) -> tuple[str, str]:
    """Generate a single audit report.

    Args:
        config: Report configuration dict.
        index: Report index (1-based).

    Returns:
        Tuple of (filename, report_content).
    """
    area = config["area"]
    topic = config["topic"]
    regulations = config["regulations"]
    severity_mix = config["severity_mix"]

    # Determine overall rating
    if "Critical" in severity_mix:
        overall_rating = "Unsatisfactory"
    elif severity_mix.count("High") >= 2:
        overall_rating = "Needs Improvement"
    elif "High" in severity_mix:
        overall_rating = "Needs Improvement"
    else:
        overall_rating = "Satisfactory"

    findings_text = generate_findings(config)
    controls_table = generate_controls_table(config)
    recommendations_text = generate_recommendations(config)

    content = AUDIT_TEMPLATE.format(
        area_display=AREA_DISPLAY.get(area, area),
        topic=topic,
        regulations_str=", ".join(regulations),
        overall_rating=overall_rating,
        findings_text=findings_text,
        controls_table=controls_table,
        recommendations_text=recommendations_text,
    )

    filename = f"audit_{index:03d}_{area}.md"
    return filename, content


def main():
    """Entry point for audit report generation."""
    parser = argparse.ArgumentParser(
        description="Generate simulated audit reports for GraphRAG corpus",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="",
        help="Output directory for audit reports",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of reports to generate (default: 50)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without generating",
    )
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Generate from templates only (no API calls)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    if not args.output_dir:
        base = Path(__file__).resolve().parent.parent.parent
        args.output_dir = str(base / "implementacao" / "data" / "audit_reports")

    configs = REPORT_CONFIGS[:args.count]

    if args.dry_run:
        print(f"\n{'='*70}")
        print(f"  Audit Report Generation Plan ({len(configs)} reports)")
        print(f"{'='*70}")

        # Count by area
        area_counts: dict[str, int] = {}
        for c in configs:
            area = c["area"]
            area_counts[area] = area_counts.get(area, 0) + 1

        for area, count in area_counts.items():
            display = AREA_DISPLAY.get(area, area)
            print(f"  {display:30s}: {count} reports")

        print(f"\n  Total: {len(configs)} reports")
        print(f"  Output: {args.output_dir}")
        return

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    generated = []
    for i, config in enumerate(configs, 1):
        filename, content = generate_report(config, i)
        filepath = os.path.join(args.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        generated.append(filepath)
        logger.info("Generated: %s (%s)", filename, config["topic"])

    print(f"\nGenerated {len(generated)} audit reports in {args.output_dir}")


if __name__ == "__main__":
    main()
