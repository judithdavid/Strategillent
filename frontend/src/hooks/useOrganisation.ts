import { useEffect, useState } from "react";
import { getOrganisation } from "../services/api";
import type { Organisation } from "../types";

export function useOrganisation(organisationId?: number | null) {
  const [organisation, setOrganisation] = useState<Organisation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (organisationId == null) {
      setOrganisation(null);
      setLoading(false);
      setError(null);
      return;
    }

    // Store the narrowed value before entering the async function.
    const id = organisationId;

    async function loadOrganisation() {
      try {
        setLoading(true);
        setError(null);

        const data = await getOrganisation(id);

        setOrganisation(data);
      } catch (err) {
        setOrganisation(null);

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load organisation."
        );
      } finally {
        setLoading(false);
      }
    }

    loadOrganisation();
  }, [organisationId]);

  return {
    organisation,
    loading,
    error,
  };
}