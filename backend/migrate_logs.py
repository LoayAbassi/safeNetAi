#!/usr/bin/env python
"""
Migration script to organize existing log files into categorized folders
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def migrate_logs():
    """Migrate existing log files to organized folder structure"""
    print("🔄 SafeNetAI Log Organization Migration")
    print("=" * 50)
    
    # Get the logs directory
    current_dir = Path(__file__).parent
    logs_dir = current_dir / 'logs'
    
    if not logs_dir.exists():
        print("❌ Logs directory not found!")
        return False
    
    # Define the migration mapping
    log_migrations = {
        'auth.log': 'auth/auth.log',
        'ai.log': 'ai/ai.log', 
        'rules.log': 'rules/rules.log',
        'transactions.log': 'transactions/transactions.log',
        'system.log': 'system/system.log',
        'errors.log': 'errors/errors.log'
    }
    
    # Create backup directory
    backup_dir = logs_dir / f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_dir.mkdir(exist_ok=True)
    
    print(f"📁 Created backup directory: {backup_dir}")
    
    success_count = 0
    total_files = 0
    
    for old_file, new_path in log_migrations.items():
        old_path = logs_dir / old_file
        new_full_path = logs_dir / new_path
        
        # Create target directory
        new_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if old_path.exists():
            total_files += 1
            try:
                # Backup original file
                backup_file = backup_dir / old_file
                shutil.copy2(old_path, backup_file)
                print(f"💾 Backed up: {old_file}")
                
                # Move to new location
                if new_full_path.exists():
                    # If new file exists, append old content
                    with open(old_path, 'r', encoding='utf-8', errors='ignore') as old_f:
                        old_content = old_f.read()
                    
                    with open(new_full_path, 'a', encoding='utf-8') as new_f:
                        new_f.write(f"\n# Migrated from {old_file} on {datetime.now()}\n")
                        new_f.write(old_content)
                    
                    print(f"📝 Appended: {old_file} → {new_path}")
                else:
                    # Move file to new location
                    shutil.move(str(old_path), str(new_full_path))
                    print(f"📁 Moved: {old_file} → {new_path}")
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed to migrate {old_file}: {e}")
        else:
            print(f"⚠️  File not found: {old_file}")
    
    # Also migrate dated log files (with extensions like .2025-09-01)
    dated_files = list(logs_dir.glob('*.log.*'))
    for dated_file in dated_files:
        base_name = dated_file.name.split('.')[0] + '.log'
        if base_name in log_migrations:
            target_dir = logs_dir / log_migrations[base_name].split('/')[0]
            target_file = target_dir / dated_file.name
            
            try:
                if not target_file.exists():
                    shutil.copy2(dated_file, target_file)
                    print(f"📅 Migrated dated log: {dated_file.name} → {target_dir.name}/")
                    dated_file.unlink()  # Remove original
            except Exception as e:
                print(f"❌ Failed to migrate dated file {dated_file.name}: {e}")
    
    print("\n" + "=" * 50)
    print("MIGRATION SUMMARY")
    print("=" * 50)
    
    if success_count == total_files:
        print(f"✅ Successfully migrated {success_count}/{total_files} log files")
        print("\n📁 New log structure:")
        
        for category in ['auth', 'ai', 'rules', 'transactions', 'system', 'errors', 'email']:
            category_dir = logs_dir / category
            if category_dir.exists():
                files = list(category_dir.glob('*.log*'))
                print(f"   logs/{category}/ ({len(files)} files)")
        
        print(f"\n💾 Backup created in: {backup_dir}")
        print("\n🚀 Ready to start with organized logging!")
        
    else:
        print(f"⚠️  Partial migration: {success_count}/{total_files} files migrated")
        print("Some files may need manual intervention.")
    
    return success_count == total_files

if __name__ == "__main__":
    migrate_logs()