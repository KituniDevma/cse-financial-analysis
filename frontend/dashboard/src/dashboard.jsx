import React, { useEffect, useState } from "react";
import Papa from "papaparse";
import { FaRobot } from "react-icons/fa";
import { MdShowChart } from "react-icons/md";
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from "recharts";
import "./dashboard.css";
import ChatBotPopup from "./chatBot"

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [company, setCompany] = useState("");
  const [companies, setCompanies] = useState([]);
  const [viewMode, setViewMode] = useState("Quarterly"); // "Quarterly" | "Annual"
  const [isChatOpen, setIsChatOpen] = useState(false);

  useEffect(() => {
    Papa.parse("/data/clean_dataset.csv", {
      download: true,
      header: true,
      dynamicTyping: true,
      complete: (results) => {
        const rows = results.data.filter((r) => r.file_name);
        setData(rows);

        const uniqueCompanies = [
          ...new Set(rows.map((r) => r.file_name.split("_")[0].toUpperCase())),
        ];
        setCompanies(uniqueCompanies);

        if (uniqueCompanies.length > 0) {
          setCompany(uniqueCompanies[0]);
        }
      },
    });
  }, []);

  // Filter selected company
  const filtered = data.filter(
    (d) => d.file_name && d.file_name.toUpperCase().startsWith(company)
  );

  // Pick latest record
  const latest = filtered.length > 0 ? filtered[0] : null;
  const latestRevenue = latest ? latest.Revenue : "N/A";
  const latestNetIncome = latest ? latest.NetIncome : "N/A";

  // --- Data aggregation ---
  // Quarterly data (sorted ascending)
  const quarterlyData = filtered
    .map((d) => ({
      quarter: d.quarter_end,
      Revenue: d.Revenue,
      NetIncome: d.NetIncome,
      GrossProfit: d.GrossProfit,
      OperatingExpenses: d.OperatingExpenses,
      OperatingIncome: d.OperatingIncome,
    }))
    .sort((a, b) => new Date(a.quarter) - new Date(b.quarter));

  // Annual aggregation
  const annualData = Object.values(
    quarterlyData.reduce((acc, row) => {
      const year = new Date(row.quarter).getFullYear();
      if (!acc[year]) {
        acc[year] = {
          quarter: year,
          Revenue: 0,
          NetIncome: 0,
          GrossProfit: 0,
          OperatingExpenses: 0,
          OperatingIncome: 0,
        };
      }
      acc[year].Revenue += row.Revenue || 0;
      acc[year].NetIncome += row.NetIncome || 0;
      acc[year].GrossProfit += row.GrossProfit || 0;
      acc[year].OperatingExpenses += row.OperatingExpenses || 0;
      acc[year].OperatingIncome += row.OperatingIncome || 0;
      return acc;
    }, {})
  ).sort((a, b) => a.quarter - b.quarter);

  const chartData = viewMode === "Quarterly" ? quarterlyData : annualData;

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="header">
        <h1>Financial Dashboard</h1>

        <div className="header-actions">
          <select
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          >
            {companies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <div className="icon" onClick={() => window.location.href = '/trend'}>
            <MdShowChart size={22} />
            <span>Trend Comparison</span>
          </div>

          {/* Chatbot toggle */}
          <div className="icon" onClick={() => setIsChatOpen(!isChatOpen)}>
            <FaRobot size={22} />
            <span>Chatbot</span>
          </div>
        </div>
        {/* Render chatbot popup */}
        {isChatOpen && <ChatBotPopup />}
      </div>

      {/* --- KPI + Line Charts --- */}
      <div className="charts-section" >
        {/* KPI Boxes */}
        <div className="summary-boxes-vertical">
          <div className="kpi-card purple">
            <h3>Revenue (Rs)</h3>
            <p className="kpi-value">{latestRevenue}</p>
            <span className="kpi-subtitle">During Last Quarter</span>
          </div>

          <div className="kpi-card purple">
            <h3>Net Income (Rs)</h3>
            <p className="kpi-value">{latestNetIncome}</p>
            <span className="kpi-subtitle">During Last Quarter</span>
          </div>
        </div>

        {/* Line Charts with Toggle */}
        <div className="line-charts-container">
          <div className="trends-header">
            <h2>Trends</h2>
            <div className="view-toggle">
              <label>View: </label>
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value)}
              >
                <option value="Quarterly">Quarterly</option>
                <option value="Annual">Annual</option>
              </select>
            </div>
          </div>

          <div className="charts-row">
            <div className="chart-card-line">
              <h3>Revenue Over Time</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="quarter" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="Revenue" stroke="#a6a2e5ff" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card-line">
              <h3>Net Income Over Time</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 20 }} >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="quarter" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="NetIncome" stroke="#f19ce4ff" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* --- Bar Charts Row --- */}
      <div className="charts-row">
        <div className="chart-card-bar">
          <h3>Gross Profit Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quarter" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="GrossProfit" fill="#eb88caff" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card-bar">
          <h3>Operating Expenses Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quarter" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="OperatingExpenses" fill="#ff6188ff" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card-bar">
          <h3>Operating Income Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 40, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="quarter" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="OperatingIncome" fill="#c49dfbff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
