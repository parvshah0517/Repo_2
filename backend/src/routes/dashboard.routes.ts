
import { Router } from "express";
import pool from "../data/db.js";

const router = Router();

router.get("/summary", async (_req, res, next) => {
  try {
    const [userRows] = await pool.query(`
      SELECT
        COUNT(*) AS totalUsers,
        COALESCE(SUM(status = 'active'), 0) AS activeUsers
      FROM users
    `);

    const [eventRows] = await pool.query(`
      SELECT
        COALESCE(SUM(event_type = 'page_view'), 0) AS pageViews,
        COALESCE(SUM(event_type = 'login'), 0) AS sessions
      FROM activity_events
    `);

    const users = (userRows as Array<{
      totalUsers: number;
      activeUsers: number;
    }>)[0];

    const events = (eventRows as Array<{
      pageViews: number;
      sessions: number;
    }>)[0];

    res.json({
      totalUsers: Number(users.totalUsers),
      activeUsers: Number(users.activeUsers),
      pageViews: Number(events.pageViews),
      sessions: Number(events.sessions),
      // Bounce rate requires session-level tracking.
      // Keep this as a clearly temporary placeholder until then.
      bounceRate: 38.5
    });
  } catch (error) {
    next(error);
  }
});

router.get("/traffic", async (_req, res, next) => {
  try {
    const [rows] = await pool.query(`
      SELECT
        DATE_FORMAT(created_at, '%Y-%m-%d') AS date,
        COUNT(*) AS visitors
      FROM activity_events
      WHERE event_type = 'page_view'
        AND created_at >= CURRENT_DATE - INTERVAL 6 DAY
        AND created_at < CURRENT_DATE + INTERVAL 1 DAY
      GROUP BY DATE(created_at)
      ORDER BY DATE(created_at)
    `);

    res.json(rows);
  } catch (error) {
    next(error);
  }
});

router.get("/activity", async (req, res, next) => {
  try {
    const limit = Math.min(
      Math.max(Number.parseInt(String(req.query.limit ?? "20"), 10) || 20, 1),
      100
    );

    const [rows] = await pool.execute(
      `SELECT
         e.id,
         u.name AS user,
         e.event_type AS action,
         e.page,
         e.created_at AS timestamp
       FROM activity_events e
       JOIN users u ON u.id = e.user_id
       ORDER BY e.created_at DESC
       LIMIT ?`,
      [limit]
    );

    res.json(rows);
  } catch (error) {
    next(error);
  }
});

export default router;
