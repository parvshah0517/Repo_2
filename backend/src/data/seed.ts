
import { faker } from "@faker-js/faker";
import pool from "./db.js";

function toMysqlDate(date: Date): string {
  return date.toISOString().slice(0, 19).replace("T", " ");
}

async function seed() {
  const connection = await pool.getConnection();

  try {
    await connection.query(`
      CREATE TABLE IF NOT EXISTS users (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(120) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_users_status (status),
        INDEX idx_users_created_at (created_at)
      )
    `);

    await connection.query(`
      CREATE TABLE IF NOT EXISTS activity_events (
        id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT UNSIGNED NOT NULL,
        event_type VARCHAR(60) NOT NULL,
        page VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL,
        CONSTRAINT fk_activity_user
          FOREIGN KEY (user_id) REFERENCES users(id)
          ON DELETE CASCADE,
        INDEX idx_events_created_at (created_at),
        INDEX idx_events_user_created (user_id, created_at),
        INDEX idx_events_type_created (event_type, created_at)
      )
    `);

    // This script resets only the sample data in these two tables.
    await connection.query("SET FOREIGN_KEY_CHECKS = 0");
    await connection.query("TRUNCATE TABLE activity_events");
    await connection.query("TRUNCATE TABLE users");
    await connection.query("SET FOREIGN_KEY_CHECKS = 1");

    const userRows: Array<[string, string, string, string]> = [];

    for (let i = 0; i < 500; i++) {
      const name = faker.person.fullName();
      const email = `user${i + 1}@example.com`;
      const status = Math.random() < 0.72 ? "active" : "inactive";
      const createdAt = toMysqlDate(
        faker.date.between({
          from: new Date("2025-01-01T00:00:00Z"),
          to: new Date()
        })
      );

      userRows.push([name, email, status, createdAt]);
    }

    for (let i = 0; i < userRows.length; i += 250) {
      const batch = userRows.slice(i, i + 250);
      await connection.query(
        "INSERT INTO users (name, email, status, created_at) VALUES ?",
        [batch]
      );
    }

    const [users] = await connection.query(
      "SELECT id FROM users"
    ) as [Array<{ id: number }>, unknown];

    const eventTypes = [
      "login",
      "page_view",
      "report_view",
      "search",
      "logout",
      "download"
    ];

    const pages = [
      "/dashboard",
      "/reports",
      "/users",
      "/settings",
      "/analytics",
      "/login"
    ];

    const eventRows: Array<[number, string, string, string]> = [];

    for (const user of users) {
      for (let j = 0; j < 20; j++) {
        const eventDate = faker.date.recent({ days: 30 });

        eventRows.push([
          user.id,
          faker.helpers.arrayElement(eventTypes),
          faker.helpers.arrayElement(pages),
          toMysqlDate(eventDate)
        ]);
      }
    }

    for (let i = 0; i < eventRows.length; i += 500) {
      const batch = eventRows.slice(i, i + 500);

      await connection.query(
        `INSERT INTO activity_events
          (user_id, event_type, page, created_at)
         VALUES ?`,
        [batch]
      );
    }

    console.log(`Seed completed: ${userRows.length} users`);
    console.log(`Seed completed: ${eventRows.length} activity events`);
  } finally {
    connection.release();
    await pool.end();
  }
}

seed().catch((error) => {
  console.error("Database seeding failed:", error);
  process.exitCode = 1;
});
