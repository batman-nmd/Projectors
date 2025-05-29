# 🛣️ Roadmap - Projectors By Lotchi

Ce document liste toutes les fonctionnalités prévues pour les futures versions de l'addon.

## 🎯 Priorités de développement

### ⭐⭐⭐ Haute priorité
- [x] Sélection multiple d'objets 
- [ ] Fonction symétrie XZ
- [ ] Patterns de test simples (WHITE, BLUE, etc.)
- [ ] Calculs techniques (Lux + taille pixel)
- [ ] Ajustement automatique taille écran

### ⭐⭐ Moyenne priorité  
- [ ] Offset automatique de l'écran avec shift caméra
- [ ] Base de données de projecteurs
- [ ] Export CSV des données

### ⭐ Basse priorité
- [ ] Interface avancée de sélection
- [ ] Auto detect de la cible la plus proche ? distance ecran

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