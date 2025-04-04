DROP TABLE IF EXISTS turbina;

CREATE TABLE IF NOT EXISTS turbina (
    timestamp TIMESTAMP PRIMARY KEY,
    lv_active_power_kw FLOAT,
    wind_speed_ms FLOAT,
    theoretical_power_curve_kwh FLOAT,
    wind_direction_deg FLOAT
);

CREATE INDEX idx_timestamp ON turbina (timestamp);
CREATE INDEX idx_wind_speed ON turbina (wind_speed_ms);