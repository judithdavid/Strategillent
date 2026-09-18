import { useOrganisationContext } from "../context/OrganisationContext";
import { useIntelligence } from "../hooks/useIntelligence";
import { useOrganisation } from "../hooks/useOrganisation";

export default function Dashboard() {
  const { selectedOrganisationId } = useOrganisationContext();

  const {
    organisation,
    loading: organisationLoading,
    error: organisationError,
  } = useOrganisation(selectedOrganisationId);

  const {
    intelligence,
    loading: intelligenceLoading,
    running,
    error: intelligenceError,
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
          <p className="eyebrow">STRATEGY INTELLIGENCE</p>

          <h1>{organisation.name}</h1>

          <p className="page-description">
            AI-powered transformation intelligence for strategic decision
            making.
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

      {(organisationError || intelligenceError) && (
        <div className="error-message">
          {organisationError || intelligenceError}
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Customers</span>
          <strong className="metric-value">
            {organisation.customers?.toLocaleString() ?? "—"}
          </strong>
        </div>

        <div className="metric-card">
          <span className="metric-label">Employees</span>
          <strong className="metric-value">
            {organisation.employees?.toLocaleString() ?? "—"}
          </strong>
        </div>

        <div className="metric-card">
          <span className="metric-label">Strategic Issues</span>
          <strong className="metric-value">
            {intelligenceLoading ? "..." : issues.length}
          </strong>
        </div>

        <div className="metric-card">
          <span className="metric-label">Opportunities</span>
          <strong className="metric-value">
            {intelligenceLoading ? "..." : opportunities.length}
          </strong>
        </div>

        <div className="metric-card">
          <span className="metric-label">Initiatives</span>
          <strong className="metric-value">
            {intelligenceLoading ? "..." : initiatives.length}
          </strong>
        </div>
      </div>

      <section className="strategic-card">
        <div className="strategic-icon">✦</div>

        <div className="strategic-content">
          <p className="eyebrow">STRATEGIC FOCUS</p>

          <h2>Transform with evidence, not assumptions</h2>

          <p>
            Strategillent connects {organisation.name}'s organisational context with
            external research evidence to identify strategic issues,
            transformation opportunities, and actionable initiatives.
          </p>

          <button
            className="text-link"
            onClick={executeAnalysis}
            disabled={running}
          >
            {running ? "Analysing..." : "Run analysis →"}
          </button>
        </div>
      </section>

      <section>
        <div className="section-header">
          <div>
            <p className="eyebrow">TRANSFORMATION AREAS</p>
            <h2>Six areas of strategic opportunity</h2>
          </div>
        </div>

        <div className="cards-grid">
          <div className="detail-card">
            <h3>Intelligent Fraud & Risk</h3>
            <p>
              Real-time transaction risk scoring, fraud analytics, and
              AI-assisted investigation.
            </p>
          </div>

          <div className="detail-card">
            <h3>AI-Assisted Lending</h3>
            <p>
              Document intelligence, underwriting support, and explainable
              lending decisions.
            </p>
          </div>

          <div className="detail-card">
            <h3>Customer Intelligence</h3>
            <p>
              Complaint classification, support assistance, and intelligent
              case routing.
            </p>
          </div>

          <div className="detail-card">
            <h3>Financial Data Platform</h3>
            <p>
              Governed financial-data ingestion, customer profiles, and data
              quality monitoring.
            </p>
          </div>

          <div className="detail-card">
            <h3>Responsible AI Governance</h3>
            <p>
              AI inventory, risk classification, explainability, and model
              monitoring.
            </p>
          </div>

          <div className="detail-card">
            <h3>Payment Operations & Resilience</h3>
            <p>
              Payment anomaly detection, incident intelligence, and operations
              assistance.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}