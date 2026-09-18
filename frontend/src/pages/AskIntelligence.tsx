import { useState } from "react";
import { Bot, Send, ExternalLink } from "lucide-react";
import { useQuestions } from "../hooks/useQuestions";
import { useOrganisationContext } from "../context/OrganisationContext";

const suggestedQuestions = [
  "What transformation areas should FinNova focus on?",
  "Why is fraud transformation important?",
  "What evidence supports AI-assisted lending?",
  "How can FinNova improve customer experience?",
  "What should FinNova prioritize first?",
];

export default function AskIntelligence() {
  const { selectedOrganisationId, selectedOrganisation } = useOrganisationContext();
  const { ask, response, loading, error } = useQuestions(selectedOrganisationId);

  const [question, setQuestion] = useState("");

  async function submitQuestion(value?: string) {
    const finalQuestion = (value ?? question).trim();

    if (!finalQuestion) return;

    setQuestion(finalQuestion);
    await ask(finalQuestion);
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    submitQuestion();
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="eyebrow">AI Strategy Assistant</div>
          <h1>Ask Strategillent</h1>
          <p>
            Ask strategic questions and receive answers grounded in the
            research evidence stored in the platform.
          </p>
        </div>
      </div>

      <div className="ask-layout">
        <div className="card ask-card">
          <div className="ask-intro">
            <div className="ask-icon">
              <Bot size={24} />
            </div>

            <div>
              <h2>Strategy Intelligence</h2>
              <p>
                Questions are answered using {selectedOrganisation?.name ?? "the selected organisation"}'s organisation context
                and retrieved external evidence.
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="question-form">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a strategic question..."
              rows={5}
            />

            <button
              type="submit"
              className="primary-button"
              disabled={loading || !question.trim()}
            >
              <Send size={17} />

              {loading ? "Analysing..." : "Ask Strategillent"}
            </button>
          </form>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>

        <div className="card suggested-card">
          <h2>Suggested questions</h2>

          <div className="suggested-list">
            {suggestedQuestions.map((item) => (
              <button
                key={item}
                className="suggested-question"
                onClick={() => submitQuestion(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>

      {response && (
        <div className="card answer-card">
          <div className="answer-header">
            <div className="ask-icon">
              <Bot size={20} />
            </div>

            <div>
              <div className="eyebrow">Strategillent Answer</div>
              <h2>{response.question}</h2>
            </div>
          </div>

          <div className="answer-body">
            <p>{response.answer}</p>
          </div>

          <div className="answer-footer">
            <div>
              <span className="footer-label">Model</span>
              <strong>{response.model_used ?? "Unknown"}</strong>
            </div>

            <div>
              <span className="footer-label">Evidence used</span>

              <div className="answer-evidence">
                {response.evidence_ids.length === 0 ? (
                  <span>No evidence references returned.</span>
                ) : (
                  response.evidence_ids.map((id) => (
                    <span className="evidence-chip" key={id}>
                      {id}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card grounding-card">
        <div>
          <div className="eyebrow">Traceability</div>
          <h2>Evidence-grounded intelligence</h2>
          <p>
            Strategillent retrieves relevant evidence before generating an
            answer. Evidence IDs are returned with each response so the
            reasoning can be traced back to the research set.
          </p>
        </div>

        <ExternalLink size={22} />
      </div>
    </div>
  );
}