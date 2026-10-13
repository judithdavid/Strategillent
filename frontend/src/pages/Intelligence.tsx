import { useOrganisationContext } from "../context/OrganisationContext";
import { useOrganisation } from "../hooks/useOrganisation";
import { useIntelligence } from "../hooks/useIntelligence";

const styles = {
  page: { maxWidth: 1180, margin: "0 auto", padding: "28px 22px", color: "var(--text-primary, #172033)" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 20, flexWrap: "wrap" as const, marginBottom: 24 },
  eyebrow: { margin: "0 0 8px", fontSize: 12, fontWeight: 700, letterSpacing: "0.12em", color: "var(--text-muted, #687386)" },
  title: { margin: "0 0 8px", fontSize: 30, lineHeight: 1.2 },
  muted: { color: "var(--text-muted, #687386)", lineHeight: 1.6 },
  button: { border: 0, borderRadius: 10, padding: "12px 18px", fontWeight: 700, cursor: "pointer", background: "var(--primary, #3157d5)", color: "#fff" },
  error: { border: "1px solid #f1b5b5", background: "#fff3f3", color: "#8b2020", borderRadius: 10, padding: 14, marginBottom: 20 },
  summaryGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, margin: "22px 0 30px" },
  summary: { border: "1px solid var(--border, #e2e7ef)", borderRadius: 14, padding: 18, background: "var(--surface, #fff)" },
  summaryNumber: { display: "block", fontSize: 28, fontWeight: 750, marginBottom: 4 },
  section: { marginTop: 30 },
  sectionHeader: { marginBottom: 14 },
  sectionTitle: { margin: "0 0 6px", fontSize: 22 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 14 },
  card: { border: "1px solid var(--border, #e2e7ef)", borderRadius: 14, padding: 18, background: "var(--surface, #fff)", minWidth: 0 },
  cardTop: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, marginBottom: 10 },
  cardTitle: { margin: "0 0 8px", fontSize: 17, lineHeight: 1.4 },
  pill: { display: "inline-block", borderRadius: 999, padding: "4px 9px", fontSize: 12, fontWeight: 700, background: "var(--surface-muted, #eef2f8)", whiteSpace: "nowrap" as const },
  detail: { marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--border, #e2e7ef)" },
  details: { marginTop: 12 },
  evidence: { display: "flex", gap: 6, flexWrap: "wrap" as const, marginTop: 12 },
  evidenceChip: { fontSize: 12, borderRadius: 6, padding: "4px 7px", background: "var(--surface-muted, #eef2f8)" },
  empty: { border: "1px dashed var(--border, #cbd3df)", borderRadius: 14, padding: 22, color: "var(--text-muted, #687386)" },
};

export default function Intelligence() {
  const { selectedOrganisationId } = useOrganisationContext();
  const { organisation, loading: organisationLoading } = useOrganisation(selectedOrganisationId);
  const {
    intelligence,
    loading: intelligenceLoading,
    running,
    error,
    executeAnalysis,
  } = useIntelligence(selectedOrganisationId);

  if (organisationLoading) {
    return <main style={styles.page}><div style={styles.empty}>Loading organisation…</div></main>;
  }

  if (!organisation) {
    return <main style={styles.page}><div style={styles.empty}>No organisation selected. Choose an organisation to view its strategy.</div></main>;
  }

  const issues = intelligence?.strategic_issues ?? [];
  const opportunities = intelligence?.opportunities ?? [];
  const initiatives = intelligence?.initiatives ?? [];

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <div>
          <p style={styles.eyebrow}>STRATEGY WORKSPACE</p>
          <h1 style={styles.title}>Strategic intelligence</h1>
          <p style={{ ...styles.muted, margin: 0 }}>
            Review the issues, opportunities, and actions identified for <strong>{organisation.name}</strong>.
          </p>
        </div>
        <button
          type="button"
          style={{ ...styles.button, opacity: running ? 0.7 : 1 }}
          onClick={executeAnalysis}
          disabled={running || !selectedOrganisationId}
        >
          {running ? "Analysing…" : intelligence ? "Run analysis again" : "Run analysis"}
        </button>
      </header>

      {error && <div role="alert" style={styles.error}>{error}</div>}

      {intelligenceLoading && <div style={styles.empty}>Loading strategy results…</div>}

      {!intelligence && !intelligenceLoading && (
        <div style={styles.empty}>
          <h2 style={{ marginTop: 0 }}>No analysis yet</h2>
          <p>Run the analysis to generate a starting point for this organisation’s transformation plan.</p>
          <p style={{ marginBottom: 0 }}>The quality of recommendations depends on the organisation profile and the available evidence.</p>
        </div>
      )}

      {intelligence && (
        <>
          <div style={styles.summaryGrid}>
            <div style={styles.summary}><span style={styles.summaryNumber}>{issues.length}</span><span style={styles.muted}>Strategic issues</span></div>
            <div style={styles.summary}><span style={styles.summaryNumber}>{opportunities.length}</span><span style={styles.muted}>Opportunities</span></div>
            <div style={styles.summary}><span style={styles.summaryNumber}>{initiatives.length}</span><span style={styles.muted}>Initiatives</span></div>
            <div style={styles.summary}><span style={styles.summaryNumber}>#{intelligence.analysis_run_id ?? "—"}</span><span style={styles.muted}>Analysis run</span></div>
          </div>

          <section style={styles.section}>
            <div style={styles.sectionHeader}>
              <p style={styles.eyebrow}>01 / UNDERSTAND</p>
              <h2 style={styles.sectionTitle}>What needs attention?</h2>
              <p style={{ ...styles.muted, margin: 0 }}>Issues identified by the current analysis. Check the rationale and linked evidence before acting.</p>
            </div>
            {issues.length === 0 ? <div style={styles.empty}>No strategic issues were returned.</div> : (
              <div style={styles.grid}>
                {issues.map((issue) => (
                  <article key={issue.id} style={styles.card}>
                    <div style={styles.cardTop}>
                      <span style={styles.pill}>Severity {issue.severity}/5</span>
                      <span style={styles.pill}>Urgency {issue.urgency}/5</span>
                    </div>
                    <h3 style={styles.cardTitle}>{issue.title}</h3>
                    <p style={styles.muted}>{issue.description}</p>
                    {issue.rationale && <div style={styles.detail}><strong>Why it matters</strong><p style={{ marginBottom: 0 }}>{issue.rationale}</p></div>}
                    {issue.evidence?.length > 0 && (
                      <div style={styles.evidence} aria-label="Supporting evidence">
                        {issue.evidence.map((item) => <span key={item.id} style={styles.evidenceChip}>{item.external_id}</span>)}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>

          <section style={styles.section}>
            <div style={styles.sectionHeader}>
              <p style={styles.eyebrow}>02 / CHOOSE</p>
              <h2 style={styles.sectionTitle}>Where could the organisation improve?</h2>
              <p style={{ ...styles.muted, margin: 0 }}>Use priority scores as decision support, not as a substitute for business validation.</p>
            </div>
            {opportunities.length === 0 ? <div style={styles.empty}>No opportunities were returned.</div> : (
              <div style={styles.grid}>
                {opportunities.map((opportunity) => (
                  <article key={opportunity.id} style={styles.card}>
                    <div style={styles.cardTop}>
                      <span style={styles.pill}>Priority #{opportunity.priority_rank ?? "—"}</span>
                      <span style={styles.pill}>Score {opportunity.priority_score?.toFixed(2) ?? "—"}</span>
                    </div>
                    <h3 style={styles.cardTitle}>{opportunity.title}</h3>
                    <p style={styles.muted}>{opportunity.description}</p>
                    {opportunity.rationale && <div style={styles.detail}><strong>Rationale</strong><p style={{ marginBottom: 0 }}>{opportunity.rationale}</p></div>}
                    <details style={styles.details}>
                      <summary style={{ cursor: "pointer", fontWeight: 700 }}>View scoring and evidence</summary>
                      <div style={styles.summaryGrid}>
                        <div><strong>Business impact</strong><div>{opportunity.business_impact}/5</div></div>
                        <div><strong>Feasibility</strong><div>{opportunity.feasibility}/5</div></div>
                        <div><strong>Urgency</strong><div>{opportunity.urgency}/5</div></div>
                        <div><strong>Strategic alignment</strong><div>{opportunity.strategic_alignment}/5</div></div>
                        <div><strong>Evidence confidence</strong><div>{opportunity.evidence_confidence}/5</div></div>
                      </div>
                      {opportunity.evidence?.length > 0 && <div style={styles.evidence}>{opportunity.evidence.map((item) => <span key={item.id} style={styles.evidenceChip}>{item.external_id}</span>)}</div>}
                    </details>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section style={styles.section}>
            <div style={styles.sectionHeader}>
              <p style={styles.eyebrow}>03 / ACT</p>
              <h2 style={styles.sectionTitle}>What actions are proposed?</h2>
              <p style={{ ...styles.muted, margin: 0 }}>Review the expected outcome, success metric, and implementation phase for each initiative.</p>
            </div>
            {initiatives.length === 0 ? <div style={styles.empty}>No initiatives were returned.</div> : (
              <div style={styles.grid}>
                {initiatives.map((initiative) => (
                  <article key={initiative.id} style={styles.card}>
                    <div style={styles.cardTop}>
                      <h3 style={styles.cardTitle}>{initiative.name}</h3>
                      <span style={styles.pill}>{initiative.status}</span>
                    </div>
                    <p style={styles.muted}>{initiative.description}</p>
                    {initiative.expected_outcome && <div style={styles.detail}><strong>Expected outcome</strong><p style={{ marginBottom: 0 }}>{initiative.expected_outcome}</p></div>}
                    {initiative.success_metric && <div style={styles.detail}><strong>Success metric</strong><p style={{ marginBottom: 0 }}>{initiative.success_metric}</p></div>}
                    {initiative.implementation_phase && <div style={styles.detail}><strong>Implementation phase</strong><p style={{ marginBottom: 0 }}>{initiative.implementation_phase}</p></div>}
                  </article>
                ))}
              </div>
            )}
          </section>

          <p style={{ ...styles.muted, fontSize: 12, marginTop: 28 }}>
            Review note: these results are generated by the current application logic. Validate that each recommendation fits this organisation and that its cited evidence supports the claim.
          </p>
        </>
      )}
    </main>
  );
}
