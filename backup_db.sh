#!/bin/bash

# SQLite Database Backup Script
BACKUP_DIR="./backups"
DB_FILE="db.sqlite3"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sqlite3"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Database file $DB_FILE not found!"
    exit 1
fi

# Create backup
echo "📦 Creating backup of $DB_FILE..."
cp "$DB_FILE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Show backup size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "📊 Backup size: $BACKUP_SIZE"
    
    # Keep only last 10 backups
    echo "🧹 Cleaning old backups (keeping last 10)..."
    ls -t "$BACKUP_DIR"/db_backup_*.sqlite3 | tail -n +11 | xargs -r rm
    
    echo "🎉 Backup completed successfully!"
else
    echo "❌ Backup failed!"
    exit 1
fi 