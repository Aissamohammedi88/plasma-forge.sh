<div align="center">
  <h1>🌌 PLASMAFORGE</h1>
  <p><strong>The Algorithmic Identity Generator.</strong></p>
  <p>Un site web qui régénère son identité visuelle à chaque visite. Zéro framework, zéro dépendance NPM. Juste du code pur.</p>
  
  [![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)](#)
  [![Java](https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)](#)
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
  [![Bash](https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnu-bash&logoColor=white)](#)
  [![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](#)
</div>

---

## 🧬 Overview

**PLASMAFORGE** n'est pas un site web statique. C'est un **moteur de génération d'identité visuelle procédurale**. 

À chaque requête, le serveur calcule une nouvelle théorie des couleurs (monochromatique, complémentaire, triadique, tétradique), génère un nouveau fond d'écran SVG vectoriel unique (Voronoi, plasma, étoiles), et l'envoie au navigateur. L'identité visuelle du site évolue en temps réel.

**La règle de PLASMAFORGE :** *Pas d'images statiques. Pas de frameworks. Juste des mathématiques et des binaires compilés.*

---

## ⚙️ Architecture Multi-Langages

C'est la vraie prouesse de ce projet : **5 langages de programmation collaborent dans un seul fichier Bash**, sans aucun framework web externe.

```mermaid
graph TD
    A[Bash Orchestrateur] -->|Compile| B(Rust Theme Engine)
    A -->|Compile| C(Java SVG Generator)
    A -->|Lance| D(Python HTTP Server)
    
    B -->|Génère JSON Palette| D
    C -->|Génère SVG Background| D
    
    D -->|Sert HTML/CSS/JS| E[Navigateur Client]
    E -->|Toutes les 10s| D
    
    style A fill:#4EAA25,color:#fff
    style B fill:#000000,color:#fff
    style C fill:#ED8B00,color:#000
    style D fill:#3776AB,color:#fff
    style E fill:#00ff9d,color:#000
