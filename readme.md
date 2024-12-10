# NexusHound

NexusHound is a modular security and auditing framework, designed to be extensible and easy to use. It offers an intuitive graphical interface and a collection of modules for different types of tests.

## Features

- 🔍 Intuitive GUI with CustomTkinter
- 🧩 Extensible modular architecture
- 💾 SQLite database results management
- 📝 Integrated wordlist system
- 🔒 Module security check
- 📊 Real-time results visualization

## Available Modules

### GoBuster
- Web directory scanner
- Custom wordlist support
- HTTP code filtering
- Asynchronous scanning for better performance

### DNS Enumerator
- DNS record enumeration
- Support for multiple record types (A, AAAA, MX, NS, TXT, CNAME, SOA)
- Detailed results analysis

### VulnScanner
- Detection of common web vulnerabilities
- XSS, SQLi, LFI, RFI, SSRF tests
- Redirect opening detection
- Detailed Reports

## Installation

```bash
# Clone the repository
git clone https://github.com/Huskago/nexushound.git
cd nexushound

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate # Linux/Mac
#or
.venv\Scripts\activate # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python -m nexushound
```

## Develop a New Module

Modules must inherit from the `ModuleBase` class and implement the required methods:

```python
class MyModule(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "MyModule"
        self.description = "Module Description"
        self.category = "Category"
        soi.options = [
            ModuleOption(
                name="option1",
                description="Option description",
                type="str",
                default=""
            )
        ]

    def run(soi):
        # Module Logic
        pass
```

## File Structure

```
nexushound/
├── database/
│ ├── __init__.py
│ ├── manager.py
│ └── schema.sql
├──gui/
│ ├── components/
│ │ ├── module_view.py
│ │ ├── search_bar.py
│ │ └── sidebar.py
│ └── app.py
├──modules/
├──wordlists/
└──results/
```

## Contributions

Contributions are welcome! To contribute:
1. Fork the project
2. Branch your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

##Security

**Important**: Use this tool only on systems for which you have explicit permission from testers.

## License

MIT License - see the LICENSE file for details.

## Authors

- Huskago - [Github](https://github.com/Huskago)
- mushin - [Github](https://github.com/patrick-4505)
