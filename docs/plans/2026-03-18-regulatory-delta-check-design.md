# Regulatory Delta Check - Design Spec

## Summary

Add a "PHASE 0: Regulatory Delta Check" to both `privacy-doc-generator` and `legal-advisor` agents in the `business` plugin. When either agent operates on an existing compliance document, it automatically checks for normative updates published since the document was last generated/updated, reports findings in a cascading format (summary first, detail on request), and feeds relevant changes into the agent's normal workflow.

## Context

The `privacy-doc-generator` agent generates structured compliance documents (Privacy Policies, Cookie Policies, DPAs, etc.) with metadata blocks including generation dates and normative references. The `legal-advisor` agent reviews contracts, policies, and compliance posture. Neither currently checks whether the normative landscape has changed since a document was created.

Real-world trigger: iubenda notified about Google Additional Consent updates for cookie banners. The agents should be able to detect this type of regulatory evolution when reviewing existing documents.

## Design

### Trigger Conditions

The delta check activates when the agent detects it is operating on an **existing compliance document**:

- User passes a file to read (privacy policy, cookie policy, DPA, etc.)
- User uses language indicating review/update of existing document ("rivedi", "aggiorna", "audit", "controlla")

If the document lacks a metadata block with generation date, the agent asks the user when the document was last generated/updated to define the search window.

For brand-new document generation (no existing file), the phase is skipped entirely.

### Delta Check Logic

**Step 1 - Context extraction from document:**
- Read the file and identify: jurisdictions covered, normative sources cited (GDPR articles, EDPB guidelines, Garante provvedimenti, etc.), generation/last-update date
- Build a list of "normative dependencies" of the document

**Step 2 - Targeted regulatory search (parallel WebSearch):**
- For each relevant institutional source, run time-filtered queries from document date to today:
  - `site:edpb.europa.eu guidelines {year}` for new EDPB guidelines
  - `site:garanteprivacy.it provvedimenti {year}` for new Garante provvedimenti
  - `site:eur-lex.europa.eu` for legislative amendments
  - `site:curia.europa.eu` for relevant new CJEU rulings
- Queries are calibrated to the specific jurisdictions and topics of the document (not generic)
- Sources are exclusively institutional (no CMP changelogs, no industry blogs)

**Step 3 - Cascading output:**

When updates are found:

```
## Regulatory Delta Check
Documento analizzato: {filename}
Periodo coperto: {data documento} - {oggi}
Jurisdictions: {lista}

| # | Fonte | Data | Novita' | Sezione impattata | Rilevanza |
|---|-------|------|---------|-------------------|-----------|
| 1 | EDPB Guidelines 01/2025 | 2025-03-15 | Nuove linee guida su consent banners | Cookie Policy - Consent mechanism | Alta |
| 2 | Garante provvedimento 9XXXXXX | 2025-06-01 | Chiarimento su retention marketing | Privacy Policy - Retention periods | Media |

Vuoi approfondire una o piu' voci? Indica i numeri.
```

When no updates are found:

```
## Regulatory Delta Check
Documento analizzato: {filename}
Periodo coperto: {data documento} - {oggi}

Nessun aggiornamento normativo rilevante rilevato per le jurisdictions e i temi coperti dal documento.
```

On user request for detail: the agent explains the impact of the selected item and proposes the specific modification to the document.

### Agent-Specific Integration

**`privacy-doc-generator`:**
- Inserted as PHASE 0, before the existing PHASE 1 (Context Gathering)
- Skipped for generation from scratch
- Delta check results feed into PHASE 1: if updates are found, the questionnaire incorporates them (e.g., "your document does not cover X, introduced by Y - do you want to include it?")

**`legal-advisor`:**
- Inserted as Step 0 in "Core Approach", before "Identify legal domain"
- Lighter version: produces an advisory summary rather than structured modification proposals (since legal-advisor doesn't generate structured documents)
- Activates when user asks to review existing contracts, policies, or compliance posture

### What Does NOT Change

- The existing research methodology (LEGAL RESEARCH METHOD in privacy-doc-generator, WebSearch approach in legal-advisor) remains unchanged
- The delta check does not replace normative validation during generation - it is an additional check focused on "what changed since this document was written"
- All other phases, validation checks, and output conventions remain as-is

## Scope

- **Files modified:** `plugins/business/agents/privacy-doc-generator.md`, `plugins/business/agents/legal-advisor.md`
- **No new files created**
- **No new plugins or components**

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Component type | Phase in existing agent prompts | Natural behavior, no indirection |
| Sources | Institutional only (EDPB, Garante, EUR-Lex, CJEU) | Conservative, authoritative |
| Trigger | Any interaction involving existing compliance document | Broad coverage without false positives |
| Output format | Cascading (summary then detail on request) | Avoids overwhelming user, allows drill-down |
| Document input | File-based (user passes the file) | Concrete, verifiable context |
