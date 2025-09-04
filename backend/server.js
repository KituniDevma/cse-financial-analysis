import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import fs from "fs";
import Papa from "papaparse";
import { GoogleGenerativeAI } from "@google/generative-ai";

dotenv.config();
const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors({ origin: "http://localhost:5173" })); // adjust if CRA = 3000
app.use(bodyParser.json());

// ✅ Initialize Gemini
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// ✅ Load CSV into memory
const file = fs.readFileSync("data/processed/clean_dataset.csv", "utf8");
const parsed = Papa.parse(file, { header: true, dynamicTyping: true }).data;

// ✅ Ask endpoint
app.post("/ask", async (req, res) => {
  try {
    const { question } = req.body;

    // Give some dataset context (first few rows)
    const context = JSON.stringify(parsed.slice(0, 20));

    // Send to Gemini
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
    const prompt = `
      You are a financial data assistant. 
      Dataset context: ${context}.
      User question: ${question}.
      Answer briefly with financial reasoning.
    `;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    res.json({ answer: text });
  } catch (err) {
    console.error("❌ Error in /ask:", err);
    res.status(500).json({ error: "Something went wrong" });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
