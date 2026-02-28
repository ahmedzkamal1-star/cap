"""
Theme management for El-Dahih application
Supports Light, Dark, and Gold themes
"""
from kivy.utils import get_color_from_hex
import logging

logger = logging.getLogger(__name__)


class ThemeManager:
    """Manages application themes"""
    
    # Light Theme Colors
    LIGHT_THEME = {
        'primary': get_color_from_hex("#00A8E8"),
        'primary_dark': get_color_from_hex("#0088CC"),
        'accent': get_color_from_hex("#FFD700"),
        'background': get_color_from_hex("#FFFFFF"),
        'surface': get_color_from_hex("#F5F9FD"),
        'text_primary': get_color_from_hex("#212121"),
        'text_secondary': get_color_from_hex("#757575"),
        'divider': get_color_from_hex("#BDBDBD"),
        'error': get_color_from_hex("#F44336"),
        'success': get_color_from_hex("#4CAF50"),
        'warning': get_color_from_hex("#FF9800"),
    }
    
    # Dark Theme Colors
    DARK_THEME = {
        'primary': get_color_from_hex("#0D47A1"),
        'primary_dark': get_color_from_hex("#0A3A7A"),
        'accent': get_color_from_hex("#FFD700"),
        'background': get_color_from_hex("#121212"),
        'surface': get_color_from_hex("#1E1E1E"),
        'text_primary': get_color_from_hex("#FFFFFF"),
        'text_secondary': get_color_from_hex("#BDBDBD"),
        'divider': get_color_from_hex("#424242"),
        'error': get_color_from_hex("#CF6679"),
        'success': get_color_from_hex("#81C784"),
        'warning': get_color_from_hex("#FFB74D"),
    }
    
    # Gold Theme Colors
    GOLD_THEME = {
        'primary': get_color_from_hex("#FFD700"),
        'primary_dark': get_color_from_hex("#FFC700"),
        'accent': get_color_from_hex("#00A8E8"),
        'background': get_color_from_hex("#FFFEF0"),
        'surface': get_color_from_hex("#FFF9E6"),
        'text_primary': get_color_from_hex("#3E2723"),
        'text_secondary': get_color_from_hex("#795548"),
        'divider': get_color_from_hex("#D7CCC8"),
        'error': get_color_from_hex("#D32F2F"),
        'success': get_color_from_hex("#388E3C"),
        'warning': get_color_from_hex("#F57C00"),
    }
    
    _current_theme = 'Light'
    _theme_map = {
        'Light': LIGHT_THEME,
        'Dark': DARK_THEME,
        'Gold': GOLD_THEME,
    }
    
    @classmethod
    def get_theme(cls, theme_name='Light'):
        """Get theme colors by name"""
        return cls._theme_map.get(theme_name, cls.LIGHT_THEME)
    
    @classmethod
    def get_color(cls, color_key, theme_name='Light'):
        """Get specific color from theme"""
        theme = cls.get_theme(theme_name)
        return theme.get(color_key, (1, 1, 1, 1))
    
    @classmethod
    def set_current_theme(cls, theme_name):
        """Set current theme"""
        if theme_name in cls._theme_map:
            cls._current_theme = theme_name
            logger.info(f"Theme changed to: {theme_name}")
            return True
        return False
    
    @classmethod
    def get_current_theme(cls):
        """Get current theme name"""
        return cls._current_theme
    
    @classmethod
    def get_current_theme_colors(cls):
        """Get current theme colors"""
        return cls.get_theme(cls._current_theme)
    
    @classmethod
    def get_all_themes(cls):
        """Get list of available themes"""
        return list(cls._theme_map.keys())
    
    @classmethod
    def apply_theme(cls, app, theme_name):
        """Apply theme to KivyMD app"""
        try:
            if theme_name == 'Light':
                app.theme_cls.theme_style = "Light"
                app.theme_cls.primary_palette = "LightBlue"
                app.theme_cls.accent_palette = "Amber"
            elif theme_name == 'Dark':
                app.theme_cls.theme_style = "Dark"
                app.theme_cls.primary_palette = "Blue"
                app.theme_cls.accent_palette = "Amber"
            elif theme_name == 'Gold':
                app.theme_cls.theme_style = "Light"
                app.theme_cls.primary_palette = "Amber"
                app.theme_cls.accent_palette = "Blue"
            
            cls.set_current_theme(theme_name)
            logger.info(f"Theme applied: {theme_name}")
            return True
        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            return False


class ColorPalette:
    """Color palette utilities"""
    
    @staticmethod
    def get_gradient(color1, color2, steps=10):
        """Generate gradient between two colors"""
        gradient = []
        for i in range(steps):
            ratio = i / (steps - 1)
            r = color1[0] + (color2[0] - color1[0]) * ratio
            g = color1[1] + (color2[1] - color1[1]) * ratio
            b = color1[2] + (color2[2] - color1[2]) * ratio
            a = color1[3] + (color2[3] - color1[3]) * ratio if len(color1) > 3 else 1
            gradient.append((r, g, b, a))
        return gradient
    
    @staticmethod
    def lighten(color, amount=0.2):
        """Lighten a color"""
        return (
            min(1, color[0] + amount),
            min(1, color[1] + amount),
            min(1, color[2] + amount),
            color[3] if len(color) > 3 else 1
        )
    
    @staticmethod
    def darken(color, amount=0.2):
        """Darken a color"""
        return (
            max(0, color[0] - amount),
            max(0, color[1] - amount),
            max(0, color[2] - amount),
            color[3] if len(color) > 3 else 1
        )
    
    @staticmethod
    def to_hex(color):
        """Convert color tuple to hex string"""
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def from_hex(hex_color):
        """Convert hex string to color tuple"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b, 1)
