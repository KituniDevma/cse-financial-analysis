import React, { useEffect, useState } from "react";
import Papa from "papaparse";
import { FaRobot } from "react-icons/fa";
import { MdShowChart } from "react-icons/md";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./trendDashboard.css";

export default function TrendDashboard() {
  const [data, setData] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [viewMode, setViewMode] = useState("Quarterly");

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
        setCompanies(uniqueCompanies.slice(0, 2)); // first 2 companies for comparison
      },
    });
  }, []);

  // Group by company
  const groupByCompany = {};
  companies.forEach((c) => {
    groupByCompany[c] = data
      .filter((d) => d.file_name && d.file_name.toUpperCase().startsWith(c))
      .map((d) => ({
        quarter: d.quarter_end,
        Revenue: d.Revenue,
        NetIncome: d.NetIncome,
        GrossProfit: d.GrossProfit,
        OperatingExpenses: d.OperatingExpenses,
        OperatingIncome: d.OperatingIncome,
      }))
      .sort((a, b) => new Date(a.quarter) - new Date(b.quarter));
  });

  // Merge data for comparison charts
  const mergedData = [];
  if (companies.length === 2) {
    const allQuarters = [
      ...new Set(
        [...groupByCompany[companies[0]], ...groupByCompany[companies[1]]].map(
          (d) => d.quarter
        )
      ),
    ].sort((a, b) => new Date(a) - new Date(b));

    allQuarters.forEach((q) => {
      const row = { quarter: q };
      companies.forEach((c) => {
        const entry = groupByCompany[c].find((d) => d.quarter === q);
        if (entry) {
          row[`${c}_Revenue`] = entry.Revenue || 0;
          row[`${c}_NetIncome`] = entry.NetIncome || 0;
        }
      });
      mergedData.push(row);
    });
  }

  // Latest values
  const latestValues = {};
  companies.forEach((c) => {
    const list = groupByCompany[c];
    latestValues[c] = list && list.length > 0 ? list[list.length - 1] : {};
  });

  // Color map for companies
  const companyColors = {
    [companies[0]]: "#6a5acd", // purple
    [companies[1]]: "#c85b91ff", // pink
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="header">
        <h1>Financial Dashboard</h1>
        <div className="header-actions">
          <div className="icon">
            <MdShowChart size={22} />
            <span>Trend Comparison</span>
          </div>
          <div className="icon">
            <FaRobot size={22} />
            <span>Chatbot</span>
          </div>
        </div>
      </div>

      {/* KPI + Trends side by side */}
      <div className="charts-section">
        {/* KPI Boxes */}
        <div className="summary-boxes-vertical">
          {companies.map((c) => (
            <React.Fragment key={c}>
              <div
                className="kpi-card"
                style={{ backgroundColor: companyColors[c] || "#a95ba0ff" }}
              >
                <h3>{c} Revenue (Rs)</h3>
                <p className="kpi-value">{latestValues[c]?.Revenue || "N/A"}</p>
                <span className="kpi-subtitle">During Last Quarter</span>
              </div>

              <div
                className="kpi-card"
                style={{ backgroundColor: companyColors[c] || "#6a5acd" }}
              >
                <h3>{c} Net Income (Rs)</h3>
                <p className="kpi-value">{latestValues[c]?.NetIncome || "N/A"}</p>
                <span className="kpi-subtitle">During Last Quarter</span>
              </div>
            </React.Fragment>
          ))}
        </div>

        {/* Trends */}
        <div className="trends-container">
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

          {/* Revenue Comparison */}
          <div className="chart-card-line">
            <h3>Revenue Comparison</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={mergedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="quarter" />
                <YAxis />
                <Tooltip />
                <Legend />
                {companies.map((c, i) => (
                  <Line
                    key={c}
                    type="monotone"
                    dataKey={`${c}_Revenue`}
                    stroke={i === 0 ? "#6a5acd" : "#ff69b4"}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Net Income Comparison */}
          <div className="chart-card-line">
            <h3>Net Income Comparison</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={mergedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="quarter" />
                <YAxis />
                <Tooltip />
                <Legend />
                {companies.map((c, i) => (
                  <Line
                    key={c}
                    type="monotone"
                    dataKey={`${c}_NetIncome`}
                    stroke={i === 0 ? "#6a5acd" : "#ff69b4"}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
