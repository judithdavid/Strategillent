import { useState, type FormEvent } from "react";

import { createOrganisation } from "../services/api";
import { useOrganisationContext } from "../context/OrganisationContext";
import { useOrganisation } from "../hooks/useOrganisation";

export default function Organisation() {
  const {
    selectedOrganisationId,
    organisations,
    selectOrganisation,
    refreshOrganisations,
  } = useOrganisationContext();

  const {
    organisation,
    loading,
    error,
  } = useOrganisation(selectedOrganisationId);

  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [form, setForm] = useState({
    name: "",
    industry: "",
    customers: "",
    employees: "",
    business_model: "",
    markets: "",
    products: "",
    challenges: "",
  });

  function updateField(
    field: keyof typeof form,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    try {
      setCreating(true);
      setFormError(null);

      if (!form.name.trim()) {
        throw new Error("Organisation name is required.");
      }

      if (!form.industry.trim()) {
        throw new Error("Industry is required.");
      }

      const payload = {
        name: form.name.trim(),
        fictional: true,
        industry: form.industry.trim(),

        business_model: form.business_model
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),

        markets: form.markets
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),

        products: form.products
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean),

        customers: form.customers
          ? Number(form.customers)
          : null,

        employees: form.employees
          ? Number(form.employees)
          : null,

        challenges: form.challenges
          .split("\n")
          .map((item) => item.trim())
          .filter(Boolean),
      };

      const created = await createOrganisation(payload);

      await refreshOrganisations();

      selectOrganisation(created.id);

      setForm({
        name: "",
        industry: "",
        customers: "",
        employees: "",
        business_model: "",
        markets: "",
        products: "",
        challenges: "",
      });

      setShowForm(false);
    } catch (err) {
      setFormError(
        err instanceof Error
          ? err.message
          : "Failed to create organisation."
      );
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="page organisation-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <div className="dashboard-header">

        <div>
          <p className="eyebrow">ORGANISATION</p>

          <h1>Organisation Input</h1>

          <p className="page-description">
            Create and manage the organisations analysed by
            Strategillent.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => {
            setFormError(null);
            setShowForm(true);
          }}
        >
          + New Organisation
        </button>

      </div>


      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <div className="organisation-layout">

        {/* ===================================================
            LEFT COLUMN
            =================================================== */}

        <main className="organisation-main">

          {/* SELECT ORGANISATION */}

          <section className="organisation-card organisation-selector-card">

            <div>
              <p className="eyebrow">WORKSPACE</p>

              <h2>Select Organisation</h2>

              <p>
                Choose an organisation to view its strategic
                context.
              </p>
            </div>

            <select
              value={selectedOrganisationId ?? ""}
              onChange={(event) =>
                selectOrganisation(
                  Number(event.target.value)
                )
              }
              disabled={
                loading ||
                organisations.length === 0
              }
            >
              {organisations.length === 0 ? (
                <option value="">
                  No organisations
                </option>
              ) : (
                organisations.map((item) => (
                  <option
                    key={item.id}
                    value={item.id}
                  >
                    {item.name}
                  </option>
                ))
              )}
            </select>

          </section>


          {/* LOADING */}

          {loading && (
            <div className="empty-state">
              <p>Loading organisation...</p>
            </div>
          )}


          {/* ERROR */}

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          {/* =================================================
              SELECTED ORGANISATION
              ================================================= */}

          {organisation && !loading && (
            <>

              {/* PROFILE */}

              <section className="organisation-card profile-card">

                <div className="profile-header">

                  <div className="organisation-avatar">
                    {organisation.name
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div className="profile-title">

                    <div className="profile-name-row">

                      <h2>
                        {organisation.name}
                      </h2>

                      {organisation.fictional && (
                        <span className="status">
                          Fictional
                        </span>
                      )}

                    </div>

                    <p>
                      {organisation.industry}
                    </p>

                  </div>

                </div>


                {/* KEY METRICS */}

                <div className="organisation-metrics">

                  <div className="organisation-metric">

                    <span>
                      Industry
                    </span>

                    <strong>
                      {organisation.industry}
                    </strong>

                  </div>


                  <div className="organisation-metric">

                    <span>
                      Customers
                    </span>

                    <strong>
                      {organisation.customers
                        ?.toLocaleString() ?? "—"}
                    </strong>

                  </div>


                  <div className="organisation-metric">

                    <span>
                      Employees
                    </span>

                    <strong>
                      {organisation.employees
                        ?.toLocaleString() ?? "—"}
                    </strong>

                  </div>

                </div>


                {/* ORGANISATION CONTEXT */}

                <div className="organisation-context-grid">

                  {/* MARKETS */}

                  <div>

                    <span className="detail-label">
                      Markets
                    </span>

                    <div className="tag-list">

                      {organisation.markets?.map(
                        (market) => (
                          <span
                            className="tag"
                            key={market}
                          >
                            {market}
                          </span>
                        )
                      )}

                    </div>

                  </div>


                  {/* BUSINESS MODEL */}

                  <div>

                    <span className="detail-label">
                      Business Model
                    </span>

                    <div className="tag-list">

                      {organisation.business_model?.map(
                        (item) => (
                          <span
                            className="tag"
                            key={item}
                          >
                            {item}
                          </span>
                        )
                      )}

                    </div>

                  </div>


                  {/* PRODUCTS */}

                  <div className="context-full">

                    <span className="detail-label">
                      Products
                    </span>

                    <div className="tag-list">

                      {organisation.products?.map(
                        (product) => (
                          <span
                            className="tag"
                            key={product}
                          >
                            {product}
                          </span>
                        )
                      )}

                    </div>

                  </div>

                </div>

              </section>


              {/* =================================================
                  BUSINESS CHALLENGES
                  ================================================= */}

              <section className="organisation-card">

                <div className="section-heading-row">

                  <div>

                    <p className="eyebrow">
                      STRATEGIC CONTEXT
                    </p>

                    <h2>
                      Known Business Challenges
                    </h2>

                  </div>

                  <span className="count-badge">
                    {organisation.challenges?.length ?? 0}
                  </span>

                </div>


                <div className="challenge-grid">

                  {organisation.challenges?.map(
                    (challenge, index) => (
                      <div
                        className="challenge-item"
                        key={challenge}
                      >

                        <span className="challenge-number">
                          {String(index + 1).padStart(
                            2,
                            "0"
                          )}
                        </span>

                        <span>
                          {challenge}
                        </span>

                      </div>
                    )
                  )}

                </div>

              </section>

            </>
          )}

        </main>


        {/* ===================================================
            RIGHT COLUMN
            =================================================== */}

        <aside className="organisation-side">

          {/* ORGANISATION COUNT */}

          <section className="organisation-card stat-card">

            <span className="stat-icon">
              ◈
            </span>

            <div>

              <span className="detail-label">
                Total Organisations
              </span>

              <strong>
                {organisations.length}
              </strong>

              <p>
                Organisations in your workspace
              </p>

            </div>

          </section>


          {/* ORGANISATION LIST */}

          <section className="organisation-card">

            <p className="eyebrow">
              WORKSPACE
            </p>

            <h2>
              All Organisations
            </h2>

            <p className="card-description">
              Select an organisation to view
              its details.
            </p>


            <div className="organisation-list">

              {organisations.map((item) => (

                <button
                  key={item.id}
                  className={
                    item.id === selectedOrganisationId
                      ? "organisation-item active"
                      : "organisation-item"
                  }
                  onClick={() =>
                    selectOrganisation(item.id)
                  }
                >

                  <span className="organisation-item-avatar">
                    {item.name
                      .charAt(0)
                      .toUpperCase()}
                  </span>


                  <span className="organisation-item-info">

                    <strong>
                      {item.name}
                    </strong>

                    <small>
                      {item.industry}
                    </small>

                  </span>


                  {item.id === selectedOrganisationId && (
                    <span className="selected-badge">
                      ✓
                    </span>
                  )}

                </button>

              ))}

            </div>

          </section>

        </aside>

      </div>


      {/* =====================================================
          CREATE ORGANISATION MODAL
          ===================================================== */}

      {showForm && (

        <div
          className="modal-overlay"
          onClick={() => {
            if (!creating) {
              setShowForm(false);
            }
          }}
        >

          <div
            className="modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            {/* MODAL HEADER */}

            <div className="modal-header">

              <div>

                <p className="eyebrow">
                  NEW ORGANISATION
                </p>

                <h2>
                  Create Organisation
                </h2>

              </div>


              <button
                className="modal-close"
                onClick={() =>
                  setShowForm(false)
                }
                disabled={creating}
                type="button"
              >
                ×
              </button>

            </div>


            {/* FORM ERROR */}

            {formError && (
              <div className="error-message">
                {formError}
              </div>
            )}


            {/* FORM */}

            <form onSubmit={handleSubmit}>

              <div className="form-grid">

                {/* NAME */}

                <div className="form-group">

                  <label>
                    Organisation Name *
                  </label>

                  <input
                    type="text"
                    value={form.name}
                    onChange={(event) =>
                      updateField(
                        "name",
                        event.target.value
                      )
                    }
                    placeholder="e.g. FinNova"
                    required
                  />

                </div>


                {/* INDUSTRY */}

                <div className="form-group">

                  <label>
                    Industry *
                  </label>

                  <input
                    type="text"
                    value={form.industry}
                    onChange={(event) =>
                      updateField(
                        "industry",
                        event.target.value
                      )
                    }
                    placeholder="e.g. Fintech"
                    required
                  />

                </div>


                {/* CUSTOMERS */}

                <div className="form-group">

                  <label>
                    Customers
                  </label>

                  <input
                    type="number"
                    value={form.customers}
                    onChange={(event) =>
                      updateField(
                        "customers",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 12000000"
                  />

                </div>


                {/* EMPLOYEES */}

                <div className="form-group">

                  <label>
                    Employees
                  </label>

                  <input
                    type="number"
                    value={form.employees}
                    onChange={(event) =>
                      updateField(
                        "employees",
                        event.target.value
                      )
                    }
                    placeholder="e.g. 2500"
                  />

                </div>


                {/* BUSINESS MODEL */}

                <div className="form-group form-full">

                  <label>
                    Business Model
                  </label>

                  <input
                    type="text"
                    value={form.business_model}
                    onChange={(event) =>
                      updateField(
                        "business_model",
                        event.target.value
                      )
                    }
                    placeholder="Digital payments, Consumer lending"
                  />

                </div>


                {/* MARKETS */}

                <div className="form-group">

                  <label>
                    Markets
                  </label>

                  <input
                    type="text"
                    value={form.markets}
                    onChange={(event) =>
                      updateField(
                        "markets",
                        event.target.value
                      )
                    }
                    placeholder="India, Southeast Asia"
                  />

                </div>


                {/* PRODUCTS */}

                <div className="form-group">

                  <label>
                    Products
                  </label>

                  <input
                    type="text"
                    value={form.products}
                    onChange={(event) =>
                      updateField(
                        "products",
                        event.target.value
                      )
                    }
                    placeholder="Payments, Loans, Wallet"
                  />

                </div>


                {/* CHALLENGES */}

                <div className="form-group form-full">

                  <label>
                    Business Challenges
                  </label>

                  <textarea
                    value={form.challenges}
                    onChange={(event) =>
                      updateField(
                        "challenges",
                        event.target.value
                      )
                    }
                    placeholder={
                      "Enter one challenge per line.\n\nRising fraud\nSlow lending decisions\nHigh support volume"
                    }
                    rows={5}
                  />

                </div>

              </div>


              {/* MODAL ACTIONS */}

              <div className="modal-actions">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowForm(false)
                  }
                  disabled={creating}
                >
                  Cancel
                </button>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={creating}
                >
                  {creating
                    ? "Creating..."
                    : "Create Organisation"}
                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </div>
  );
}