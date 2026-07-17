"""
PharmaValidate v0.5 - Complete Database Module
"""

import sqlite3
import time
from pathlib import Path

DB_FILE = Path("data/pharmavalidate.db")


def get_connection(max_retries=5, delay=0.5):
    """Get database connection with retry logic to prevent locking."""
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(str(DB_FILE), timeout=20)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA busy_timeout = 30000;")  # 30 seconds
            return conn
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            raise
    return None


def execute_with_retry(func, *args, max_retries=3, **kwargs):
    """Execute a database function with retry on lock."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < max_retries - 1:
                time.sleep(1 * (attempt + 1))
                continue
            raise
    return None


def initialize_database():
    """Creates all tables for PharmaValidate."""
    print("🔵 Initializing database...")
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                product TEXT,
                method TEXT,
                validation_type TEXT,
                protocol_number TEXT,
                analyst TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Protocols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                protocol_number TEXT NOT NULL,
                protocol_data TEXT,
                pdf_path TEXT,
                generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Specificity results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS specificity_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                sample_type TEXT NOT NULL,
                peak_detected TEXT,
                retention_time REAL,
                peak_area REAL,
                resolution REAL,
                interference REAL,
                status TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Linearity results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS linearity_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                level_number INTEGER NOT NULL,
                nominal_percent REAL,
                weight_1 REAL,
                weight_2 REAL,
                weight_3 REAL,
                response_1 REAL,
                response_2 REAL,
                response_3 REAL,
                mean_response REAL,
                rsd_percent REAL,
                slope REAL,
                intercept REAL,
                r_squared REAL,
                multiple_r REAL,
                rss REAL,
                y_intercept_percent REAL,
                pooled_rsd REAL,
                status_r_squared TEXT,
                status_y_intercept TEXT,
                overall_status TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Accuracy results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accuracy_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                sst_injection_1 REAL,
                sst_injection_2 REAL,
                sst_injection_3 REAL,
                sst_injection_4 REAL,
                sst_injection_5 REAL,
                sst_mean REAL,
                sst_rsd REAL,
                matrix_response REAL,
                std_weight REAL,
                dilution_ratio REAL,
                level_80_spike_1 REAL,
                level_80_spike_2 REAL,
                level_80_spike_3 REAL,
                level_80_found_1 REAL,
                level_80_found_2 REAL,
                level_80_found_3 REAL,
                level_80_recovery_1 REAL,
                level_80_recovery_2 REAL,
                level_80_recovery_3 REAL,
                level_80_mean REAL,
                level_80_rsd REAL,
                level_80_bias REAL,
                level_80_status TEXT,
                level_100_spike_1 REAL,
                level_100_spike_2 REAL,
                level_100_spike_3 REAL,
                level_100_found_1 REAL,
                level_100_found_2 REAL,
                level_100_found_3 REAL,
                level_100_recovery_1 REAL,
                level_100_recovery_2 REAL,
                level_100_recovery_3 REAL,
                level_100_mean REAL,
                level_100_rsd REAL,
                level_100_bias REAL,
                level_100_status TEXT,
                level_120_spike_1 REAL,
                level_120_spike_2 REAL,
                level_120_spike_3 REAL,
                level_120_found_1 REAL,
                level_120_found_2 REAL,
                level_120_found_3 REAL,
                level_120_recovery_1 REAL,
                level_120_recovery_2 REAL,
                level_120_recovery_3 REAL,
                level_120_mean REAL,
                level_120_rsd REAL,
                level_120_bias REAL,
                level_120_status TEXT,
                overall_mean_recovery REAL,
                overall_rsd REAL,
                overall_bias REAL,
                pooled_sd REAL,
                overall_status TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Precision results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS precision_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                rep_1 REAL,
                rep_2 REAL,
                rep_3 REAL,
                rep_4 REAL,
                rep_5 REAL,
                rep_6 REAL,
                rep_mean REAL,
                rep_sd REAL,
                rep_rsd REAL,
                rep_status TEXT,
                ip_1 REAL,
                ip_2 REAL,
                ip_3 REAL,
                ip_4 REAL,
                ip_5 REAL,
                ip_6 REAL,
                ip_mean REAL,
                ip_sd REAL,
                ip_rsd REAL,
                ip_status TEXT,
                combined_mean REAL,
                combined_sd REAL,
                combined_rsd REAL,
                overall_status TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Robustness OFAT results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robustness_ofat_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                parameter_name TEXT NOT NULL,
                retention_time REAL,
                tailing_factor REAL,
                theoretical_plates REAL,
                assay_result REAL,
                deviation_percent REAL,
                is_nominal INTEGER DEFAULT 0,
                status TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Robustness DOE results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robustness_doe_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                factor_a_name TEXT,
                factor_b_name TEXT,
                factor_c_name TEXT,
                factor_a_low REAL,
                factor_a_high REAL,
                factor_b_low REAL,
                factor_b_high REAL,
                factor_c_low REAL,
                factor_c_high REAL,
                run_1_response REAL,
                run_2_response REAL,
                run_3_response REAL,
                run_4_response REAL,
                run_5_response REAL,
                run_6_response REAL,
                run_7_response REAL,
                run_8_response REAL,
                effect_a REAL,
                effect_b REAL,
                effect_c REAL,
                dominant_factor TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # Related Substances tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_impurities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                impurity_name TEXT NOT NULL,
                spec_limit REAL DEFAULT 0.15,
                use_rrf INTEGER DEFAULT 0,
                rrf_value REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

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
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_lod_loq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impurity_id INTEGER NOT NULL,
                run_num INTEGER NOT NULL,
                concentration REAL NOT NULL,
                signal_to_noise REAL,
                FOREIGN KEY (impurity_id) REFERENCES rel_sub_impurities(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rel_sub_accuracy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                impurity_id INTEGER NOT NULL,
                level_name TEXT NOT NULL,
                replicate_num INTEGER NOT NULL,
                spiked_amount REAL NOT NULL,
                peak_area REAL NOT NULL,
                recovery_pct REAL NOT NULL,
                FOREIGN KEY (impurity_id) REFERENCES rel_sub_impurities(id) ON DELETE CASCADE
            )
        """)

        # Validation summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER UNIQUE NOT NULL,
                specificity_status TEXT,
                linearity_status TEXT,
                accuracy_status TEXT,
                precision_status TEXT,
                robustness_status TEXT,
                rel_sub_status TEXT,
                overall_status TEXT,
                report_generated_date TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# ============================================
# PROJECT FUNCTIONS
# ============================================

def create_project(project_name, product, method, validation_type, protocol_number, analyst):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (project_name, product, method, validation_type, protocol_number, analyst)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (project_name, product, method, validation_type, protocol_number, analyst))
        project_id = cursor.lastrowid
        conn.commit()
        return project_id
    finally:
        if conn:
            conn.close()


def get_projects():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


def get_project(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()
        return project
    finally:
        if conn:
            conn.close()


def delete_project(project_id):
    """Permanently deletes a validation project."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        print(f"✅ Project {project_id} deleted")
    finally:
        if conn:
            conn.close()


# ============================================
# PROTOCOL FUNCTIONS
# ============================================

def save_protocol(project_id, protocol_number, protocol_data, pdf_path=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO protocols (project_id, protocol_number, protocol_data, pdf_path)
            VALUES (?, ?, ?, ?)
        """, (project_id, protocol_number, protocol_data, pdf_path))
        protocol_id = cursor.lastrowid
        conn.commit()
        return protocol_id
    finally:
        if conn:
            conn.close()


def get_protocol_by_project(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM protocols 
            WHERE project_id = ? 
            ORDER BY generated_date DESC 
            LIMIT 1
        """, (project_id,))
        protocol = cursor.fetchone()
        return protocol
    finally:
        if conn:
            conn.close()


# ============================================
# SPECIFICITY FUNCTIONS
# ============================================

def save_specificity(project_id, rows_data):
    """Saves specificity validation results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM specificity_results WHERE project_id = ?", (project_id,))
        
        for row in rows_data:
            cursor.execute("""
                INSERT INTO specificity_results (
                    project_id, sample_type, peak_detected, retention_time, 
                    peak_area, resolution, interference, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                row.get("name", ""),
                row.get("peak_detected", ""),
                row.get("rt", 0.0),
                row.get("area", 0.0),
                row.get("rs", 0.0),
                row.get("interference", 0.0),
                row.get("status", "PENDING")
            ))
        
        conn.commit()
        
        # Update summary in a separate connection to avoid lock issues
        status = _get_overall_status_from_rows(rows_data)
        _update_summary_status(project_id, "specificity_status", status)
        
        print(f"✅ Specificity data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving specificity: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_specificity_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sample_type, peak_detected, retention_time, peak_area, 
                   resolution, interference, status
            FROM specificity_results 
            WHERE project_id = ?
            ORDER BY id ASC
        """, (project_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


# ============================================
# LINEARITY FUNCTIONS
# ============================================

def save_linearity(project_id, data):
    """Saves linearity validation results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM linearity_results WHERE project_id = ?", (project_id,))
        
        cursor.execute("""
            INSERT INTO linearity_results (
                project_id, level_number, nominal_percent,
                weight_1, weight_2, weight_3,
                response_1, response_2, response_3,
                mean_response, rsd_percent,
                slope, intercept, r_squared, multiple_r, rss,
                y_intercept_percent, pooled_rsd,
                status_r_squared, status_y_intercept, overall_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            data.get("level_number"),
            data.get("nominal_percent"),
            data.get("weight_1", 0.0),
            data.get("weight_2", 0.0),
            data.get("weight_3", 0.0),
            data.get("response_1", 0.0),
            data.get("response_2", 0.0),
            data.get("response_3", 0.0),
            data.get("mean_response", 0.0),
            data.get("rsd_percent", 0.0),
            data.get("slope", 0.0),
            data.get("intercept", 0.0),
            data.get("r_squared", 0.0),
            data.get("multiple_r", 0.0),
            data.get("rss", 0.0),
            data.get("y_intercept_percent", 0.0),
            data.get("pooled_rsd", 0.0),
            data.get("status_r_squared", "PENDING"),
            data.get("status_y_intercept", "PENDING"),
            data.get("overall_status", "PENDING")
        ))
        
        conn.commit()
        print(f"✅ Linearity data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving linearity: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_linearity_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM linearity_results WHERE project_id = ?
            ORDER BY level_number ASC
        """, (project_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


# ============================================
# ACCURACY FUNCTIONS
# ============================================

def save_accuracy(project_id, data):
    """Saves accuracy validation results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM accuracy_results WHERE project_id = ?", (project_id,))
        
        # FIXED: Added the missing 4 placeholders to make it exactly 55 '?' marks
        cursor.execute("""
            INSERT INTO accuracy_results (
                project_id,
                sst_injection_1, sst_injection_2, sst_injection_3, sst_injection_4, sst_injection_5,
                sst_mean, sst_rsd,
                matrix_response, std_weight, dilution_ratio,
                level_80_spike_1, level_80_spike_2, level_80_spike_3,
                level_80_found_1, level_80_found_2, level_80_found_3,
                level_80_recovery_1, level_80_recovery_2, level_80_recovery_3,
                level_80_mean, level_80_rsd, level_80_bias, level_80_status,
                level_100_spike_1, level_100_spike_2, level_100_spike_3,
                level_100_found_1, level_100_found_2, level_100_found_3,
                level_100_recovery_1, level_100_recovery_2, level_100_recovery_3,
                level_100_mean, level_100_rsd, level_100_bias, level_100_status,
                level_120_spike_1, level_120_spike_2, level_120_spike_3,
                level_120_found_1, level_120_found_2, level_120_found_3,
                level_120_recovery_1, level_120_recovery_2, level_120_recovery_3,
                level_120_mean, level_120_rsd, level_120_bias, level_120_status,
                overall_mean_recovery, overall_rsd, overall_bias, pooled_sd, overall_status
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?
            )
        """, (
            project_id,
            data.get("sst_1", 0.0), data.get("sst_2", 0.0), data.get("sst_3", 0.0),
            data.get("sst_4", 0.0), data.get("sst_5", 0.0),
            data.get("sst_mean", 0.0), data.get("sst_rsd", 0.0),
            data.get("matrix_response", 0.0), data.get("std_weight", 0.0), data.get("dilution_ratio", 0.0),
            data.get("l80_spike_1", 0.0), data.get("l80_spike_2", 0.0), data.get("l80_spike_3", 0.0),
            data.get("l80_found_1", 0.0), data.get("l80_found_2", 0.0), data.get("l80_found_3", 0.0),
            data.get("l80_rec_1", 0.0), data.get("l80_rec_2", 0.0), data.get("l80_rec_3", 0.0),
            data.get("l80_mean", 0.0), data.get("l80_rsd", 0.0), data.get("l80_bias", 0.0), data.get("l80_status", "PENDING"),
            data.get("l100_spike_1", 0.0), data.get("l100_spike_2", 0.0), data.get("l100_spike_3", 0.0),
            data.get("l100_found_1", 0.0), data.get("l100_found_2", 0.0), data.get("l100_found_3", 0.0),
            data.get("l100_rec_1", 0.0), data.get("l100_rec_2", 0.0), data.get("l100_rec_3", 0.0),
            data.get("l100_mean", 0.0), data.get("l100_rsd", 0.0), data.get("l100_bias", 0.0), data.get("l100_status", "PENDING"),
            data.get("l120_spike_1", 0.0), data.get("l120_spike_2", 0.0), data.get("l120_spike_3", 0.0),
            data.get("l120_found_1", 0.0), data.get("l120_found_2", 0.0), data.get("l120_found_3", 0.0),
            data.get("l120_rec_1", 0.0), data.get("l120_rec_2", 0.0), data.get("l120_rec_3", 0.0),
            data.get("l120_mean", 0.0), data.get("l120_rsd", 0.0), data.get("l120_bias", 0.0), data.get("l120_status", "PENDING"),
            data.get("overall_mean", 0.0), data.get("overall_rsd", 0.0),
            data.get("overall_bias", 0.0), data.get("pooled_sd", 0.0),
            data.get("overall_status", "PENDING")
        ))
        
        conn.commit()
        print(f"✅ Accuracy data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving accuracy: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_accuracy_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accuracy_results WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        return row
    finally:
        if conn:
            conn.close()


# ============================================
# PRECISION FUNCTIONS
# ============================================

def save_precision(project_id, data):
    """Saves precision validation results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM precision_results WHERE project_id = ?", (project_id,))
        
        cursor.execute("""
            INSERT INTO precision_results (
                project_id,
                rep_1, rep_2, rep_3, rep_4, rep_5, rep_6,
                rep_mean, rep_sd, rep_rsd, rep_status,
                ip_1, ip_2, ip_3, ip_4, ip_5, ip_6,
                ip_mean, ip_sd, ip_rsd, ip_status,
                combined_mean, combined_sd, combined_rsd, overall_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            data.get("rep_1", 0.0), data.get("rep_2", 0.0), data.get("rep_3", 0.0),
            data.get("rep_4", 0.0), data.get("rep_5", 0.0), data.get("rep_6", 0.0),
            data.get("rep_mean", 0.0), data.get("rep_sd", 0.0), data.get("rep_rsd", 0.0),
            data.get("rep_status", "PENDING"),
            data.get("ip_1", 0.0), data.get("ip_2", 0.0), data.get("ip_3", 0.0),
            data.get("ip_4", 0.0), data.get("ip_5", 0.0), data.get("ip_6", 0.0),
            data.get("ip_mean", 0.0), data.get("ip_sd", 0.0), data.get("ip_rsd", 0.0),
            data.get("ip_status", "PENDING"),
            data.get("combined_mean", 0.0), data.get("combined_sd", 0.0),
            data.get("combined_rsd", 0.0), data.get("overall_status", "PENDING")
        ))
        
        conn.commit()
        print(f"✅ Precision data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving precision: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_precision_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM precision_results WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        return row
    finally:
        if conn:
            conn.close()


# ============================================
# ROBUSTNESS FUNCTIONS
# ============================================

def save_robustness_ofat(project_id, rows_data):
    """Saves OFAT robustness results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM robustness_ofat_results WHERE project_id = ?", (project_id,))
        
        for row in rows_data:
            cursor.execute("""
                INSERT INTO robustness_ofat_results (
                    project_id, parameter_name, retention_time, tailing_factor,
                    theoretical_plates, assay_result, deviation_percent, is_nominal, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                row.get("name", ""),
                row.get("rt", 0.0),
                row.get("tailing", 0.0),
                row.get("plates", 0.0),
                row.get("assay", 0.0),
                row.get("deviation", 0.0),
                1 if row.get("is_nominal", False) else 0,
                row.get("status", "PENDING")
            ))
        
        conn.commit()
        print(f"✅ OFAT robustness data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving OFAT robustness: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_robustness_ofat_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM robustness_ofat_results 
            WHERE project_id = ?
            ORDER BY id ASC
        """, (project_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


def save_robustness_doe(project_id, data):
    """Saves DOE robustness results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM robustness_doe_results WHERE project_id = ?", (project_id,))
        
        cursor.execute("""
            INSERT INTO robustness_doe_results (
                project_id,
                factor_a_name, factor_b_name, factor_c_name,
                factor_a_low, factor_a_high,
                factor_b_low, factor_b_high,
                factor_c_low, factor_c_high,
                run_1_response, run_2_response, run_3_response, run_4_response,
                run_5_response, run_6_response, run_7_response, run_8_response,
                effect_a, effect_b, effect_c, dominant_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            data.get("factor_a_name", ""),
            data.get("factor_b_name", ""),
            data.get("factor_c_name", ""),
            data.get("factor_a_low", 0.0),
            data.get("factor_a_high", 0.0),
            data.get("factor_b_low", 0.0),
            data.get("factor_b_high", 0.0),
            data.get("factor_c_low", 0.0),
            data.get("factor_c_high", 0.0),
            data.get("run_1", 0.0), data.get("run_2", 0.0),
            data.get("run_3", 0.0), data.get("run_4", 0.0),
            data.get("run_5", 0.0), data.get("run_6", 0.0),
            data.get("run_7", 0.0), data.get("run_8", 0.0),
            data.get("effect_a", 0.0),
            data.get("effect_b", 0.0),
            data.get("effect_c", 0.0),
            data.get("dominant_factor", "")
        ))
        
        conn.commit()
        print(f"✅ DOE robustness data saved for project {project_id}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error saving DOE robustness: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_robustness_doe_results(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM robustness_doe_results WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        return row
    finally:
        if conn:
            conn.close()


# ============================================
# RELATED SUBSTANCES FUNCTIONS
# ============================================

def save_rel_sub_impurity(project_id, name, spec_limit=0.15, use_rrf=False, rrf_value=1.0):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rel_sub_impurities (project_id, impurity_name, spec_limit, use_rrf, rrf_value)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, name, spec_limit, 1 if use_rrf else 0, rrf_value))
        impurity_id = cursor.lastrowid
        conn.commit()
        return impurity_id
    finally:
        if conn:
            conn.close()


def get_rel_sub_impurities(project_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, impurity_name, spec_limit, use_rrf, rrf_value
            FROM rel_sub_impurities
            WHERE project_id = ?
            ORDER BY id ASC
        """, (project_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


def save_rel_sub_linearity(impurity_id, datasets):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_linearity WHERE impurity_id = ?", (impurity_id,))
        for level, act_c, act_a, imp_c, imp_a in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_linearity (impurity_id, level_num, active_conc, active_area, imp_conc, imp_area)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (impurity_id, level, act_c, act_a, imp_c, imp_a))
        conn.commit()
    finally:
        if conn:
            conn.close()


def get_rel_sub_linearity(impurity_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT level_num, active_conc, active_area, imp_conc, imp_area
            FROM rel_sub_linearity
            WHERE impurity_id = ?
            ORDER BY level_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


def save_rel_sub_lod_loq(impurity_id, datasets):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_lod_loq WHERE impurity_id = ?", (impurity_id,))
        for run, conc, sn in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_lod_loq (impurity_id, run_num, concentration, signal_to_noise)
                VALUES (?, ?, ?, ?)
            """, (impurity_id, run, conc, sn))
        conn.commit()
    finally:
        if conn:
            conn.close()


def get_rel_sub_lod_loq(impurity_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT run_num, concentration, signal_to_noise
            FROM rel_sub_lod_loq
            WHERE impurity_id = ?
            ORDER BY run_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


def save_rel_sub_accuracy(impurity_id, datasets):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rel_sub_accuracy WHERE impurity_id = ?", (impurity_id,))
        for lvl, rep, spike, area, rec in datasets:
            cursor.execute("""
                INSERT INTO rel_sub_accuracy (impurity_id, level_name, replicate_num, spiked_amount, peak_area, recovery_pct)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (impurity_id, lvl, rep, spike, area, rec))
        conn.commit()
    finally:
        if conn:
            conn.close()


def get_rel_sub_accuracy(impurity_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT level_name, replicate_num, spiked_amount, peak_area, recovery_pct
            FROM rel_sub_accuracy
            WHERE impurity_id = ?
            ORDER BY level_name ASC, replicate_num ASC
        """, (impurity_id,))
        rows = cursor.fetchall()
        return rows
    finally:
        if conn:
            conn.close()


# ============================================
# VALIDATION SUMMARY FUNCTIONS
# ============================================

def _get_overall_status_from_rows(rows):
    """Helper to determine overall status from rows data."""
    if not rows:
        return "PENDING"
    for row in rows:
        if row.get("status", "").upper() == "FAIL":
            return "FAIL"
    return "PASS"


def _update_summary_status(project_id, column, status):
    """Updates a specific column in the validation summary."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM validation_summary WHERE project_id = ?", (project_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(f"""
                UPDATE validation_summary 
                SET {column} = ?
                WHERE project_id = ?
            """, (status, project_id))
        else:
            cursor.execute(f"""
                INSERT INTO validation_summary (project_id, {column})
                VALUES (?, ?)
            """, (project_id, status))
        
        conn.commit()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Error updating summary: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_validation_summary(project_id):
    """Gets the complete validation summary for a project."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM validation_summary WHERE project_id = ?
        """, (project_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                "specificity_status": row[1],
                "linearity_status": row[2],
                "accuracy_status": row[3],
                "precision_status": row[4],
                "robustness_status": row[5],
                "rel_sub_status": row[6],
                "overall_status": row[7],
                "report_generated_date": row[8]
            }
        return None
    finally:
        if conn:
            conn.close()


def update_overall_status(project_id):
    """Calculates and updates the overall status based on all modules."""
    summary = get_validation_summary(project_id)
    if not summary:
        return
    
    statuses = [
        summary.get("specificity_status", ""),
        summary.get("linearity_status", ""),
        summary.get("accuracy_status", ""),
        summary.get("precision_status", ""),
        summary.get("robustness_status", ""),
        summary.get("rel_sub_status", "")
    ]
    
    if any(s == "FAIL" for s in statuses):
        overall = "FAIL"
    elif all(s == "PASS" for s in statuses if s):
        overall = "PASS"
    else:
        overall = "INCOMPLETE"
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE validation_summary 
            SET overall_status = ? 
            WHERE project_id = ?
        """, (overall, project_id))
        conn.commit()
    finally:
        if conn:
            conn.close()