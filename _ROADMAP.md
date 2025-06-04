# 🛣️ Roadmap - Projectors By Lotchi

Ce document liste toutes les fonctionnalités prévues pour les futures versions de l'addon.

## 🎯 Priorités de développement

### ⭐⭐⭐ Haute priorité
- [x] Sélection multiple d'objets 
- [x] Calculs techniques (Lux + taille pixel)
- [x] Ajustement automatique taille écran
- [x] Définir si c'est Portrait ou paysage 
- [x] Option Paysage Dual disponible, si coché double ligne dans CSV, et visibilité d'un objet dont le nom contient "dual"
- [x] Export CSV des données
- [x] Offset automatique de l'écran avec shift caméra
- [ ] Base de données de projecteurs
- [ ] Fonction Mirror XZ, si c'est Portrait tel Mirror, si c'est Paysage tel Mirror
- [ ] Bouton Dupliquer Mirror Renommer Delete

### ⭐⭐ Moyenne priorité  
- [ ] Patterns de test simples (WHITE, BLUE, etc.)
- [ ] Faire une explication sur comment riger un nouveau VP
- [ ] texturing de VP, mettre une couleur sur un VP (noir, rose, cyan, jaune)
- [ ] Avoir un bouton Open wider throw ratio -+15% (présent meme en sélection de groupe ?), changer aussi la résolution du projet ?
- [ ] Exporter les POV VP en batch, demander un dossier de destination
- [ ] Ajouter le control de la hauteur dans l'UI

### ⭐ Basse priorité
- [ ] Auto detect de la cible la plus proche ? jouer sur distance ecran
- [ ] Avoir un bouton ajout VP Paysage et Portrait .blend
- [ ] Interface avancée de sélection

---

## 📊 Calculs Techniques

### Fonctionnalité : Affichage Lux et Taille Pixel
**Objectif :** Calculer et afficher en temps réel les informations techniques du projecteur.

**Formules à implémenter :**
```python
def calculate_lux(power_lumens_ansi, screen_width, screen_height):
    """
    Calcule les lux sur l'écran
    Lux = Lumens ANSI / Surface_écran_m²
    Utiliser les lumens ANSI pour calculs précis
    """
    surface_m2 = (screen_width * screen_height)
    return power_lumens_ansi / surface_m2

def calculate_pixel_size(screen_width, screen_height, resolution):
    """
    Calcule la taille physique d'un pixel sur l'écran
    """
    res_w, res_h = resolution.split('x')
    pixel_width = screen_width / float(res_w)
    pixel_height = screen_height / float(res_h)
    return pixel_width, pixel_height

def calculate_screen_size(throw_ratio, screen_distance, resolution):
    """
    Calcule la taille de l'écran selon throw ratio et distance
    """
    # Largeur image = distance / throw_ratio
    screen_width = screen_distance / throw_ratio
    
    # Hauteur selon aspect ratio de la résolution
    res_w, res_h = resolution.split('x')
    aspect_ratio = float(res_w) / float(res_h)
    screen_height = screen_width / aspect_ratio
    
    return screen_width, screen_height