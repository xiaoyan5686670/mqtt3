# -*- coding: utf-8 -*-
"""
迁移脚本：为 devices 表添加 relay_in_display_name 字段
用于存储继电器输入的自定义显示名称
"""
from sqlalchemy import create_engine, text
from core.config import settings

def migrate():
    """执行迁移"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('devices') 
            WHERE name='relay_in_display_name'
        """))
        exists = result.scalar() > 0
        
        if exists:
            print("✓ 字段 relay_in_display_name 已存在，跳过迁移")
            return
        
        # 添加字段
        print("正在添加 relay_in_display_name 字段...")
        conn.execute(text("""
            ALTER TABLE devices 
            ADD COLUMN relay_in_display_name VARCHAR
        """))
        conn.commit()
        
        print("✓ 成功添加 relay_in_display_name 字段")
        print("  - 字段说明: 继电器输入的自定义显示名称")
        print("  - 默认值: NULL (前端将显示'继电器输入')")

if __name__ == "__main__":
    print("=" * 60)
    print("迁移：添加 devices.relay_in_display_name 字段")
    print("=" * 60)
    migrate()
    print("=" * 60)
    print("迁移完成！")
    print("=" * 60)
