# Coefficient correcteur pour les shift Barco (valeurs constructeur ÷ 2)
BARCO_SHIFT_COEFFICIENT = 0.5

# Base de données des projecteurs
PROJECTOR_DATABASE = {
    'Barco': {
        # Série G62 (ANSI lumens confirmées)
        'G62-W9': {
            '0.36:1 G LENS UST (R9801785)': {'ansi_lumens': 9000, 'v_shift_min': 182, 'v_shift_max': 186, 'h_shift_min': 0, 'h_shift_max': 0},
            '0.37-0.4:1 G LENS UST 90° (R9801830)': {'ansi_lumens': 9000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.65-0.75:1 G LENS (R9802300)': {'ansi_lumens': 9000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.75-0.95:1 G LENS (R9801840)': {'ansi_lumens': 9000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.95-1.22:1 G LENS (R9832755)': {'ansi_lumens': 9000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.22-1.53:1 G LENS (R9801784)': {'ansi_lumens': 9000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.52-2.92:1 G LENS (R9832756)': {'ansi_lumens': 9000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.90-5.50:1 G LENS (R9832778)': {'ansi_lumens': 9000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
        },
        'G62-W11': {
            '0.36:1 G LENS UST (R9801785)': {'ansi_lumens': 11000, 'v_shift_min': 182, 'v_shift_max': 186, 'h_shift_min': 0, 'h_shift_max': 0},
            '0.37-0.4:1 G LENS UST 90° (R9801830)': {'ansi_lumens': 11000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.65-0.75:1 G LENS (R9802300)': {'ansi_lumens': 11000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.75-0.95:1 G LENS (R9801840)': {'ansi_lumens': 11000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.95-1.22:1 G LENS (R9832755)': {'ansi_lumens': 11000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.22-1.53:1 G LENS (R9801784)': {'ansi_lumens': 11000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.52-2.92:1 G LENS (R9832756)': {'ansi_lumens': 11000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.90-5.50:1 G LENS (R9832778)': {'ansi_lumens': 11000, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
        },
        'G62-W14': {
            '0.36:1 G LENS UST (R9801785)': {'ansi_lumens': 11500, 'v_shift_min': 182, 'v_shift_max': 186, 'h_shift_min': 0, 'h_shift_max': 0},
            '0.37-0.4:1 G LENS UST 90° (R9801830)': {'ansi_lumens': 11500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.65-0.75:1 G LENS (R9802300)': {'ansi_lumens': 11500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -40, 'h_shift_max': 40},
            '0.75-0.95:1 G LENS (R9801840)': {'ansi_lumens': 11500, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.95-1.22:1 G LENS (R9832755)': {'ansi_lumens': 11500, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.22-1.53:1 G LENS (R9801784)': {'ansi_lumens': 11500, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.52-2.92:1 G LENS (R9832756)': {'ansi_lumens': 11500, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.90-5.50:1 G LENS (R9832778)': {'ansi_lumens': 11500, 'v_shift_min': -100, 'v_shift_max': 100, 'h_shift_min': -30, 'h_shift_max': 30},
        },
        'G100-W16': {
            '0.38:1 FLDX UST 90° (R9801832)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 90, 'h_shift_min': 0, 'h_shift_max': 50},
            '0.65-0.75:1 GC LENS (R9802188)': {'ansi_lumens': 14500, 'v_shift_min': -102, 'v_shift_max': 102, 'h_shift_min': -48, 'h_shift_max': 48},
            '0.84-1.02:1 GC LENS (R9802181)': {'ansi_lumens': 14500, 'v_shift_min': -74, 'v_shift_max': 74, 'h_shift_min': -26, 'h_shift_max': 26},
            '1.02-1.36:1 GC LENS (R9802182)': {'ansi_lumens': 14500, 'v_shift_min': -82, 'v_shift_max': 82, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.2-1.5:1 GC LENS (R9802183)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '1.5-2.0:1 GC LENS (R9802184)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '2.0-4.0:1 GC LENS (R9802185)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '4.0-7.2:1 GC LENS (R9802186)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '7.2-10.8:1 GC LENS (R9802187)': {'ansi_lumens': 14500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
        },
        'G100-W19': {
            '0.38:1 FLDX UST 90° (R9801832)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 90, 'h_shift_min': 0, 'h_shift_max': 50},
            '0.65-0.75:1 GC LENS (R9802188)': {'ansi_lumens': 16000, 'v_shift_min': -102, 'v_shift_max': 102, 'h_shift_min': -48, 'h_shift_max': 48},
            '0.84-1.02:1 GC LENS (R9802181)': {'ansi_lumens': 16000, 'v_shift_min': -74, 'v_shift_max': 74, 'h_shift_min': -26, 'h_shift_max': 26},
            '1.02-1.36:1 GC LENS (R9802182)': {'ansi_lumens': 16000, 'v_shift_min': -82, 'v_shift_max': 82, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.2-1.5:1 GC LENS (R9802183)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '1.5-2.0:1 GC LENS (R9802184)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '2.0-4.0:1 GC LENS (R9802185)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '4.0-7.2:1 GC LENS (R9802186)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '7.2-10.8:1 GC LENS (R9802187)': {'ansi_lumens': 16000, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
        },
        'G100-W22': {
            '0.38:1 FLDX UST 90° (R9801832)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 90, 'h_shift_min': 0, 'h_shift_max': 50},
            '0.65-0.75:1 GC LENS (R9802188)': {'ansi_lumens': 18500, 'v_shift_min': -102, 'v_shift_max': 102, 'h_shift_min': -48, 'h_shift_max': 48},
            '0.84-1.02:1 GC LENS (R9802181)': {'ansi_lumens': 18500, 'v_shift_min': -74, 'v_shift_max': 74, 'h_shift_min': -26, 'h_shift_max': 26},
            '1.02-1.36:1 GC LENS (R9802182)': {'ansi_lumens': 18500, 'v_shift_min': -82, 'v_shift_max': 82, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.2-1.5:1 GC LENS (R9802183)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '1.5-2.0:1 GC LENS (R9802184)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '2.0-4.0:1 GC LENS (R9802185)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '4.0-7.2:1 GC LENS (R9802186)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '7.2-10.8:1 GC LENS (R9802187)': {'ansi_lumens': 18500, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
        },
        'G100-W25': {
            '0.38:1 FLDX UST 90° (R9801832)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 90, 'h_shift_min': 0, 'h_shift_max': 50},
            '0.65-0.75:1 GC LENS (R9802188)': {'ansi_lumens': 21100, 'v_shift_min': -102, 'v_shift_max': 102, 'h_shift_min': -48, 'h_shift_max': 48},
            '0.84-1.02:1 GC LENS (R9802181)': {'ansi_lumens': 21100, 'v_shift_min': -74, 'v_shift_max': 74, 'h_shift_min': -26, 'h_shift_max': 26},
            '1.02-1.36:1 GC LENS (R9802182)': {'ansi_lumens': 21100, 'v_shift_min': -82, 'v_shift_max': 82, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.2-1.5:1 GC LENS (R9802183)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '1.5-2.0:1 GC LENS (R9802184)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '2.0-4.0:1 GC LENS (R9802185)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '4.0-7.2:1 GC LENS (R9802186)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
            '7.2-10.8:1 GC LENS (R9802187)': {'ansi_lumens': 21100, 'v_shift_min': -120, 'v_shift_max': 120, 'h_shift_min': -50, 'h_shift_max': 50},
        },
        
        # Série I600 4K15 (ANSI lumens confirmées)
        'I600-4K8': {
            '0.37:1 ILD UST (R9803077)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.5:1 ILD UST (R9803076)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.65-0.8:1 ILD ST (R9803072)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.8-1.0:1 ILD ST (R9803071)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.0-1.4:1 ILD (R9803070)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.4-2.1:1 ILD (R9803061)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.1-4.0:1 ILD (R9803075)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '4.0-7.4:1 ILD (R9803073)': {'ansi_lumens': 7500, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
        },
        'I600-4K10': {
            '0.37:1 ILD UST (R9803077)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.5:1 ILD UST (R9803076)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.65-0.8:1 ILD ST (R9803072)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.8-1.0:1 ILD ST (R9803071)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.0-1.4:1 ILD (R9803070)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.4-2.1:1 ILD (R9803061)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.1-4.0:1 ILD (R9803075)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '4.0-7.4:1 ILD (R9803073)': {'ansi_lumens': 10000, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
        },
        'I600-4K15': {
            '0.37:1 ILD UST (R9803077)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.5:1 ILD UST (R9803076)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.65-0.8:1 ILD ST (R9803072)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '0.8-1.0:1 ILD ST (R9803071)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.0-1.4:1 ILD (R9803070)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '1.4-2.1:1 ILD (R9803061)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '2.1-4.0:1 ILD (R9803075)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
            '4.0-7.4:1 ILD (R9803073)': {'ansi_lumens': 13800, 'v_shift_min': -110, 'v_shift_max': 110, 'h_shift_min': -30, 'h_shift_max': 30},
        }
    }
}

def get_brands(self, context):
    return [(brand, brand, '') for brand in PROJECTOR_DATABASE.keys()]

def get_models(self, context):
    from .helper import get_projector
    projector = get_projector(context)
    if not projector or not projector.proj_settings.projector_brand:
        return [('NONE', 'Select Brand First', '')]
    
    brand = projector.proj_settings.projector_brand
    if brand in PROJECTOR_DATABASE:
        return [(model, model, '') for model in PROJECTOR_DATABASE[brand].keys()]
    return [('NONE', 'No Models', '')]

def get_lenses(self, context):
    from .helper import get_projector
    projector = get_projector(context)
    if not projector or not projector.proj_settings.projector_brand or not projector.proj_settings.projector_model:
        return [('NONE', 'Select Model First', '')]
    
    brand = projector.proj_settings.projector_brand
    model = projector.proj_settings.projector_model
    
    if brand in PROJECTOR_DATABASE and model in PROJECTOR_DATABASE[brand]:
        # TOUJOURS inclure NONE comme première option
        lenses = [('NONE', '-- Select Lens --', '')]
        lenses.extend([(lens, lens, '') for lens in PROJECTOR_DATABASE[brand][model].keys()])
        return lenses
    return [('NONE', 'No Lenses', '')]

def update_projector_brand(proj_settings, context):
    proj_settings.projector_model = 'NONE'
    proj_settings.projector_lens = 'NONE'

def update_projector_model(proj_settings, context):
    proj_settings.projector_lens = 'NONE'
    
    # Mettre à jour les lumens selon le modèle choisi
    brand = proj_settings.projector_brand
    model = proj_settings.projector_model
    
    print(f"DEBUG: update_projector_model called - Brand: {brand}, Model: {model}")  # DEBUG
    
    if (brand in PROJECTOR_DATABASE and 
        model in PROJECTOR_DATABASE[brand]):
        
        # Prendre la première optique du modèle pour récupérer les lumens
        first_lens = next(iter(PROJECTOR_DATABASE[brand][model].values()))
        new_lumens = first_lens['ansi_lumens']
        
        print(f"DEBUG: Setting lumens to {new_lumens}")  # DEBUG
        proj_settings.lumens = new_lumens
        
        # Forcer le rafraîchissement de l'interface
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    else:
        print(f"DEBUG: Brand/Model not found in database")  # DEBUG

def update_projector_lens(proj_settings, context):
    brand = proj_settings.projector_brand
    model = proj_settings.projector_model
    lens = proj_settings.projector_lens
    
    if (brand in PROJECTOR_DATABASE and 
        model in PROJECTOR_DATABASE[brand] and 
        lens in PROJECTOR_DATABASE[brand][model]):
        
        lens_data = PROJECTOR_DATABASE[brand][model][lens]
        
        # Appliquer SEULEMENT les valeurs ANSI lumens et shift ranges (PAS le throw ratio)
        proj_settings.lumens = lens_data['ansi_lumens']
        
        # Appliquer le coefficient correcteur Barco pour les shift ranges
        proj_settings.v_shift_min = lens_data['v_shift_min'] * BARCO_SHIFT_COEFFICIENT
        proj_settings.v_shift_max = lens_data['v_shift_max'] * BARCO_SHIFT_COEFFICIENT  
        proj_settings.h_shift_min = lens_data['h_shift_min'] * BARCO_SHIFT_COEFFICIENT
        proj_settings.h_shift_max = lens_data['h_shift_max'] * BARCO_SHIFT_COEFFICIENT