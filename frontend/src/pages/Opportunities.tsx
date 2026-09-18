import { useIntelligence } from "../hooks/useIntelligence";
import { useOrganisationContext } from "../context/OrganisationContext";

export default function Opportunities() {
  const { selectedOrganisationId, selectedOrganisation } = useOrganisationContext();
  const { intelligence, loading, error } = useIntelligence(selectedOrganisationId);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Opportunities</h1>
          <p>{selectedOrganisation?.name ?? "Selected organisation"} transformation portfolio.</p>
        </div>

        <div className="card empty-state">
          <p>Loading opportunities...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <h1>Opportunities</h1>
          <p>Ranked transformation opportunities.</p>
        </div>

        <div className="card empty-state">
          <h3>Unable to load opportunities</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!intelligence || intelligence.opportunities.length === 0) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <div className="eyebrow">Transformation Portfolio</div>
            <h1>Opportunities</h1>
            <p>Ranked transformation opportunities.</p>
          </div>
        </div>

        <div className="card empty-state">
          <h3>No opportunities yet</h3>
          <p>
            Run the intelligence analysis from the Intelligence page first.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="eyebrow">Transformation Portfolio</div>
          <h1>Opportunities</h1>
          <p>
            Evidence-backed opportunities ranked using a deterministic
            prioritisation model.
          </p>
        </div>
      </div>

      <div className="opportunity-explainer card">
        <div>
          <h2>How prioritisation works</h2>
          <p>
            Priority scores combine business impact, feasibility, urgency,
            strategic alignment and evidence confidence.
          </p>
        </div>

        <div className="formula">
          <span>35% Impact</span>
          <span>20% Feasibility</span>
          <span>20% Urgency</span>
          <span>15% Alignment</span>
          <span>10% Evidence</span>
        </div>
      </div>

      <div className="opportunities-list">
        {intelligence.opportunities.map((opportunity) => (
          <article className="card opportunity-detail-card" key={opportunity.id}>
            <div className="opportunity-detail-header">
              <div className="rank large-rank">
                #{opportunity.priority_rank}
              </div>

              <div className="opportunity-main">
                <div className="opportunity-header">
                  <div>
                    <div className="eyebrow">Transformation opportunity</div>
                    <h2>{opportunity.title}</h2>
                  </div>

                  <div className="priority-score large-score">
                    {opportunity.priority_score?.toFixed(2)}
                  </div>
                </div>

                <p>{opportunity.description}</p>

                {opportunity.rationale && (
                  <div className="rationale">
                    <strong>Why this matters</strong>
                    <p>{opportunity.rationale}</p>
                  </div>
                )}

                <div className="score-grid">
                  <div className="score-item">
                    <span>Business Impact</span>
                    <strong>{opportunity.business_impact}/5</strong>
                  </div>

                  <div className="score-item">
                    <span>Feasibility</span>
                    <strong>{opportunity.feasibility}/5</strong>
                  </div>

                  <div className="score-item">
                    <span>Urgency</span>
                    <strong>{opportunity.urgency}/5</strong>
                  </div>

                  <div className="score-item">
                    <span>Strategic Alignment</span>
                    <strong>{opportunity.strategic_alignment}/5</strong>
                  </div>

                  <div className="score-item">
                    <span>Evidence Confidence</span>
                    <strong>{opportunity.evidence_confidence}/5</strong>
                  </div>
                </div>

                <div className="evidence-row">
                  <span className="evidence-label">Evidence</span>

                  {opportunity.evidence.map((evidence) => (
                    <span
                      className="evidence-chip"
                      key={evidence.id}
                    >
                      {evidence.external_id}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {opportunity.initiatives &&
              opportunity.initiatives.length > 0 && (
                <div className="initiative-section">
                  <div className="eyebrow">Recommended initiatives</div>

                  <div className="initiative-grid">
                    {opportunity.initiatives.map((initiative) => (
                      <div
                        className="initiative-mini-card"
                        key={initiative.id}
                      >
                        <div className="initiative-top">
                          <h3>{initiative.name}</h3>
                          <span className="status">
                            {initiative.status}
                          </span>
                        </div>

                        <p>{initiative.description}</p>

                        {initiative.expected_outcome && (
                          <div className="initiative-detail">
                            <span>Expected outcome</span>
                            <strong>
                              {initiative.expected_outcome}
                            </strong>
                          </div>
                        )}

                        {initiative.success_metric && (
                          <div className="initiative-detail">
                            <span>Success metric</span>
                            <strong>
                              {initiative.success_metric}
                            </strong>
                          </div>
                        )}

                        {initiative.implementation_phase && (
                          <div className="initiative-detail">
                            <span>Phase</span>
                            <strong>
                              {initiative.implementation_phase}
                            </strong>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </article>
        ))}
      </div>
    </div>
  );
}