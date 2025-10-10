"""
Export Service - Export attendance data to Excel/CSV
"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from src.database.operations import DatabaseOperations
from config.settings import Settings

logger = logging.getLogger(__name__)


class ExportService:
    """Handles data export operations"""
    
    def __init__(self):
        """Initialize export service"""
        self.db_ops = DatabaseOperations()
    
    def export_session_to_excel(
        self,
        session_id: int,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Export session attendance to Excel
        
        Args:
            session_id: Class session ID
            filename: Output filename (auto-generated if None)
        
        Returns:
            str: Path to exported file or None
        """
        try:
            # Get session data
            session = self.db_ops.get_session_by_id(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return None
            
            # Get attendance data
            attendance = self.db_ops.get_session_attendance(session_id)
            
            if not attendance:
                logger.warning(f"No attendance data for session {session_id}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(attendance)
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"attendance_session_{session_id}_{timestamp}.xlsx"
            
            # Output path
            output_path = Settings.EXPORTS_DIR / 'excel' / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Export to Excel
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Attendance exported to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return None
    
    def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str
    ) -> Optional[str]:
        """Export data to CSV"""
        try:
            df = pd.DataFrame(data)
            output_path = Settings.EXPORTS_DIR / 'csv' / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logger.info(f"Data exported to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            return None
