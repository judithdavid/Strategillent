import type {
  Organisation,
  CreateOrganisationRequest,
  Evidence,
  ResearchSource,
  IntelligenceResponse,
  QuestionResponse,
} from "../types";


const API_BASE = "/api";


async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {

  const response = await fetch(
    `${API_BASE}${endpoint}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
      ...options,
    }
  );


  if (!response.ok) {

    let message = `Request failed: ${response.status}`;

    try {
      const error = await response.json();

      if (error.detail) {
        message = error.detail;
      }

    } catch {
      // Keep default message.
    }

    throw new Error(message);
  }


  return response.json();
}


export async function getOrganisations(): Promise<
  Organisation[]
> {
  return request<Organisation[]>(
    "/organisations"
  );
}


export async function getOrganisation(
  organisationId: number
): Promise<Organisation> {

  return request<Organisation>(
    `/organisations/${organisationId}`
  );
}


export async function getEvidence(
  domain?: string
): Promise<Evidence[]> {

  const query = domain
    ? `?domain=${encodeURIComponent(domain)}`
    : "";

  return request<Evidence[]>(
    `/research/evidence${query}`
  );
}


export async function getResearchSources(): Promise<
  ResearchSource[]
> {

  return request<ResearchSource[]>(
    "/research/sources"
  );
}


export async function getResearchDomains(): Promise<
  string[]
> {

  return request<string[]>(
    "/research/domains"
  );
}


export async function getIntelligence(
  organisationId: number
): Promise<IntelligenceResponse> {

  return request<IntelligenceResponse>(
    `/intelligence/${organisationId}`
  );
}


export async function runIntelligence(
  organisationId: number
): Promise<IntelligenceResponse> {

  return request<IntelligenceResponse>(
    `/intelligence/${organisationId}/run`,
    {
      method: "POST",
    }
  );
}


export async function askQuestion(
  organisationId: number,
  question: string
): Promise<QuestionResponse> {

  return request<QuestionResponse>(
    `/questions/${organisationId}`,
    {
      method: "POST",

      body: JSON.stringify({
        question,
      }),
    }
  );
}

export async function createOrganisation(
  data: {
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
) {
  return request<Organisation>("/organisations", {
    method: "POST",
    body: JSON.stringify(data),
  });
}