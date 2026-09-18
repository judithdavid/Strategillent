import { useOrganisationContext } from "../context/OrganisationContext";
import { useOrganisation } from "../hooks/useOrganisation";
import { useIntelligence } from "../hooks/useIntelligence";

export default function Intelligence() {
  const { selectedOrganisationId } = useOrganisationContext();

  const {
    organisation,
    loading: organisationLoading,
  } = useOrganisation(selectedOrganisationId);

  const {
    intelligence,
    loading: intelligenceLoading,
    running,
    error,
    executeAnalysis,
  } = useIntelligence(selectedOrganisationId);

  if (organisationLoading) {
    return (
      <div className="page">
        <div className="empty-state">
          <p>Loading organisation...</p>
        </div>
      </div>
    );
  }

  if (!organisation) {
    return (
      <div className="page">
        <div className="empty-state">
          <p>No organisation selected.</p>
        </div>
      </div>
    );
  }

  const issues = intelligence?.strategic_issues ?? [];
  const opportunities = intelligence?.opportunities ?? [];
  const initiatives = intelligence?.initiatives ?? [];

  return (
    <div className="page">
      <div className="dashboard-header">
        <div>
          <p className="eyebrow">AI ANALYSIS</p>

          <h1>Strategic Intelligence</h1>

          <p className="page-description">
            Evidence-backed transformation analysis for{" "}
            <strong>{organisation.name}</strong>.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={executeAnalysis}
          disabled={running || !selectedOrganisationId}
        >
          {running ? "Running Analysis..." : "Run Intelligence"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!intelligence && !intelligenceLoading && (
        <div className="empty-state">
          <div className="empty-icon">✦</div>

          <h2>No analysis yet</h2>

          <p>
            Run the intelligence analysis to identify strategic issues,
            opportunities, and recommended initiatives for{" "}
            {organisation.name}.
          </p>

          <button
            className="primary-button"
            onClick={executeAnalysis}
            disabled={running}
          >
            {running ? "Running Analysis..." : "Run Intelligence"}
          </button>
        </div>
      )}

      {intelligenceLoading && (
        <div className="empty-state">
          <p>Loading intelligence...</p>
        </div>
      )}

      {intelligence && (
        <>
          <div className="analysis-meta">
            <span>
              Organisation: <strong>{organisation.name}</strong>
            </span>

            {intelligence.analysis_run_id && (
              <span>
                Analysis Run:{" "}
                <strong>#{intelligence.analysis_run_id}</strong>
              </span>
            )}
          </div>

          {/* Strategic Issues */}
          <section>
            <div className="section-header">
              <div>
                <p className="eyebrow">01 · STRATEGIC ISSUES</p>
                <h2>What needs attention?</h2>
              </div>
            </div>

            {issues.length === 0 ? (
              <div className="empty-state">
                <p>No strategic issues identified.</p>
              </div>
            ) : (
              <div className="issues-grid">
                {issues.map((issue) => (
                  <div
                    className="issue-card"
                    key={issue.id}
                  >
                    <div className="issue-header">
                      <div>
                        <span className="issue-id">
                          ISSUE #{issue.id}
                        </span>

                        <h3>{issue.title}</h3>
                      </div>

                      <div className="score-grid">
                        <div className="score-item">
                          <span>Severity</span>
                          <strong>{issue.severity}/5</strong>
                        </div>

                        <div className="score-item">
                          <span>Urgency</span>
                          <strong>{issue.urgency}/5</strong>
                        </div>
                      </div>
                    </div>

                    <p>{issue.description}</p>

                    {issue.rationale && (
                      <div className="rationale">
                        <strong>Why this matters</strong>
                        <p>{issue.rationale}</p>
                      </div>
                    )}

                    {issue.evidence?.length > 0 && (
                      <div className="evidence-row">
                        <span>Evidence:</span>

                        {issue.evidence.map((evidence) => (
                          <span
                            className="evidence-chip"
                            key={evidence.id}
                          >
                            {evidence.external_id}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Opportunities */}
          <section>
            <div className="section-header">
              <div>
                <p className="eyebrow">02 · OPPORTUNITIES</p>
                <h2>Where should the organisation transform?</h2>
              </div>
            </div>

            {opportunities.length === 0 ? (
              <div className="empty-state">
                <p>No opportunities identified.</p>
              </div>
            ) : (
              <div className="opportunities-grid">
                {opportunities.map((opportunity) => (
                  <div
                    className="opportunity-card"
                    key={opportunity.id}
                  >
                    <div className="opportunity-header">
                      <div className="rank">
                        #{opportunity.priority_rank ?? "—"}
                      </div>

                      <div className="opportunity-main">
                        <h3>{opportunity.title}</h3>

                        <p>{opportunity.description}</p>
                      </div>

                      <div className="priority-score">
                        <span>Priority</span>
                        <strong>
                          {opportunity.priority_score?.toFixed(2) ?? "—"}
                        </strong>
                      </div>
                    </div>

                    {opportunity.rationale && (
                      <div className="rationale">
                        <strong>Rationale</strong>
                        <p>{opportunity.rationale}</p>
                      </div>
                    )}

                    <div className="score-grid">
                      <div className="score-item">
                        <span>Business Impact</span>
                        <strong>
                          {opportunity.business_impact}/5
                        </strong>
                      </div>

                      <div className="score-item">
                        <span>Feasibility</span>
                        <strong>
                          {opportunity.feasibility}/5
                        </strong>
                      </div>

                      <div className="score-item">
                        <span>Urgency</span>
                        <strong>
                          {opportunity.urgency}/5
                        </strong>
                      </div>

                      <div className="score-item">
                        <span>Alignment</span>
                        <strong>
                          {opportunity.strategic_alignment}/5
                        </strong>
                      </div>

                      <div className="score-item">
                        <span>Evidence</span>
                        <strong>
                          {opportunity.evidence_confidence}/5
                        </strong>
                      </div>
                    </div>

                    {opportunity.evidence?.length > 0 && (
                      <div className="evidence-row">
                        <span>Evidence:</span>

                        {opportunity.evidence.map((evidence) => (
                          <span
                            className="evidence-chip"
                            key={evidence.id}
                          >
                            {evidence.external_id}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Initiatives */}
          <section>
            <div className="section-header">
              <div>
                <p className="eyebrow">03 · INITIATIVES</p>
                <h2>What should be done?</h2>
              </div>
            </div>

            {initiatives.length === 0 ? (
              <div className="empty-state">
                <p>No initiatives generated.</p>
              </div>
            ) : (
              <div className="initiatives-grid">
                {initiatives.map((initiative) => (
                  <div
                    className="initiative-card"
                    key={initiative.id}
                  >
                    <div className="initiative-top">
                      <div>
                        <span className="issue-id">
                          INITIATIVE #{initiative.id}
                        </span>

                        <h3>{initiative.name}</h3>
                      </div>

                      <span className="status">
                        {initiative.status}
                      </span>
                    </div>

                    <p>{initiative.description}</p>

                    {initiative.expected_outcome && (
                      <div className="initiative-detail">
                        <strong>Expected outcome</strong>
                        <span>
                          {initiative.expected_outcome}
                        </span>
                      </div>
                    )}

                    {initiative.success_metric && (
                      <div className="initiative-detail">
                        <strong>Success metric</strong>
                        <span>
                          {initiative.success_metric}
                        </span>
                      </div>
                    )}

                    {initiative.implementation_phase && (
                      <div className="initiative-detail">
                        <strong>Implementation phase</strong>
                        <span>
                          {initiative.implementation_phase}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}