import json
import os
from typing import List, Optional
from datetime import datetime
import uuid
from .models import Incident, ReportFilters


class JSONStorage:
    def __init__(self, file_path: str = "data/incidents.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read_data(self) -> List[dict]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_data(self, data: List[dict]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_incident(self, incident: Incident) -> Incident:
        incidents = self._read_data()
        incident.id = str(uuid.uuid4())
        incident.created_at = datetime.now().isoformat()
        incident.updated_at = datetime.now().isoformat()
        incidents.append(incident.to_dict())
        self._write_data(incidents)
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        incidents = self._read_data()
        for data in incidents:
            if data.get("id") == incident_id:
                return Incident.from_dict(data)
        return None

    def get_all_incidents(self) -> List[Incident]:
        incidents = self._read_data()
        return [Incident.from_dict(data) for data in incidents]

    def update_incident(self, incident_id: str, updates: dict) -> Optional[Incident]:
        incidents = self._read_data()
        for i, data in enumerate(incidents):
            if data.get("id") == incident_id:
                data.update(updates)
                data["updated_at"] = datetime.now().isoformat()
                incidents[i] = data
                self._write_data(incidents)
                return Incident.from_dict(data)
        return None

    def delete_incident(self, incident_id: str) -> bool:
        incidents = self._read_data()
        initial_len = len(incidents)
        incidents = [d for d in incidents if d.get("id") != incident_id]
        if len(incidents) < initial_len:
            self._write_data(incidents)
            return True
        return False

    def filter_incidents(self, filters: ReportFilters) -> List[Incident]:
        incidents = self.get_all_incidents()

        if filters.category:
            incidents = [i for i in incidents if i.category == filters.category]
        if filters.severity:
            incidents = [i for i in incidents if i.severity == filters.severity]
        if filters.status:
            incidents = [i for i in incidents if i.status == filters.status]
        if filters.date_from:
            incidents = [i for i in incidents if i.created_at >= filters.date_from]
        if filters.date_to:
            incidents = [i for i in incidents if i.created_at <= filters.date_to]

        return incidents

    def get_statistics(self) -> dict:
        incidents = self.get_all_incidents()
        return {
            "total": len(incidents),
            "by_category": self._count_by_field(incidents, "category"),
            "by_severity": self._count_by_field(incidents, "severity"),
            "by_status": self._count_by_field(incidents, "status"),
        }

    def _count_by_field(self, incidents: List[Incident], field: str) -> dict:
        counts = {}
        for incident in incidents:
            value = getattr(incident, field, None)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts
