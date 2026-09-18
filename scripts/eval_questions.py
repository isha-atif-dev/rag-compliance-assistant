"""
Evaluation question set for Phase 6.

Each entry pairs a realistic compliance question with the document
that should correctly answer it. Used by evaluate_retrieval.py to
calculate Recall@5: for what percentage of these questions does the
correct source document actually appear in the top 5 retrieved chunks?
"""

EVAL_QUESTIONS = [
    {"question": "What is the timeline for reporting suspicious activity?", "expected_source": "12_sar_procedure.txt"},
    {"question": "How long must customer due diligence records be kept?", "expected_source": "05_retention_policy.txt"},
    {"question": "What are the six outcomes of treating customers fairly?", "expected_source": "10_tcf_policy.txt"},
    {"question": "How much can an employee accept in gifts before declaring it?", "expected_source": "16_conflicts_policy.txt"},
    {"question": "What are the four outcomes required under Consumer Duty?", "expected_source": "18_consumer_duty_policy.txt"},
    {"question": "Within how many hours must a data breach be reported to the ICO?", "expected_source": "20_data_breach_procedure.txt"},
    {"question": "What is required before onboarding a critical vendor?", "expected_source": "13_vendor_risk_policy.txt"},
    {"question": "How quickly must a complaint be acknowledged?", "expected_source": "06_complaints_policy.txt"},
    {"question": "What happens when a sanctions screening match is found?", "expected_source": "19_sanctions_screening_policy.txt"},
    {"question": "What is Enhanced Due Diligence and when does it apply?", "expected_source": "03_cdd_standard.txt"},
    {"question": "How can an employee report wrongdoing confidentially?", "expected_source": "08_whistleblowing_policy.txt"},
    {"question": "What is the recovery time objective for core payment processing?", "expected_source": "15_bcp_policy.txt"},
    {"question": "What approval is needed before publishing a financial promotion?", "expected_source": "17_financial_promotions_policy.txt"},
    {"question": "What multi-factor authentication requirements apply to customer data systems?", "expected_source": "14_infosec_policy.txt"},
    {"question": "What are the escalation tiers for suspected fraud?", "expected_source": "11_fraud_escalation.txt"},
    {"question": "What documents are required to verify a business customer at onboarding?", "expected_source": "02_kyc_procedures.txt"},
    {"question": "What are the five Individual Conduct Rules under SMCR?", "expected_source": "09_fca_conduct_rules.txt"},
    {"question": "What penetration testing frequency is required for customer-facing systems?", "expected_source": "14_infosec_policy.txt"},
    {"question": "What percentage of shareholding requires a beneficial owner to be identified?", "expected_source": "02_kyc_procedures.txt"},
    {"question": "What must be documented for a critical vendor's exit plan?", "expected_source": "13_vendor_risk_policy.txt"},
]