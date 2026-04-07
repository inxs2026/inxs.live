"""
pp_colors.py — Official North American Post Position Colors
Standard used by racetracks (Gulfstream, etc.)
Import this in ALL picks PDF scripts instead of hardcoding.

Usage:
    from scripts.pp_colors import PP_COLORS, PP_TEXT, pp_styles
"""
try:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    PP_COLORS = {
        1:  colors.HexColor('#E8383D'),  # Red
        2:  colors.white,                 # White
        3:  colors.HexColor('#1B75BC'),  # Blue
        4:  colors.HexColor('#F5E642'),  # Yellow
        5:  colors.HexColor('#3CB44B'),  # Green
        6:  colors.HexColor('#000000'),  # Black
        7:  colors.HexColor('#FF8800'),  # Orange
        8:  colors.HexColor('#FF69B4'),  # Pink
        9:  colors.HexColor('#21B7B7'),  # Teal
        10: colors.HexColor('#6B2D8C'),  # Purple
        11: colors.HexColor('#808080'),  # Gray
        12: colors.HexColor('#66CC00'),  # Lime Green
    }

    PP_TEXT = {
        1:  colors.white,                # white on red
        2:  colors.black,                # black on white
        3:  colors.white,                # white on blue
        4:  colors.black,                # black on yellow
        5:  colors.white,                # white on green
        6:  colors.HexColor('#F5E642'),  # yellow on black
        7:  colors.black,                # black on orange
        8:  colors.black,                # black on pink
        9:  colors.white,                # white on teal
        10: colors.white,                # white on purple
        11: colors.white,                # white on gray
        12: colors.black,                # black on lime green
    }

    def pp_badge_style(pp):
        """Return (bg_color, text_color) for a given post position."""
        bg = PP_COLORS.get(pp, colors.gray)
        fg = PP_TEXT.get(pp, colors.white)
        return bg, fg

    def pp_text_hex(pp):
        """Return text colour as hex string for ReportLab font tags."""
        fg = PP_TEXT.get(pp, colors.white)
        if fg == colors.black:
            return '#000000'
        elif fg == colors.white:
            return '#ffffff'
        elif hasattr(fg, 'hexval'):
            hex_val = fg.hexval()
            # hexval() returns '0xf5e642' format, convert to '#f5e642'
            if hex_val.startswith('0x'):
                hex_val = '#' + hex_val[2:]
            return hex_val
        else:
            return '#ffffff'

    def pp_border_color(pp):
        """Return a border color for badges that need contrast (white/yellow bg)."""
        bg = PP_COLORS.get(pp, colors.gray)
        if bg in [colors.white, colors.HexColor('#F5E642')]:
            return colors.HexColor('#888888')
        return bg

except ImportError:
    pass  # reportlab not available in this context

# Human-readable reference (always available)
PP_REFERENCE = {
    1:  {"bg": "Red",       "text": "White"},
    2:  {"bg": "White",     "text": "Black"},
    3:  {"bg": "Blue",      "text": "White"},
    4:  {"bg": "Yellow",    "text": "Black"},
    5:  {"bg": "Green",     "text": "White"},
    6:  {"bg": "Black",     "text": "Yellow"},
    7:  {"bg": "Orange",    "text": "Black"},
    8:  {"bg": "Pink",      "text": "Black"},
    9:  {"bg": "Teal",      "text": "White"},
    10: {"bg": "Purple",    "text": "White"},
    11: {"bg": "Gray",      "text": "White"},
    12: {"bg": "Lime Green","text": "Black"},
}

if __name__ == "__main__":
    print("Post Position Color Reference:")
    print("-" * 40)
    for pp, ref in PP_REFERENCE.items():
        print(f"  #{pp:2d}  bg={ref['bg']:<12} text={ref['text']}")
