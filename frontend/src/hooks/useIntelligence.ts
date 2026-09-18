import { useEffect, useState } from "react";
import {
  getIntelligence,
  runIntelligence,
} from "../services/api";

import type { IntelligenceResponse } from "../types";

export function useIntelligence(organisationId: number | null) {
  const [intelligence, setIntelligence] =
    useState<IntelligenceResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadIntelligence() {
    if (!organisationId) {
      setIntelligence(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = await getIntelligence(organisationId);
      setIntelligence(data);
    } catch (err) {
      setIntelligence(null);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load intelligence."
      );
    } finally {
      setLoading(false);
    }
  }

  async function runAnalysis() {
    if (!organisationId) {
      return;
    }

    try {
      setRunning(true);
      setError(null);

      const data = await runIntelligence(organisationId);
      setIntelligence(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to run intelligence analysis."
      );
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    loadIntelligence();
  }, [organisationId]);

  return {
    intelligence,
    loading,
    running,
    error,

    // New name
    runAnalysis,

    // Compatibility with existing pages
    executeAnalysis: runAnalysis,

    loadIntelligence,
  };
}