# Multi-Agent System Input/Output Scenarios

This document describes various input scenarios and the expected output from the Multi-Agent Harassment Detection System. The system employs a chain of agents: **Linguistic Analyst**, **Policy Auditor**, and **Resolution Agent**.

## Agents Overview

1.  **Linguistic Analyst**: Analyzes tone, intent, and subtle nuances (sarcasm, slang).
2.  **Policy Auditor**: Checks against community guidelines (Hate Speech, Gender-based Harassment, Violence, Cyberbullying).
3.  **Resolution Agent**: Assigns severity and suggests mitigation actions.

---

## Scenarios

### Scenario 1: Safe Content
**Input Text**: "I really enjoyed the community event today! Everyone was so helpful."

**Expected Output**:
- **Status**: `safe`
- **Category**: `None`
- **Severity**: `Low`
- **Suggested Action**: `Ignore`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Positive tone, appreciative intent.
    - *Policy Auditor*: No violations found.
    - *Resolution Agent*: Content is safe.

### Scenario 2: Hate Speech (SDG 10)
**Input Text**: "People like [Group X] shouldn't be allowed here. They ruin everything."

**Expected Output**:
- **Status**: `harmful`
- **Category**: `Hate Speech`
- **Severity**: `High`
- **Suggested Action**: `Warn` or `Shadowban`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Hostile tone, discriminatory intent.
    - *Policy Auditor*: Violation of Hate Speech policy (targeting a group).
    - *Resolution Agent*: High severity due to discriminatory nature.

### Scenario 3: Gender-based Harassment (SDG 5)
**Input Text**: "Go back to the kitchen where you belong. Women can't code."

**Expected Output**:
- **Status**: `harmful`
- **Category**: `Gender-based Harassment`
- **Severity**: `High`
- **Suggested Action**: `Shadowban`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Sexist tone, demeaning intent.
    - *Policy Auditor*: Violation of Gender-based Harassment policy.
    - *Resolution Agent*: High severity due to sexist stereotypes and exclusion.

### Scenario 4: Cyberbullying
**Input Text**: "You are so stupid, nobody likes you. Just delete your account."

**Expected Output**:
- **Status**: `harmful`
- **Category**: `Cyberbullying`
- **Severity**: `Medium` to `High`
- **Suggested Action**: `Warn`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Aggressive tone, personal attack.
    - *Policy Auditor*: Violation of Cyberbullying policy.
    - *Resolution Agent*: Medium/High severity depending on history (stateless here, so likely High).

### Scenario 5: Incitement of Violence (SDG 16)
**Input Text**: "I'm going to find where you live and hurt you."

**Expected Output**:
- **Status**: `harmful`
- **Category**: `Incitement of Violence`
- **Severity**: `Critical`
- **Suggested Action**: `Immediate Report`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Threatening tone, violent intent.
    - *Policy Auditor*: Violation of Incitement of Violence policy.
    - *Resolution Agent*: Critical severity, immediate danger.

### Scenario 6: Ambiguous/Sarcastic (Linguistic Nuance)
**Input Text**: "Oh great, another brilliant idea from the genius." (Context: Sarcastic)

**Expected Output**:
- **Status**: `safe` or `harmful` (depending on strictness, likely `safe` but noted as rude)
- **Category**: `None` or `Cyberbullying` (Low confidence)
- **Severity**: `Low`
- **Suggested Action**: `Ignore`
- **Reasoning Chain**:
    - *Linguistic Analyst*: Sarcastic tone, passive-aggressive.
    - *Policy Auditor*: May not meet threshold for specific violation, or minor bullying.
    - *Resolution Agent*: Low severity, likely ignore or monitor.

---

## API Usage

**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "text": "Your input text here"
}
```

**Response Format**:
```json
{
  "status": "harmful",
  "category": "Hate Speech",
  "severity": "High",
  "reasoning_chain": [
    {
      "agent": "Linguistic Analyst",
      "thought": "...",
      "output": "..."
    },
    ...
  ],
  "suggested_action": "Warn"
}
```
