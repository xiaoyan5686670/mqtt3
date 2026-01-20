"""清理重复的传感器配置记录"""
import sys
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.sensor_config import SensorConfigModel


def find_duplicate_configs(db: Session):
    """查找重复的传感器配置"""
    # 查询有重复的 (device_id, type) 组合
    duplicates = db.query(
        SensorConfigModel.device_id,
        SensorConfigModel.type,
        func.count(SensorConfigModel.id).label('count')
    ).group_by(
        SensorConfigModel.device_id,
        SensorConfigModel.type
    ).having(
        func.count(SensorConfigModel.id) > 1
    ).all()
    
    return duplicates


def cleanup_duplicates(db: Session, dry_run=True):
    """清理重复的传感器配置，只保留最新的一条"""
    duplicates = find_duplicate_configs(db)
    
    if not duplicates:
        print("✓ 没有发现重复的传感器配置记录")
        return 0
    
    print(f"发现 {len(duplicates)} 组重复的传感器配置：")
    print("-" * 80)
    
    total_deleted = 0
    
    for device_id, sensor_type, count in duplicates:
        print(f"\n设备ID: {device_id}, 传感器类型: {sensor_type}, 重复数量: {count}")
        
        # 获取该设备该类型的所有配置，按更新时间排序
        configs = db.query(SensorConfigModel).filter(
            SensorConfigModel.device_id == device_id,
            SensorConfigModel.type == sensor_type
        ).order_by(SensorConfigModel.updated_at.desc()).all()
        
        # 保留第一条（最新的），删除其他的
        keep_config = configs[0]
        delete_configs = configs[1:]
        
        print(f"  保留配置: ID={keep_config.id}, display_name={keep_config.display_name}, updated_at={keep_config.updated_at}")
        
        for config in delete_configs:
            # 检查这个配置是否有关联的数据
            data_count = len(config.sensor_data)
            print(f"  {'[DRY RUN] ' if dry_run else ''}删除配置: ID={config.id}, display_name={config.display_name}, 关联数据数量={data_count}")
            
            if not dry_run:
                # 如果有关联数据，将数据迁移到保留的配置
                if data_count > 0:
                    print(f"    迁移 {data_count} 条数据到配置 ID={keep_config.id}")
                    for data in config.sensor_data:
                        data.sensor_config_id = keep_config.id
                
                # 删除重复的配置
                db.delete(config)
                total_deleted += 1
    
    if not dry_run:
        db.commit()
        print(f"\n✓ 清理完成，共删除 {total_deleted} 条重复配置")
    else:
        print(f"\n[DRY RUN] 预计删除 {len(duplicates)} 组重复配置")
        print("\n运行 'python cleanup_duplicate_sensor_configs.py --execute' 来执行实际清理")
    
    return total_deleted


def main():
    """主函数"""
    dry_run = True
    
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        dry_run = False
        print("⚠️  警告：这将真实删除数据库中的重复记录！")
        confirm = input("确认执行吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消操作")
            return
    
    db = SessionLocal()
    try:
        if dry_run:
            print("=" * 80)
            print("检查重复的传感器配置（预览模式）")
            print("=" * 80)
        else:
            print("=" * 80)
            print("清理重复的传感器配置（执行模式）")
            print("=" * 80)
        
        cleanup_duplicates(db, dry_run=dry_run)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
