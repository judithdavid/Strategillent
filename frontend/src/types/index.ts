export interface Organisation {
  id: number;
  name: string;
  fictional: boolean;
  industry: string;
  business_model: string[];
  markets: string[];
  customers: number | null;
  employees: number | null;
  products: string[];
  challenges: string[];
}


export interface ResearchSource {
  id: number;
  source_name: string;
  source_type: string;
  url: string;
  publication_date: string | null;
}


export interface Evidence {
  id: number;
  external_id: string;
  domain: string;
  title: string;
  publication_date: string | null;
  url: string;
  claim: string;
  evidence_text: string;
  strategic_implication: string;
  confidence: number;
  relevance: number;
  tags: string[];
  research_source: ResearchSource;
}


export interface EvidenceSummary {
  id: number;
  external_id: string;
  domain: string;
  title: string;
}


export interface StrategicIssue {
  id: number;
  title: string;
  description: string;
  rationale: string | null;
  severity: number;
  urgency: number;
  model_used: string | null;
  analysis_version: string | null;
  evidence: EvidenceSummary[];
}


export interface Opportunity {
  id: number;
  title: string;
  description: string;
  rationale: string | null;

  business_impact: number;
  feasibility: number;
  urgency: number;
  strategic_alignment: number;
  evidence_confidence: number;

  priority_score: number | null;
  priority_rank: number | null;

  model_used: string | null;
  analysis_version: string | null;

  evidence: EvidenceSummary[];
  initiatives: Initiative[];
}


export interface Initiative {
  id: number;
  name: string;
  description: string;
  expected_outcome: string | null;
  success_metric: string | null;
  implementation_phase: string | null;
  status: string;
  model_used: string | null;
  analysis_version: string | null;
}


export interface IntelligenceResponse {
  organisation_id: number;
  organisation_name: string;
  analysis_run_id: number | null;
  strategic_issues: StrategicIssue[];
  opportunities: Opportunity[];
  initiatives: Initiative[];
}


export interface QuestionResponse {
  question: string;
  answer: string;
  evidence_ids: string[];
  model_used: string | null;
}

export interface CreateOrganisationRequest {
  name: string;
  fictional: boolean;
  industry: string;
  business_model: string[];
  markets: string[];
  customers: number | null;
  employees: number | null;
  products: string[];
  challenges: string[];
}