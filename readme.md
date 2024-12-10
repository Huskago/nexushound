# NexusHound

NexusHound is a modular security and auditing framework, designed to be extensible and easy to use. It features an intuitive graphical interface and a collection of modules for different types of testing.

## Features

- 🔍 Intuitive graphical interface with CustomTkinter
- 🧩 Extensible modular architecture
- 💾 Results management in SQLite database
- 📝 Integrated wordlist system
- 🔒 Module security checks
- 📊 Real-time visualization of results

## Available modules

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
- Detection of open redirects
- Detailed reporting

## Installation

```bash
# Clone repository
git clone https://github.com/Huskago/nexushound.git
cd nexushound

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate # Linux/Mac
# or
.venv\Scripts\activate # Windows

# Install dependencies
pip install -r requirements.txt
```

## Use

```bash
python -m nexushound
```

## Developing a new module

Modules must inherit from the `ModuleBase` class and implement the required methods

Translated with DeepL.com (free version)
