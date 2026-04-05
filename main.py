import express from "express";
import { z } from "zod";

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3000;

const db = {
  operations: [],
  operationLogs: [],
};

let operationIdCounter = 1;

app.post("/api/roblox/join", (req, res) => {
  try {
    const { inviteCode, tokenIds, userId } = req.body;

    if (!inviteCode || !tokenIds || !userId) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const operationId = operationIdCounter++;

    db.operations.push({
      id: operationId,
      userId: userId,
      type: "join",
      status: "pending",
      targetId: inviteCode,
      tokenCount: tokenIds.length,
      createdAt: new Date(),
    });

    for (const tokenId of tokenIds) {
      db.operationLogs.push({
        operationId: operationId,
        tokenId: tokenId,
        status: "pending",
        message: "Queued for execution",
        createdAt: new Date(),
      });
    }

    res.json({
      success: true,
      operationId: operationId,
      message: "Join operation started",
    });
  } catch (error) {
    console.error("Join error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.post("/api/roblox/leave", (req, res) => {
  try {
    const { guildId, tokenIds, userId } = req.body;

    if (!guildId || !tokenIds || !userId) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const operationId = operationIdCounter++;

    db.operations.push({
      id: operationId,
      userId: userId,
      type: "leave",
      status: "pending",
      targetId: guildId,
      tokenCount: tokenIds.length,
      createdAt: new Date(),
    });

    for (const tokenId of tokenIds) {
      db.operationLogs.push({
        operationId: operationId,
        tokenId: tokenId,
        status: "pending",
        message: "Queued for execution",
        createdAt: new Date(),
      });
    }

    res.json({
      success: true,
      operationId: operationId,
      message: "Leave operation started",
    });
  } catch (error) {
    console.error("Leave error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.post("/api/roblox/spam", (req, res) => {
  try {
    const { channelId, message, tokenIds, userId } = req.body;

    if (!channelId || !message || !tokenIds || !userId) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    const operationId = operationIdCounter++;

    db.operations.push({
      id: operationId,
      userId: userId,
      type: "spam",
      status: "pending",
      targetId: channelId,
      tokenCount: tokenIds.length,
      metadata: { message: message },
      createdAt: new Date(),
    });

    for (const tokenId of tokenIds) {
      db.operationLogs.push({
        operationId: operationId,
        tokenId: tokenId,
        status: "pending",
        message: "Queued for execution",
        createdAt: new Date(),
      });
    }

    res.json({
      success: true,
      operationId: operationId,
      message: "Spam operation started",
    });
  } catch (error) {
    console.error("Spam error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/api/roblox/operation/:id", (req, res) => {
  try {
    const operationId = parseInt(req.params.id);

    const operation = db.operations.find((op) => op.id === operationId);

    if (!operation) {
      return res.status(404).json({ error: "Operation not found" });
    }

    const logs = db.operationLogs.filter(
      (log) => log.operationId === operationId
    );

    const successCount = logs.filter((l) => l.status === "success").length;
    const failureCount = logs.filter((l) => l.status === "failed").length;
    const captchaCount = logs.filter((l) =>
      l.message.includes("captcha")
    ).length;
    const cloudflareCount = logs.filter((l) =>
      l.message.includes("cloudflare")
    ).length;

    res.json({
      id: operation.id,
      type: operation.type,
      status: operation.status,
      tokenCount: operation.tokenCount,
      successCount: successCount,
      failureCount: failureCount,
      captchaCount: captchaCount,
      cloudflareCount: cloudflareCount,
      createdAt: operation.createdAt,
    });
  } catch (error) {
    console.error("Get operation error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/api/roblox/operation/:id/logs", (req, res) => {
  try {
    const operationId = parseInt(req.params.id);

    const logs = db.operationLogs.filter(
      (log) => log.operationId === operationId
    );

    res.json({
      logs: logs.map((log) => ({
        tokenId: log.tokenId,
        status: log.status,
        message: log.message,
        createdAt: log.createdAt,
      })),
    });
  } catch (error) {
    console.error("Get logs error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date() });
});

app.listen(PORT, () => {
  console.log(`CWELIUM API running on port ${PORT}`);
});

export default app;
