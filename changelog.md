# Changelog

Toutes les modifications importantes de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/lang/fr/).

## [2025.1.3] - 2025-06-04

### Ajouté
- **Sélection par objet parent** : Plus besoin de sélectionner directement la caméra projecteur
- **Recherche automatique** des projecteurs dans la hiérarchie d'enfants (recherche récursive)
- **Interface utilisateur améliorée** :
  - Affichage du nom de la caméra projecteur actuellement gérée
  - Bouton **"Focus"** : Zoom sur l'objet sélectionné (équivalent à "View Selected")
  - Bouton **"POV"** : Basculer en vue caméra (équivalent à "View Camera")
  - Bouton **"Screen ON/OFF"** : Masquer/afficher les objets contenant "écran" ou "screen" dans leur nom
  - Bouton **"Light ON/OFF"** : Contrôler la visibilité et le rendu de la lumière projecteur
- **Exposition des custom properties** dans l'interface :
  - `SCREEN_DISTANCE` : Distance à l'écran
  - `VP_PAN` : Contrôle de panoramique virtuel
  - `VP_TILT` : Contrôle d'inclinaison virtuel
  - `VP_DOUBLE_PAN` : Contrôle de double panoramique
- **Recherche récursive avancée** pour les objets écran dans toute la hiérarchie
- **Synchronisation complète** des systèmes de visibilité (viewport + render pour la lumière)
- **Résolutions VP** il manquait 3840x2400 en 16:10

### Modifié
- **Nom de l'onglet** : "Projector" → "Proj By Lotchi"
- **Fonctions de sélection** : `get_projector()` et `get_projectors()` améliorées dans `helper.py`
- **Interface utilisateur** : Réorganisation avec section d'information sur la caméra gérée
- **Système de contrôles** : Boutons d'action groupés pour un accès rapide
- **Recherche d'objets** : Amélioration de la recherche récursive dans les hiérarchies complexes

### Corrigé
- **Problème de sélection** : Plus besoin de cliquer directement sur la caméra projecteur
- **Détection des objets écran** : Recherche maintenant dans toute la hiérarchie d'objets
- **Cohérence des systèmes de visibilité** : Distinction claire entre visibilité viewport et rendu
- **Mise à jour de l'interface** : Rafraîchissement automatique des états des boutons

### Technique
- **Nouveaux opérateurs Blender** :
  - `PROJECTOR_OT_focus_selected` : Focalisation sur objet
  - `PROJECTOR_OT_view_camera` : Vue caméra
  - `PROJECTOR_OT_toggle_screen` : Basculement écran
  - `PROJECTOR_OT_toggle_light` : Basculement lumière
- **Fonctions helper** pour la gestion dynamique des boutons
- **Amélioration de la recherche récursive** d'objets dans les hiérarchies Blender
- **Gestion des custom properties** directement depuis l'objet parent sélectionné

---

## [2024.1.1] - 2024-01-01

### Ajouté
- Création facile et modification de projecteurs basés sur la physique
- Paramètres de projecteur réalistes (throw ratio, résolution, lens shift)
- Projection de textures de test ou de contenu personnalisé (images et vidéos)
- Aperçu des projections en mode rendu Cycles
- Support pour différentes résolutions :
  - 16:10 (WXGA, WXGA+, WUXGA)
  - 16:9 (720p, 1080p, 4K Ultra HD)
  - 4:3 (SVGA, XGA, SXGA+, UXGA)
  - 17:9 (4K Natif)
  - 1:1 (Carré)
- Textures projetées : Checker, Color Grid, Custom Texture
- Contrôle de la puissance du projecteur
- Décalage de lentille horizontal et vertical
- Grille de pixels pour visualisation
- Couleurs aléatoires pour les textures checker

### Modifié
- Compatible avec Blender 2.81+
- Optimisé pour Cycles (Eevee sera supporté quand la fonctionnalité sera implémentée)

### Technique
- Utilisation de nodes Shader pour la projection
- Système de groupes de nœuds pour l'organisation
- Propriétés personnalisées pour les paramètres du projecteur
- Tests unitaires inclus

---

## Format des versions

### Types de changements
- **Ajouté** : pour les nouvelles fonctionnalités
- **Modifié** : pour les changements dans les fonctionnalités existantes
- **Déprécié** : pour les fonctionnalités qui seront supprimées
- **Supprimé** : pour les fonctionnalités supprimées
- **Corrigé** : pour les corrections de bugs
- **Sécurité** : en cas de vulnérabilités

### Numérotation des versions
Le projet utilise le format `ANNÉE.MAJEUR.MINEUR` :

- **ANNÉE** : Année de sortie (ex: 2024)
- **MAJEUR** : Changements majeurs ou breaking changes (ex: 1, 2, 3...)
- **MINEUR** : Corrections de bugs et petites améliorations (ex: 1, 2, 3...)

**Exemple :** `2024.2.1` = Version 2.1 de l'année 2024