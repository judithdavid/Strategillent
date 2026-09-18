import {
  BrowserRouter,
  NavLink,
  Route,
  Routes,
} from "react-router-dom";

import {
  LayoutDashboard,
  Building2,
  Brain,
  Lightbulb,
  Database,
  MessageSquare,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import Organisation from "./pages/Organisation";
import Intelligence from "./pages/Intelligence";
import Opportunities from "./pages/Opportunities";
import Evidence from "./pages/Evidence";
import AskIntelligence from "./pages/AskIntelligence";

import { useOrganisationContext } from "./context/OrganisationContext";

function AppContent() {
  const {
    organisations,
    selectedOrganisationId,
    selectOrganisation,
    loading,
  } = useOrganisationContext();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">STG</div>

          <div>
            <h2>Strategillent</h2>
            <span>Strategy Intelligence</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>

          <NavLink
            to="/organisation"
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <Building2 size={18} />
            Organisation
          </NavLink>

          <NavLink
            to="/intelligence"
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <Brain size={18} />
            Intelligence
          </NavLink>

          <NavLink
            to="/opportunities"
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <Lightbulb size={18} />
            Opportunities
          </NavLink>

          <NavLink
            to="/evidence"
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <Database size={18} />
            Evidence
          </NavLink>

          <NavLink
            to="/ask"
            className={({ isActive }) =>
              isActive ? "nav-item active" : "nav-item"
            }
          >
            <MessageSquare size={18} />
            Ask Intelligence
          </NavLink>
        </nav>

        
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-context">
            <span className="status-dot" />
            <span>STRATEGILLENT WORKSPACE</span>
          </div>
          <div className="topbar-meta">
            <span className="topbar-label">STRATEGILLENT</span>
            <div className="avatar">STG</div>
          </div>
        </header>

        <div className="organisation-selector">
          <label htmlFor="organisation-select">
            Organisation
          </label>

          <select
            id="organisation-select"
            value={selectedOrganisationId ?? ""}
            onChange={(event) =>
              selectOrganisation(
                Number(event.target.value)
              )
            }
            disabled={loading || organisations.length === 0}
          >
            {organisations.length === 0 ? (
              <option value="">
                No organisations
              </option>
            ) : (
              organisations.map((organisation) => (
                <option
                  key={organisation.id}
                  value={organisation.id}
                >
                  {organisation.name}
                </option>
              ))
            )}
          </select>
        </div>

        <Routes>
          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/organisation"
            element={<Organisation />}
          />

          <Route
            path="/intelligence"
            element={<Intelligence />}
          />

          <Route
            path="/opportunities"
            element={<Opportunities />}
          />

          <Route
            path="/evidence"
            element={<Evidence />}
          />

          <Route
            path="/ask"
            element={<AskIntelligence />}
          />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}