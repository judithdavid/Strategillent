import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";

import { getOrganisations } from "../services/api";
import type { Organisation } from "../types";

interface OrganisationContextValue {
  organisations: Organisation[];
  selectedOrganisation: Organisation | null;
  selectedOrganisationId: number | null;
  loading: boolean;

  selectOrganisation: (id: number) => void;
  refreshOrganisations: () => Promise<void>;
}

const OrganisationContext =
  createContext<OrganisationContextValue | null>(null);

export function OrganisationProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [organisations, setOrganisations] = useState<Organisation[]>([]);
  const [selectedOrganisationId, setSelectedOrganisationId] =
    useState<number | null>(null);

  const [loading, setLoading] = useState(true);

  async function refreshOrganisations() {
    try {
      setLoading(true);

      const data = await getOrganisations();

      setOrganisations(data);

      if (data.length === 0) {
        setSelectedOrganisationId(null);
        localStorage.removeItem("strategillent_organisation_id");
        return;
      }

      const savedId = localStorage.getItem(
        "strategillent_organisation_id"
      );

      const savedOrganisation = savedId
        ? data.find((org) => org.id === Number(savedId))
        : null;

      if (savedOrganisation) {
        setSelectedOrganisationId(savedOrganisation.id);
      } else {
        setSelectedOrganisationId(data[0].id);

        localStorage.setItem(
          "strategillent_organisation_id",
          String(data[0].id)
        );
      }
    } catch (error) {
      console.error(
        "Failed to load organisations:",
        error
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshOrganisations();
  }, []);

  function selectOrganisation(id: number) {
    setSelectedOrganisationId(id);

    localStorage.setItem(
      "strategillent_organisation_id",
      String(id)
    );
  }

  const selectedOrganisation =
    organisations.find(
      (organisation) =>
        organisation.id === selectedOrganisationId
    ) ?? null;

  return (
    <OrganisationContext.Provider
      value={{
        organisations,
        selectedOrganisation,
        selectedOrganisationId,
        loading,
        selectOrganisation,
        refreshOrganisations,
      }}
    >
      {children}
    </OrganisationContext.Provider>
  );
}

export function useOrganisationContext() {
  const context = useContext(OrganisationContext);

  if (context === null) {
    throw new Error(
      "useOrganisationContext must be used inside OrganisationProvider"
    );
  }

  return context;
}