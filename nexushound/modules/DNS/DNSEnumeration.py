from nexushound.modules_manager import ModuleBase, ModuleOption, WordlistOption
import asyncio
import aiodns
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Optional, Any
import customtkinter as ctk


class DNSEnumerator(ModuleBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "DNSEnumerator"
        self.version = "1.0.0"
        self.description = "DNS record enumeration tool"
        self.category = "DNS"
        self.is_public = True
        self.authors = ["NexusHound"]
        self.license = "MIT"
        self.dependencies = ["aiodns"]
        self.min_python_version = "3.10"
        self.tags = ["dns", "enumeration", "records"]

        self.options = [
            ModuleOption(
                name="domain",
                description="Target domain",
                type="str",
                default="",
                required=True
            ),
            ModuleOption(
                name="record_types",
                description="DNS record types to query (comma-separated)",
                type="str",
                default="A,AAAA,MX,NS,TXT,CNAME,SOA",
                required=False
            )
        ]

        self._results = []

    def create_ui(self, parent: ctk.CTkBaseClass) -> None:
        self._ui_elements["results"] = ctk.CTkTextbox(parent, height=400)
        self._ui_elements["results"].pack(fill="both", expand=True, padx=5, pady=5)

    async def enumerate_dns(self, domain: str, record_types: List[str]) -> List[Dict]:
        results = []
        resolver = aiodns.DNSResolver()

        for record_type in record_types:
            try:
                self._ui_elements["results"].insert("end", f"\nQuerying {record_type} records...\n")
                result = await resolver.query(domain, record_type)

                if isinstance(result, list):
                    records = result
                else:
                    records = [result]

                for record in records:
                    record_data = {
                        "type": record_type,
                        "domain": domain
                    }

                    if record_type in ["A", "AAAA"]:
                        record_data["ip"] = record.host
                    elif record_type == "MX":
                        record_data["host"] = record.host
                        record_data["priority"] = record.priority
                    elif record_type == "NS":
                        record_data["nameserver"] = record.host
                    elif record_type == "TXT":
                        record_data["text"] = record.text
                    elif record_type == "CNAME":
                        record_data["target"] = record.cname
                    elif record_type == "SOA":
                        record_data.update({
                            "mname": record.mname,
                            "rname": record.rname,
                            "serial": record.serial,
                            "refresh": record.refresh,
                            "retry": record.retry,
                            "expire": record.expire,
                            "minimum": record.minimum
                        })

                    results.append(record_data)
                    self._ui_elements["results"].insert("end", f"Found: {record_data}\n")

            except Exception as e:
                self._ui_elements["results"].insert("end", f"Error querying {record_type}: {str(e)}\n")
                continue

        return results

    def run(self) -> None:
        domain = self.get_option_value("domain")
        record_types = [t.strip() for t in self.get_option_value("record_types").split(",")]

        if not domain:
            self._ui_elements["results"].insert("end", "Error: Domain required\n")
            return

        self._ui_elements["results"].insert("end", f"Starting DNS enumeration for {domain}...\n")

        results = asyncio.run(self.enumerate_dns(domain, record_types))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("nexushound/results/dns_enum")
        results_dir.mkdir(parents=True, exist_ok=True)
        file_path = results_dir / f"dns_{timestamp}.json"

        with open(file_path, "w") as f:
            json.dump(results, f, indent=4)

        options = {
            "domain": domain,
            "record_types": record_types
        }
        self.db.save_result(self.id, str(file_path), options)

        self._ui_elements["results"].insert("end", f"\nScan complete! Found {len(results)} records\n")
        self._ui_elements["results"].insert("end", f"Results saved to: {file_path}\n")