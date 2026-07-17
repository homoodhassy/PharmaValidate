"""
PharmaValidate v0.5 - Related Substances Database Layer
Handles storage, retrieval, and schema management for:
- Impurity Profiles (spec limits, RRF configurations)
- Linearity & RRF Raw Data
- LOD/LOQ S/N and Regression runs
- Spiked Recovery / Accuracy records
"""

import sqlite3
import os

class RelSubDatabase:
    def __init__(self, db_path="pharmavalidate.db"):
        self.db_path = db_path
        self.initialize_tables()

    def _get_connection(self):
        """Helper to establish database connection with automated foreign key support."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_tables(self):
        """Creates the necessary SQLite schema for Related Substances validation if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Impurities Registry Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_impurities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                impurity_name TEXT NOT NULL,
                spec_limit REAL DEFAULT 0.15,
                use_rrf INTEGER DEFAULT 0, -- 0 = False, 1 = True
                rrf_value REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Linearity Raw Data Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_linearity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impurity_id INTEGER NOT NULL,
                level_num INTEGER NOT NULL,
                active_conc REAL NOT NULL,
                active_area REAL NOT NULL,
                imp_conc REAL NOT NULL,
                imp_area REAL NOT NULL,
                FOREIGN KEY (impurity_id) REFERENCES rel_sub_impurities(id) ON DELETE CASCADE
            );
        """)

        # 3. LOD & LOQ Determination Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_lod_loq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impurity_id INTEGER NOT NULL,
                run_num INTEGER NOT NULL,
                concentration REAL NOT NULL,
                signal_to_noise REAL,
                FOREIGN KEY (impurity_id) REFERENCES rel_sub_impurities(id) ON DELETE CASCADE
            );
        """)

        # 4. Accuracy / Spiked Recovery Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_accuracy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impurity_id INTEGER NOT NULL,
                level_name TEXT NOT NULL, -- e.g., 'LOQ', '100%', '150%'
                replicate_num INTEGER NOT NULL,
                spiked_amount REAL NOT NULL,
                peak_area REAL NOT NULL,
                recovery_pct REAL NOT NULL,
                FOREIGN KEY (impurity_id) REFERENCES rel_sub_impurities(id) ON DELETE CASCADE
            );
        """)

        conn.commit()
        conn.close()

    # ==========================================
    # IMPURITY REGISTRY OPERATIONS
    # ==========================================
    def add_impurity(self, project_id, name, spec_limit, use_rrf, rrf_value):
        """Adds an impurity parameter configuration linked to a specific validation project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rel_sub_impurities (project_id, impurity_name, spec_limit, use_rrf, rrf_value)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, name, spec_limit, 1 if use_rrf else 0, rrf_value))
        impurity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return impurity_id

    def get_impurities_by_project(self, project_id):
        """Fetches all registered impurities for a validation project."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, impurity_name, spec_limit, use_rrf, rrf_value 
            FROM rel_sub_impurities 
            WHERE project_id = ?
            ORDER BY id ASC
        """, (project_id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "name": r[1],
                "spec_limit": r[2],
                "use_rrf": bool(r[3]),
                "rrf_value": r[4]
            }
            for r in rows
        ]

    def update_impurity_config(self, impurity_id, spec_limit, use_rrf, rrf_value):
        """Updates limits and static RRF values for a registered impurity."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rel_sub_impurities
            SET spec_limit = ?, use_rrf = ?, rrf_value = ?
            WHERE id = ?
        """, (spec_limit, 1 if use_rrf else 0, rrf_value, impurity_id))
        conn.commit()
        conn.close()

    def delete_impurity(self, impurity_id):
        """Removes an impurity profile and cascades to clear its related raw datasets."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_impurities WHERE id = ?", (impurity_id,))
        conn.commit()
        conn.close()

    # ==========================================
    # LINEARITY DATA OPERATIONS
    # ==========================================
    def save_linearity_runs(self, impurity_id, datasets):
        """
        Saves full linearity standard matrix for active vs. impurity.
        datasets list format: [(level_num, active_conc, active_area, imp_conc, imp_area), ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        # Delete old linearity values first to avoid duplication
        cursor.execute("DELETE FROM rel_sub_linearity WHERE impurity_id = ?", (impurity_id,))
        
        for level, act_c, act_a, imp_c, imp_a in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_linearity (impurity_id, level_num, active_conc, active_area, imp_conc, imp_area)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (impurity_id, level, act_c, act_a, imp_c, imp_a))
            
        conn.commit()
        conn.close()

    def get_linearity_runs(self, impurity_id):
        """Retrieves raw linearity values for a given impurity ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT level_num, active_conc, active_area, imp_conc, imp_area
            FROM rel_sub_linearity
            WHERE impurity_id = ?
            ORDER BY level_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # ==========================================
    # LOD & LOQ DATA OPERATIONS
    # ==========================================
    def save_lod_loq_runs(self, impurity_id, datasets):
        """
        Saves LOD/LOQ Signal-to-Noise determination matrix.
        datasets list format: [(run_num, concentration, signal_to_noise), ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_lod_loq WHERE impurity_id = ?", (impurity_id,))
        
        for run, conc, sn in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_lod_loq (impurity_id, run_num, concentration, signal_to_noise)
                VALUES (?, ?, ?, ?)
            """, (impurity_id, run, conc, sn))
            
        conn.commit()
        conn.close()

    def get_lod_loq_runs(self, impurity_id):
        """Retrieves LOD/LOQ runs for a given impurity ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT run_num, concentration, signal_to_noise
            FROM rel_sub_lod_loq
            WHERE impurity_id = ?
            ORDER BY run_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # ==========================================
    # ACCURACY & RECOVERY DATA OPERATIONS
    # ==========================================
    def save_accuracy_runs(self, impurity_id, datasets):
        """
        Saves accuracy raw spiked data points.
        datasets list format: [(level_name, replicate_num, spiked_amount, peak_area, recovery_pct), ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_accuracy WHERE impurity_id = ?", (impurity_id,))
        
        for lvl, rep, spike, area, rec in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_accuracy (impurity_id, level_name, replicate_num, spiked_amount, peak_area, recovery_pct)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (impurity_id, lvl, rep, spike, area, rec))
            
        conn.commit()
        conn.close()

    def get_accuracy_runs(self, impurity_id):
        """Retrieves accuracy records for a given impurity ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT level_name, replicate_num, spiked_amount, peak_area, recovery_pct
            FROM rel_sub_accuracy
            WHERE impurity_id = ?
            ORDER BY level_name ASC, replicate_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows