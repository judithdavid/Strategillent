import { useEffect, useMemo, useState } from "react";
import { ExternalLink, FileText, Search } from "lucide-react";
import { getEvidence, getResearchDomains } from "../services/api";
import type { Evidence } from "../types";

export default function Evidence() {
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [domains, setDomains] = useState<string[]>([]);
  const [selectedDomain, setSelectedDomain] = useState("ALL");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [evidenceData, domainData] = await Promise.all([
          getEvidence(),
          getResearchDomains(),
        ]);

        setEvidence(evidenceData);
        setDomains(domainData);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const filteredEvidence = useMemo(() => {
    const query = search.toLowerCase().trim();

    return evidence.filter((item) => {
      const matchesDomain =
        selectedDomain === "ALL" || item.domain === selectedDomain;

      const searchable = [
        item.external_id,
        item.title,
        item.domain,
        item.claim,
        item.evidence_text,
        item.strategic_implication,
      ]
        .join(" ")
        .toLowerCase();

      return matchesDomain && (!query || searchable.includes(query));
    });
  }, [evidence, selectedDomain, search]);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <div className="eyebrow">Research Intelligence</div>
          <h1>Evidence Explorer</h1>
          <p>
            Explore the external evidence supporting Strategillent's
            transformation analysis.
          </p>
        </div>
      </div>

      <div className="evidence-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search evidence..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <select
          className="domain-select"
          value={selectedDomain}
          onChange={(event) => setSelectedDomain(event.target.value)}
        >
          <option value="ALL">All domains</option>

          {domains.map((domain) => (
            <option key={domain} value={domain}>
              {domain}
            </option>
          ))}
        </select>
      </div>

      <div className="evidence-summary">
        <span>
          Showing <strong>{filteredEvidence.length}</strong> of{" "}
          <strong>{evidence.length}</strong> evidence records
        </span>
      </div>

      {loading ? (
        <div className="card empty-state">
          <p>Loading research evidence...</p>
        </div>
      ) : filteredEvidence.length === 0 ? (
        <div className="card empty-state">
          <FileText size={32} />
          <h3>No evidence found</h3>
          <p>Try changing the search term or domain filter.</p>
        </div>
      ) : (
        <div className="evidence-list">
          {filteredEvidence.map((item) => (
            <article className="card evidence-card" key={item.id}>
              <div className="evidence-card-header">
                <div>
                  <div className="evidence-id">{item.external_id}</div>

                  <h2>{item.title}</h2>

                  <div className="evidence-meta">
                    <span className="domain-badge">{item.domain}</span>

                    {item.publication_date && (
                      <span>
                        Published {item.publication_date}
                      </span>
                    )}
                  </div>
                </div>

                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="source-link"
                >
                  Source
                  <ExternalLink size={15} />
                </a>
              </div>

              <div className="evidence-section">
                <h3>Claim</h3>
                <p>{item.claim}</p>
              </div>

              <div className="evidence-section">
                <h3>Evidence</h3>
                <p>{item.evidence_text}</p>
              </div>

              <div className="evidence-section implication">
                <h3>Strategic implication</h3>
                <p>{item.strategic_implication}</p>
              </div>

              <div className="evidence-footer">
                <span>
                  Confidence: <strong>{item.confidence}/5</strong>
                </span>

                <span>
                  Relevance: <strong>{item.relevance}/5</strong>
                </span>

                <span>
                  Source: <strong>{item.research_source.source_name}</strong>
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}