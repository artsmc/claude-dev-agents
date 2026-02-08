/**
 * Test fixture: JavaScript injection vulnerabilities.
 *
 * THIS FILE CONTAINS INTENTIONALLY VULNERABLE CODE FOR TESTING PURPOSES.
 * All code patterns are designed to validate the InjectionAnalyzer's
 * JavaScript SQL injection and code injection detection capabilities.
 *
 * Expected detections by InjectionAnalyzer:
 *   - sql-injection (HIGH, line ~20) - Sequelize raw query concatenation
 *   - sql-injection (HIGH, line ~26) - Template literal SQL injection
 *   - code-injection (HIGH, line ~31) - eval usage
 *   - code-injection (HIGH, line ~36) - new Function constructor
 *   - sql-injection (HIGH, line ~41) - String concatenation SQL
 *
 * Total expected findings: 5
 */

const { Sequelize } = require("sequelize");

// VULN: SQL injection via Sequelize raw query with string concatenation
async function getUserUnsafe(sequelize, userId) {
  const result = await sequelize.query("SELECT * FROM users WHERE id = " + userId);
  return result;
}

// VULN: SQL injection via template literal interpolation
async function searchUsers(db, searchTerm) {
  const query = `SELECT * FROM users WHERE name LIKE '%${searchTerm}%'`;
  return db.query(query);
}

// VULN: Code injection via eval
function dynamicCalculate(expression) {
  return eval(expression);
}

// VULN: Code injection via new Function constructor
function createDynamicFunction(body) {
  const fn = new Function("x", body);
  return fn;
}

// VULN: SQL injection via string concatenation
function buildQuery(table, condition) {
  const query = "SELECT * FROM " + table + " WHERE " + condition;
  return query;
}

// Safe: Parameterized query (should NOT be flagged)
async function getUserSafe(sequelize, userId) {
  const result = await sequelize.query(
    "SELECT * FROM users WHERE id = ?",
    { replacements: [userId] }
  );
  return result;
}

// Safe: JSON.parse instead of eval
function parseData(jsonString) {
  return JSON.parse(jsonString);
}
