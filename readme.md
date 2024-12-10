# NexusHound

NexusHound est un framework modulaire de sécurité et d'audit, conçu pour être extensible et facile à utiliser. Il propose une interface graphique intuitive et une collection de modules pour différents types de tests.

## Fonctionnalités

- 🔍 Interface graphique intuitive avec CustomTkinter
- 🧩 Architecture modulaire extensible
- 💾 Gestion des résultats en base de données SQLite
- 📝 Système de wordlists intégré
- 🔒 Vérification de sécurité des modules
- 📊 Visualisation des résultats en temps réel

## Modules Disponibles

### GoBuster
- Scanner de répertoires web
- Support des wordlists personnalisées
- Filtrage par codes HTTP
- Scan asynchrone pour de meilleures performances

### DNS Enumerator
- Enumération de records DNS
- Support de multiples types d'enregistrements (A, AAAA, MX, NS, TXT, CNAME, SOA)
- Analyse détaillée des résultats

### VulnScanner
- Détection de vulnérabilités web courantes
- Tests XSS, SQLi, LFI, RFI, SSRF
- Détection d'open redirects
- Rapports détaillés

## Installation

```bash
# Cloner le repository
git clone https://github.com/Huskago/nexushound.git
cd nexushound

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

```bash
python -m nexushound
```

## Développer un Nouveau Module

Les modules doivent hériter de la classe `ModuleBase` et implémenter les méthodes requises :

```python
class MyModule(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "MonModule"
        self.description = "Description du module"
        self.category = "Catégorie"
        self.options = [
            ModuleOption(
                name="option1",
                description="Description de l'option",
                type="str",
                default=""
            )
        ]

    def run(self):
        # Logique du module
        pass
```

## Structure des Fichiers

```
nexushound/
├── database/
│   ├── __init__.py
│   ├── manager.py
│   └── schema.sql
├── gui/
│   ├── components/
│   │   ├── module_view.py
│   │   ├── search_bar.py
│   │   └── sidebar.py
│   └── app.py
├── modules/
│   ├── DNS/
│   ├── Security/
│   └── URL/
├── wordlists/
└── results/
```

## Contributions

Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez sur la branche
5. Créez une Pull Request

## Sécurité

**Important** : Utilisez cet outil uniquement sur des systèmes pour lesquels vous avez l'autorisation explicite de les tester.

## License

MIT License - voir le fichier LICENSE pour plus de détails.

## Auteurs

- Huskago - [Github](https://github.com/Huskago)
- mushin - [Github](https://github.com/patrick-4505) 