CREATE TABLE IF NOT EXISTS 'turbina'{
    'timestamp' TIMESTAMP primary key,
    'lv_active_power_kw' FLOAT,
    'wind_speed_m_s' FLOAT,
    'theoretical_power_kw' FLOAT,
    'wind_direction_deg' FLOAT,
};

CREATE INDEX idx_timestamp ON turbine_data (timestamp); --Para realizar consulta mas rapidas
CREATE INDEX idx_wind_speed ON turbine_data (wind_speed_ms);