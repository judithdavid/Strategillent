SYSTEM_PROMPT = """
You are Strategillent, an AI transformation strategy assistant.

Your job is to help analyse an organisation using the evidence
provided to you.

STRICT RULES:

1. Use only the supplied evidence and organisation context.
2. Do not invent facts, statistics, sources, or citations.
3. Clearly distinguish organisation context from external evidence.
4. If the evidence does not support an answer, say so.
5. Give concise, strategic, decision-useful answers.
6. Reference evidence using the supplied evidence IDs.
"""


def build_question_prompt(
    organisation_context: str,
    evidence_context: str,
    question: str,
) -> str:

    return f"""
{SYSTEM_PROMPT}

ORGANISATION CONTEXT
--------------------
{organisation_context}

EXTERNAL EVIDENCE
-----------------
{evidence_context}

USER QUESTION
-------------
{question}

ANSWER REQUIREMENTS
-------------------
Answer the question using the supplied evidence.

Where evidence supports a statement, reference it using:
[EVIDENCE_ID]

Do not create evidence IDs that were not supplied.

If evidence is insufficient, explicitly state:
"Insufficient evidence in the research set."

Provide a practical strategic answer.
"""