"""
PharmaValidate v0.5 - Related Substances Math Engine
Calculates:
- Linear Regression (Slope, Intercept, r, r^2, Standard Error, Intercept Standard Deviation)
- Relative Response Factor (RRF)
- Limit of Detection (LOD) & Limit of Quantitation (LOQ) using multiple ICH methods
- Impurity Recovery % (via direct standard or RRF correction)
- System Suitability (Mean, SD, %RSD)
"""

import math
import numpy as np

class RelSubCalculator:
    
    @staticmethod
    def calculate_regression(x_vals, y_vals):
        """
        Performs linear regression (y = mx + c) and calculates statistical validation parameters.
        Returns detailed stats including standard deviation of intercept for LOD/LOQ calculation.
        """
        if len(x_vals) < 2 or len(x_vals) != len(y_vals):
            return {
                "slope": 0.0,
                "intercept": 0.0,
                "r_value": 0.0,
                "r_squared": 0.0,
                "residual_std_dev": 0.0,
                "intercept_std_dev": 0.0
            }
            
        x = np.array(x_vals, dtype=float)
        y = np.array(y_vals, dtype=float)
        n = len(x)
        
        # Linear Fit (y = mx + c)
        m, c = np.polyfit(x, y, 1)
        
        # Correlation Coefficient (r) and Coefficient of Determination (r^2)
        r_matrix = np.corrcoef(x, y)
        r = r_matrix[0, 1] if r_matrix.shape == (2, 2) else 0.0
        r2 = r ** 2
        
        # Calculate Residuals & Residual Standard Deviation (s_y/x)
        y_pred = m * x + c
        residuals = y - y_pred
        sum_sq_residuals = np.sum(residuals ** 2)
        
        if n > 2:
            residual_std_dev = np.sqrt(sum_sq_residuals / (n - 2))
        else:
            residual_std_dev = 0.0
            
        # Calculate Standard Deviation of the Intercept (s_c)
        mean_x = np.mean(x)
        sum_sq_diff_x = np.sum((x - mean_x) ** 2)
        
        if sum_sq_diff_x != 0 and n > 2:
            intercept_std_dev = residual_std_dev * np.sqrt((1.0 / n) + (mean_x**2 / sum_sq_diff_x))
        else:
            intercept_std_dev = 0.0
            
        return {
            "slope": float(m),
            "intercept": float(c),
            "r_value": float(r),
            "r_squared": float(r2),
            "residual_std_dev": float(residual_std_dev),
            "intercept_std_dev": float(intercept_std_dev)
        }

    @staticmethod
    def calculate_rrf(slope_impurity, slope_active):
        """
        Calculates the Relative Response Factor (RRF) of an impurity.
        RRF = Slope of Impurity / Slope of Active Drug Substance
        """
        if slope_active == 0:
            return 0.0
        return float(slope_impurity / slope_active)

    @staticmethod
    def calculate_lod_loq_from_curve(slope, intercept_std_dev):
        """
        Calculates LOD and LOQ using standard deviation of y-intercept (ICH Option 1).
        LOD = 3.3 * (SD of Intercept / Slope)
        LOQ = 10.0 * (SD of Intercept / Slope)
        """
        if slope == 0:
            return {"lod": 0.0, "loq": 0.0}
        lod = (3.3 * intercept_std_dev) / slope
        loq = (10.0 * intercept_std_dev) / slope
        return {
            "lod": float(lod),
            "loq": float(loq)
        }

    @staticmethod
    def calculate_lod_loq_from_residuals(slope, residual_std_dev):
        """
        Calculates LOD and LOQ using Residual Standard Deviation (ICH Option 2).
        LOD = 3.3 * (Residual SD / Slope)
        LOQ = 10.0 * (Residual SD / Slope)
        """
        if slope == 0:
            return {"lod": 0.0, "loq": 0.0}
        lod = (3.3 * residual_std_dev) / slope
        loq = (10.0 * residual_std_dev) / slope
        return {
            "lod": float(lod),
            "loq": float(loq)
        }

    @staticmethod
    def calculate_lod_loq_by_sn(concentrations, sn_ratios):
        """
        Calculates approximate LOD and LOQ using Signal-to-Noise (S/N) verification data.
        Determines the concentration closest to:
        - S/N ~ 3 for LOD
        - S/N ~ 10 for LOQ
        """
        if not concentrations or len(concentrations) != len(sn_ratios):
            return {"lod": None, "loq": None}
            
        # Sort values by S/N ratio ascending
        sorted_pairs = sorted(zip(sn_ratios, concentrations))
        
        lod_conc = None
        loq_conc = None
        
        # Simple threshold search
        for sn, conc in sorted_pairs:
            if sn >= 3.0 and lod_conc is None:
                lod_conc = conc
            if sn >= 10.0 and loq_conc is None:
                loq_conc = conc
                break
                
        return {
            "lod": float(lod_conc) if lod_conc is not None else None,
            "loq": float(loq_conc) if loq_conc is not None else None
        }

    @staticmethod
    def calculate_impurity_recovery(area, spiked_amount, cal_slope, cal_intercept, rrf=1.0, use_rrf=False):
        """
        Calculates spiked recovery % for an impurity run.
        Supports:
        - Direct calculations via Impurity Linearity Curve (use_rrf=False)
        - Indirect calculations via Active Curve corrected by RRF (use_rrf=True)
        """
        if cal_slope == 0 or spiked_amount == 0:
            return {"recovered_conc": 0.0, "recovery_pct": 0.0}
            
        # Step 1: Calculate recovered concentration from response (area)
        if use_rrf:
            # Active Curve with RRF applied: Conc = (Area - ActiveIntercept) / (ActiveSlope * RRF)
            recovered_conc = (area - cal_intercept) / (cal_slope * rrf)
        else:
            # Direct Impurity Curve: Conc = (Area - ImpurityIntercept) / ImpuritySlope
            recovered_conc = (area - cal_intercept) / cal_slope
            
        # Step 2: Recovery Percentage
        recovery_pct = (recovered_conc / spiked_amount) * 100.0
        
        return {
            "recovered_conc": float(recovered_conc),
            "recovery_pct": float(recovery_pct)
        }

    @staticmethod
    def calculate_statistics(data_list):
        """
        Calculates Standard Deviation and %RSD for system suitability verification.
        """
        if not data_list or len(data_list) == 0:
            return {"mean": 0.0, "sd": 0.0, "rsd": 0.0}
            
        data = np.array(data_list, dtype=float)
        mean = np.mean(data)
        
        if len(data) > 1:
            sd = np.std(data, ddof=1)  # Sample Standard Deviation (ddof=1)
        else:
            sd = 0.0
            
        rsd = (sd / mean * 100.0) if mean != 0 else 0.0
        
        return {
            "mean": float(mean),
            "sd": float(sd),
            "rsd": float(rsd)
        }