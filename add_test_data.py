#!/usr/bin/env python3
"""
添加测试数据的脚本
"""

import sqlite3
from datetime import datetime

def add_test_sensor_data():
    # 连接到数据库
    conn = sqlite3.connect('/Users/qinxiaoyan/work/mqtt3/backend/mqtt_iot.db')
    cursor = conn.cursor()
    
    # 插入一些传感器数据
    now = datetime.now().isoformat()
    test_data = [
        (1, 'Temperature1', 25.5, '°C', now),
        (1, 'Humidity1', 60.0, '%', now),
        (1, 'Temperature2', 22.3, '°C', now),
        (1, 'Humidity2', 45.2, '%', now),
        (1, 'Relay Status', 1, '', now),
        (1, 'PB8 Level', 0, '', now)
    ]
    
    cursor.executemany(
        "INSERT INTO sensors (device_id, type, value, unit, timestamp) VALUES (?, ?, ?, ?, ?)",
        test_data
    )
    
    conn.commit()
    conn.close()
    
    print("测试数据已添加")

if __name__ == '__main__':
    add_test_sensor_data()