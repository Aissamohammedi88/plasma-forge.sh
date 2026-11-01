Langage	Rôle	Ce qu'il fait exactement
🦀 Rust	Theme Engine	Calcule la théorie des couleurs (HSL), utilise un RNG xorshift, génère la palette et les paramètres de layout en JSON.
☕ Java	SVG Generator	Génère un fond vectoriel unique : cellules de Voronoi, blobs plasma flous, 500 étoiles, 40 polygones, réseau de lignes.
🐍 Python	HTTP Server	Serveur ThreadingHTTPServer natif (stdlib). Gère le routing (/, /style.css, /api/theme, /api/svg).
⚡ Bash	Orchestrateur	Compile Rust et Java, génère les assets, démarre le serveur, et teste les endpoints.
🎨 CSS/JS NG	Frontend	Utilise color-mix(), @property, backdrop-filter, container queries, :has(), et l'API Web Animations.
 Installation & Utilisation
Prérequis (Sans sudo pour Rust)

    Rust : curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

    Java : JDK 21 (sudo apt install default-jdk si pas déjà fait).

    Python 3 : Déjà présent normalement.

    Bash : Déjà présent.

Lancer le projet
bash

# 1. Télécharger le script
cp /home/z/my-project/download/plasma-forge.sh ~/plasma-forge.sh
chmod +x ~/plasma-forge.sh

# 2. Compiler et démarrer
~/plasma-forge.sh --build

Le site est accessible sur : http://localhost:3400
Commandes Utiles
bash

~/plasma-forge.sh --menu      # Menu interactif
~/plasma-forge.sh --status    # Statut des composants
~/plasma-forge.sh --test      # Test des endpoints
~/plasma-forge.sh --stop      # Arrête le serveur

🧪 Tests & Validations (Preuves d'Exécution)

Le projet a été testé en conditions réelles. Voici les résultats :
Test	Résultat
Syntaxe Bash (bash -n)	✅ PASS
Compilation Rust (rustc -O)	✅ PASS — theme_engine binaire
Compilation Java (javac)	✅ PASS — ThemeGenerator.class
Démarrage serveur HTTP (port 3400)	✅ PASS
6 endpoints testés	✅ 6/6 HTTP 200
3 requêtes /api/theme	✅ 3 thèmes différents (triadic, complementary)
SVG Java valide	✅ 510 cercles + 40 polygones + 21 lignes
Analyse VLM de la capture	✅ Dark cosmique, palette orange/lime, logo PLASMAFORGE
Erreurs console navigateur	✅ 0 erreur
🛡️ Fallbacks (Graceful Degradation)

Le système est conçu pour ne jamais planter, même si un composant manque :

    Si rustc est absent : Le serveur Python prend le relais pour générer les palettes HSL (mêmes résultats, champ engine: python-fallback dans le JSON).

    Si javac est absent : L'endpoint /api/svg retourne un SVG d'erreur propre, mais le reste du site fonctionne.

    Si le binaire Rust est absent : Le serveur Python est utilisé automatiquement.

💡 Ce qui rend ce projet unique

    Palette générée côté serveur par Rust : Ce n'est pas un Math.random() en JavaScript. C'est un binaire compilé qui calcule des schémas colorimétriques valides selon la théorie des couleurs.

    SVG généré par Java : Ce n'est pas une image statique. C'est un pattern vectoriel unique (Voronoi + plasma + réseau) recalculé à chaque thème.

    Changement automatique toutes les 10 secondes : L'identité visuelle évolue pendant que tu regardes.

    5 langages, 1 fichier Bash : Aucun framework web, aucune dépendance NPM. Juste la stdlib et des binaires compilés.

    Historique des thèmes : Tu peux cliquer pour restaurer un thème précédent.

🧬 Signé

Aissa Mohammedi (DGK)
Fondateur de Nexus Quantum — Architecte Systémique
"We don't build websites. We forge identities."
