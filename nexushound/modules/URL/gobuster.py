from nexushound.modules_manager import ModuleBase, ModuleOption, WordlistOption
import aiohttp
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import customtkinter as ctk


class GoBuster(ModuleBase):
    def __init__(self) -> None:
        super().__init__()
        self.name = "GoBuster"
        self.version = "0.1.0"
        self.description = "Web directory and file brute forcing tool"
        self.category = "URL"
        self.is_public = True
        self.authors = ["NexusHound"]
        self.homepage = ""
        self.license = "MIT"
        self.dependencies = ["requests"]
        self.min_python_version = "3.10"
        self.tags = ["bruteforce", "directory", "files"]
        self.repository = ""

        # Define module options
        self.options = [
            ModuleOption(
                name="url",
                description="Target URL",
                type="str",
                default="",
                required=True
            ),
            WordlistOption(
                name="wordlist",
                description="Wordlist for directory/file enumeration",
                required=True
            ),
            ModuleOption(
                name="threads",
                description="Number of threads",
                type="int",
                default=10,
                required=False
            ),
            ModuleOption(
                name="status_codes",
                description="Valid status codes (comma-separated)",
                type="str",
                default="200,204,301,302,307,401,403",
                required=False
            )
        ]

        self._results = []
        self._progress = 0
        self._total = 0

    def create_ui(self, parent: ctk.CTkBaseClass) -> None:
        self._ui_elements["progress_label"] = ctk.CTkLabel(parent, text="Progress: 0%")
        self._ui_elements["progress_label"].pack(pady=5)

        self._ui_elements["progress_bar"] = ctk.CTkProgressBar(parent)
        self._ui_elements["progress_bar"].pack(fill="x", padx=5, pady=5)
        self._ui_elements["progress_bar"].set(0)

        self._ui_elements["results"] = ctk.CTkTextbox(parent, height=200)
        self._ui_elements["results"].pack(fill="both", expand=True, padx=5, pady=5)

    async def scan_url(self, session: aiohttp.ClientSession, url: str, status_codes: List[int]) -> Optional[Dict]:
        try:
            async with session.get(url, timeout=10) as response:
                self._progress += 1
                progress = (self._progress / self._total) * 100
                self._ui_elements["progress_bar"].set(progress/100)
                self._ui_elements["progress_label"].configure(text=f"Progress: {progress:.1f}%")

                self._ui_elements["results"].insert("end", f"Scanning {url} - Status: {response.status}\n")

                if response.status in status_codes:
                    return {
                        "url": url,
                        "status": response.status,
                        "size": len(await response.text())
                    }
                    self._ui_elements["results"].insert("end", f"Found: {url}\n")
                    return result
        except:
            self._ui_elements["results"].insert("end", f"Error scanning: {url}\n")
        return None

    async def run_scan(self, base_url: str, words: List[str],
                       threads: int, status_codes: List[int]) -> List[Dict]:
        if not base_url.endswith('/'):
            base_url += '/'

        self._total = len(words)
        self._progress = 0

        try:
            connector = aiohttp.TCPConnector(limit=threads)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = []
                for word in words:
                    url = base_url + word
                    tasks.append(self.scan_url(session, url, status_codes))

                results = await asyncio.gather(*tasks)
                return [r for r in results if r is not None]
        except Exception as e:
            self._ui_elements["results"].insert("end", f"Error during scan: {str(e)}\n")
            return []

    def save_results(self, results: List[Dict]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("nexushound/results/gobuster")
        results_dir.mkdir(parents=True, exist_ok=True)

        file_path = results_dir / f"scan_{timestamp}.json"
        with open(file_path, "w") as f:
            json.dump(results, f, indent=4)

        return str(file_path)

    def run(self) -> None:
        url = self.get_option_value("url")
        wordlist_id = self.get_option_value("wordlist")
        threads = self.get_option_value("threads")
        status_codes = [int(code.strip()) for code in self.get_option_value("status_codes").split(",")]

        if not url:
            self._ui_elements["results"].insert("end", "Error: URL required\n")
            return

        if wordlist_id is None:
            self._ui_elements["results"].insert("end", "Error: No wordlist selected\n")
            return

        wordlist = self.db.get_wordlist(wordlist_id)
        if not wordlist:
            self._ui_elements["results"].insert("end", f"Error: Could not find wordlist with ID {wordlist_id}\n")
            return

        words = wordlist['elements']
        if not words:
            self._ui_elements["results"].insert("end", "Error: Wordlist is empty\n")
            return

        self._ui_elements["results"].insert("end", f"Starting scan of {url}\n")
        self._ui_elements["results"].insert("end", f"Using wordlist: {wordlist['name']} ({len(words)} words)\n")

        results = asyncio.run(self.run_scan(url, words, threads, status_codes))

        file_path = self.save_results(results)
        options = {
            "url": url,
            "threads": threads,
            "status_codes": status_codes,
        }
        self.db.save_result(self.id, file_path, options)

        self._ui_elements["results"].insert("end", f"\nScan complete! Found {len(results)} results\n")
        self._ui_elements["results"].insert("end", f"Results saved to: {file_path}\n\n")

        for result in results:
            self._ui_elements["results"].insert("end",
                f"[{result['status']}] {result['url']} ({result['size']} bytes)\n")