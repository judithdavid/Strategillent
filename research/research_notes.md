# FinNova Research Pack

## Purpose
This is the evidence foundation for the Modus Enterprise AI Build Challenge.

**FinNova is fictional. External evidence is real.**

## Dataset
- 32 evidence records
- 6 research domains
- Primary emphasis on regulators, central banks, international financial institutions and standards bodies
- Each record separates `claim`, `evidence`, and `strategic_implication`

## Six domains
1. AI
2. FRAUD
3. LENDING
4. CX
5. GOVERNANCE
6. DATA

## Important modelling rule
Do not allow the AI system to treat fictional FinNova assumptions as external facts.

External evidence answers:
> What is happening in the real financial-services environment?

FinNova context answers:
> What are we assuming about the organisation?

The intelligence layer should connect the two.

## Recommended next build
1. Load `external_evidence.json`
2. Load `finnova_context.json`
3. Load `transformation_dimensions.json`
4. Build retrieval over evidence records
5. Generate evidence-backed issue/opportunity mappings
6. Add prioritisation only after the evidence-to-opportunity chain works
