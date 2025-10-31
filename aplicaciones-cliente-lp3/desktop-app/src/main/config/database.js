const fs = require('fs');
const path = require('path');
const { app } = require('electron');

class DatabaseManager {
  constructor() {
    this.dbPath = path.join(app.getPath('userData'), 'banco.db');
    this.db = null;
    this.init();
  }

  async init() {
    try {
      const sqlite3 = require('sqlite3').verbose();
      
      // Crear directorio si no existe
      const dbDir = path.dirname(this.dbPath);
      if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
      }

      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          console.error('Error opening database:', err.message);
        } else {
          console.log('Connected to SQLite database');
          this.createTables();
        }
      });
    } catch (error) {
      console.error('Error initializing database:', error);
    }
  }

  createTables() {
    const tables = {
      users: `
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          email TEXT UNIQUE NOT NULL,
          full_name TEXT NOT NULL,
          dni TEXT UNIQUE NOT NULL,
          phone TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `,
      accounts: `
        CREATE TABLE IF NOT EXISTS accounts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          account_number TEXT UNIQUE NOT NULL,
          account_type TEXT NOT NULL,
          balance DECIMAL(15,2) DEFAULT 0.00,
          status TEXT DEFAULT 'active',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `,
      transactions: `
        CREATE TABLE IF NOT EXISTS transactions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          account_id INTEGER NOT NULL,
          transaction_type TEXT NOT NULL,
          amount DECIMAL(15,2) NOT NULL,
          description TEXT,
          reference_number TEXT UNIQUE,
          status TEXT DEFAULT 'pending',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
      `,
      loans: `
        CREATE TABLE IF NOT EXISTS loans (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          loan_type TEXT NOT NULL,
          amount DECIMAL(15,2) NOT NULL,
          interest_rate DECIMAL(5,2) NOT NULL,
          term_months INTEGER NOT NULL,
          monthly_payment DECIMAL(15,2) NOT NULL,
          status TEXT DEFAULT 'pending',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users (id)
        )
      `,
      qr_codes: `
        CREATE TABLE IF NOT EXISTS qr_codes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          account_id INTEGER NOT NULL,
          qr_data TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
      `
    };

    Object.entries(tables).forEach(([tableName, sql]) => {
      this.db.run(sql, (err) => {
        if (err) {
          console.error(`Error creating table ${tableName}:`, err.message);
        } else {
          console.log(`Table ${tableName} created or already exists`);
        }
      });
    });
  }

  async query(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  async run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function(err) {
        if (err) {
          reject(err);
        } else {
          resolve({ id: this.lastID, changes: this.changes });
        }
      });
    });
  }

  async create(table, data) {
    const columns = Object.keys(data).join(', ');
    const placeholders = Object.keys(data).map(() => '?').join(', ');
    const values = Object.values(data);

    const sql = `INSERT INTO ${table} (${columns}) VALUES (${placeholders})`;
    return await this.run(sql, values);
  }

  async read(table, conditions = {}) {
    let sql = `SELECT * FROM ${table}`;
    const params = [];

    if (Object.keys(conditions).length > 0) {
      const whereClause = Object.keys(conditions)
        .map(key => `${key} = ?`)
        .join(' AND ');
      sql += ` WHERE ${whereClause}`;
      params.push(...Object.values(conditions));
    }

    return await this.query(sql, params);
  }

  async update(table, data, conditions) {
    const setClause = Object.keys(data)
      .map(key => `${key} = ?`)
      .join(', ');
    const whereClause = Object.keys(conditions)
      .map(key => `${key} = ?`)
      .join(' AND ');
    
    const sql = `UPDATE ${table} SET ${setClause} WHERE ${whereClause}`;
    const params = [...Object.values(data), ...Object.values(conditions)];

    return await this.run(sql, params);
  }

  async delete(table, conditions) {
    const whereClause = Object.keys(conditions)
      .map(key => `${key} = ?`)
      .join(' AND ');
    
    const sql = `DELETE FROM ${table} WHERE ${whereClause}`;
    const params = Object.values(conditions);

    return await this.run(sql, params);
  }

  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
        } else {
          console.log('Database connection closed');
        }
      });
    }
  }
}

module.exports = new DatabaseManager();
