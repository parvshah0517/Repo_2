import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import dashboardRoutes from "./routes/dashboard.routes.js";

dotenv.config();

const app = express();
const PORT = Number(process.env.PORT) || 5000;

app.use(cors());
app.use(express.json());

app.get("/api/health", (_req, res) => {
  res.json({
    status: "ok",
    message: "Analytics Dashboard API is running"
  });
});

app.use("/api/dashboard", dashboardRoutes);
app.get("/", (_req, res) => {
  res.send("Analytics Dashboard API is running");
});
app.listen(PORT, () => {
  console.log(`Backend running at http://localhost:${PORT}`);
});