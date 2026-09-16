from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from PIL import Image
import os
from pathlib import Path

class CredentialPDFGeneratorBranded:
    """Generate professional credentials with event-specific branding images"""

    EVENT_BRANDING = {
        'Summer': {
            'header_image': 'SummerHeader.png',
            'footer_image': 'SummerFooter.png',
            'text_color': '#000000'
        },
        'Winter': {
            'header_image': 'WinterHeader.png',
            'footer_image': 'WinterFooter.png',
            'text_color': '#FFFFFF'
        },
        'Fall': {
            'header_image': 'FallHeader.png',
            'footer_image': 'FallFooter.png',
            'text_color': '#FFFFFF'
        },
        'Bowling': {
            'header_image': 'BowlingHeader.png',
            'footer_image': 'BowlingFooter.png',
            'text_color': '#FFFFFF'
        }
    }

    # Credential dimensions in inches (optimized to fit 4 per page)
    CRED_WIDTH = 3.85 * inch
    CRED_HEIGHT = 5.0 * inch
    HEADER_HEIGHT = 1.25 * inch
    FOOTER_HEIGHT = 0.75 * inch

    def __init__(self, event_name, event_type, sizing_preset='standard'):
        self.event_name = event_name
        self.event_type = event_type
        self.sizing_preset = sizing_preset
        self.branding = self.EVENT_BRANDING.get(event_type, self.EVENT_BRANDING['Summer'])

        # Define sizing presets
        self.sizing_presets = {
            'compact': {'margin': 0.10, 'spacing': 0.15},
            'standard': {'margin': 0.30, 'spacing': 0.20},
            'spacious': {'margin': 0.40, 'spacing': 0.30}
        }
        self.sizing = self.sizing_presets.get(sizing_preset, self.sizing_presets['standard'])

        # Get the path to branding images (relative to this file's directory)
        self.branding_dir = Path(__file__).parent / 'branding'
        self.header_image_path = self.branding_dir / self.branding['header_image']
        self.footer_image_path = self.branding_dir / self.branding['footer_image']

    def generate(self, dataframe, output_path):
        """Generate PDF with credentials from dataframe"""
        # Use letter size (8.5" x 11")
        page_width, page_height = letter

        # Margins and spacing (based on selected preset)
        margin = self.sizing['margin'] * inch
        spacing = self.sizing['spacing'] * inch

        # Calculate how many credentials fit per page (portrait)
        # Typically 2 per row
        creds_per_row = 2
        available_width = page_width - (2 * margin)
        cred_width_actual = (available_width - spacing) / creds_per_row

        # Calculate positions for 2-column layout
        positions = []
        current_y = page_height - margin - self.CRED_HEIGHT
        col = 0

        for row_num in range(10):  # Up to 10 rows per page
            if current_y < margin:
                break
            for col_num in range(creds_per_row):
                x = margin + col_num * (self.CRED_WIDTH + spacing)
                if x + self.CRED_WIDTH > page_width - margin:
                    continue
                positions.append((x, current_y))
            current_y -= (self.CRED_HEIGHT + spacing)

        # Create PDF
        c = canvas.Canvas(output_path, pagesize=letter)

        cred_index = 0
        for idx, row in dataframe.iterrows():
            if cred_index >= len(positions):
                # New page needed
                c.showPage()
                positions = []
                current_y = page_height - margin - self.CRED_HEIGHT

                for row_num in range(10):
                    if current_y < margin:
                        break
                    for col_num in range(creds_per_row):
                        x = margin + col_num * (self.CRED_WIDTH + spacing)
                        if x + self.CRED_WIDTH > page_width - margin:
                            continue
                        positions.append((x, current_y))
                    current_y -= (self.CRED_HEIGHT + spacing)

                cred_index = 0

            x, y = positions[cred_index]
            self._draw_credential(c, x, y, row)
            cred_index += 1

        c.save()

    def _get_best_font_size(self, c, text, max_width, start_size=22, min_size=10):
        """Find the best font size that fits the text within max_width"""
        # Start with smaller sizes to prevent overflow
        font_sizes = [22, 20, 18, 16, 14, 12, 10]

        for size in font_sizes:
            text_width = c.stringWidth(text, "Helvetica-Bold", size)
            if text_width <= max_width:
                return size

        # If even 10pt doesn't fit, return 10pt anyway
        return 10

    def _interpolate_color(self, color1, color2, progress):
        """Interpolate between two HexColor objects (progress: 0.0 to 1.0)"""
        # Extract RGB values from HexColor
        r1, g1, b1 = color1.red * 255, color1.green * 255, color1.blue * 255
        r2, g2, b2 = color2.red * 255, color2.green * 255, color2.blue * 255

        # Interpolate
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)

        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return HexColor(f'#{r:02x}{g:02x}{b:02x}')

    def _draw_gradient_rect(self, c, x, y, width, height, color1, color2, num_bands=1000):
        """Draw a rectangle with a smooth gradient from color1 (left) to color2 (right)"""
        band_width = width / num_bands

        for i in range(num_bands):
            # Calculate progress (0.0 at left to 1.0 at right)
            progress = i / (num_bands - 1) if num_bands > 1 else 0
            interpolated_color = self._interpolate_color(color1, color2, progress)

            # Draw this vertical band
            band_x = x + i * band_width
            c.setFillColor(interpolated_color)
            c.rect(band_x, y, band_width, height, fill=1, stroke=0)

    def _draw_credential(self, c, x, y, data_row):
        """Draw a single credential card with branded header and footer"""
        width = self.CRED_WIDTH
        height = self.CRED_HEIGHT
        header_height = self.HEADER_HEIGHT
        footer_height = self.FOOTER_HEIGHT
        content_height = height - header_height - footer_height

        # Draw content area background (light grey)
        content_y_top = y + height - header_height
        c.setFillColor(HexColor('#F5F5F5'))
        c.rect(x, content_y_top - content_height, width, content_height, fill=1, stroke=0)

        # Draw gradient header background with logo
        header_y_top = y + height - header_height
        header_y_bottom = y + height

        # Get gradient colors based on event type (top to bottom)
        gradient_colors = {
            'Summer': (HexColor('#ed2024'), HexColor('#ed2024')),  # Red
            'Winter': (HexColor('#4a7abd'), HexColor('#21409a')),  # Blue gradient
            'Fall': (HexColor('#fdc225'), HexColor('#f26522')),    # Orange gradient
            'Bowling': (HexColor('#9acc5c'), HexColor('#08753c'))  # Green gradient
        }

        color1, color2 = gradient_colors.get(self.event_type, gradient_colors['Summer'])

        # Draw gradient header background with smooth color transition
        self._draw_gradient_rect(c, x, header_y_top, width, header_height, color1, color2)

        # Draw logo on top of header background (centered)
        logo_path = self.branding_dir / 'Logo.png'
        try:
            if logo_path.exists():
                # Calculate size to fit within header (with padding)
                logo_height = header_height - 0.1 * inch
                logo_width = logo_height * 2.5  # Approximate aspect ratio
                logo_x = x + (width - logo_width) / 2
                logo_y = header_y_top + (header_height - logo_height) / 2

                c.drawImage(
                    str(logo_path),
                    logo_x, logo_y,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")

        # Draw footer with gradient background matching header colors
        footer_y_top = y + footer_height
        footer_y_bottom = y

        # Draw footer gradient background (same colors as header for consistency)
        self._draw_gradient_rect(c, x, footer_y_bottom, width, footer_height, color1, color2)

        # Draw footer image on top of the background color
        footer_image_map = {
            'Summer': 'SummerFooter.png',
            'Winter': 'WinterFooter.png',
            'Fall': 'FallFooter.png',
            'Bowling': 'BowlingFooter.png'
        }

        footer_filename = footer_image_map.get(self.event_type, 'SummerFooter.png')
        footer_path = self.branding_dir / footer_filename

        try:
            if footer_path.exists():
                c.drawImage(
                    str(footer_path),
                    x, footer_y_bottom,
                    width=width,
                    height=footer_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
        except Exception as e:
            print(f"Warning: Could not load footer image: {e}")

        # Draw content in the middle section
        content_y_bottom = y + footer_height

        # Extract data
        first_name = str(data_row.get('Name first', '')).upper()
        last_name = str(data_row.get('Name last/family', '')).upper()
        role = str(data_row.get('Role', '')).upper()
        sport = str(data_row.get('Sports', '')).upper()
        delegation = str(data_row.get('Delegation', '')).upper()
        event_name = str(self.event_name).upper()

        # EVENT NAME (centered at top of content area - dynamic font sizing)
        c.setFillColor(HexColor('#000000'))

        # Support 2-line event names using pipe character as separator
        # e.g., "2026 Summer|State Game" or auto-split long names
        event_lines = []

        if '|' in event_name:
            # Explicit split using pipe character
            event_lines = event_name.split('|')
        else:
            # Auto-split long names intelligently
            words = event_name.split()

            # If name is long enough, try to split it
            if len(event_name) > 25 and len(words) > 2:
                # Try splitting after the first part
                # For "2026 SPECIAL OLYMPICS EVENT", split after first 2-3 words
                mid_point = len(words) // 2
                line1 = ' '.join(words[:mid_point])
                line2 = ' '.join(words[mid_point:])
                event_lines = [line1, line2]
            else:
                event_lines = [event_name]

        # Define padding constants for consistent spacing
        side_padding = 0.18 * inch
        max_width = width - (2 * side_padding)

        # Track event name height for dynamic role box positioning
        event_name_bottom_y = content_y_top

        if len(event_lines) > 1:
            # Multi-line event name - find font size that fits the longest line
            longest_line = max(event_lines, key=len)
            best_size = self._get_best_font_size(c, longest_line, max_width)

            # Increased top margin to prevent overlap with header
            start_y = content_y_top - 0.35 * inch

            for i, line in enumerate(event_lines):
                line_y = start_y - (i * 0.28 * inch)
                c.setFont("Helvetica-Bold", best_size)
                event_name_width = c.stringWidth(line, "Helvetica-Bold", best_size)
                # Ensure text stays within container: use max(side_padding, centered position)
                event_x = max(x + side_padding, x + (width - event_name_width) / 2)
                # Also ensure right edge doesn't exceed container
                event_x = min(event_x, x + width - side_padding - event_name_width)
                c.drawString(event_x, line_y, line)

            # Calculate where event name ends for dynamic role box positioning
            # Use a fixed offset to position role box below event name
            last_line_y = start_y - ((len(event_lines) - 1) * 0.28 * inch)
            event_name_bottom_y = last_line_y - 0.55 * inch
        else:
            # Single line event name
            best_size = self._get_best_font_size(c, event_name, max_width)
            c.setFont("Helvetica-Bold", best_size)
            event_name_width = c.stringWidth(event_name, "Helvetica-Bold", best_size)
            # Ensure text stays within container: use max(side_padding, centered position)
            event_x = max(x + side_padding, x + (width - event_name_width) / 2)
            # Also ensure right edge doesn't exceed container
            event_x = min(event_x, x + width - side_padding - event_name_width)
            # Increased top margin to prevent overlap with header
            event_name_y = content_y_top - 0.40 * inch
            c.drawString(event_x, event_name_y, event_name)

            # Calculate where event name ends for dynamic role box positioning
            # Use a fixed offset to position role box below event name
            event_name_bottom_y = event_name_y - 0.55 * inch

        # ROLE - Grey background box with white text on the RIGHT side (dynamic positioning)
        role_box_width = 1.55 * inch
        role_box_height = 0.38 * inch
        role_box_x = x + width - role_box_width - side_padding  # Right-aligned with consistent padding
        role_box_y = event_name_bottom_y  # Position directly below event name

        # Grey background box
        c.setFillColor(HexColor('#808080'))
        c.rect(role_box_x, role_box_y, role_box_width, role_box_height, fill=1, stroke=0)

        # White text for role (13pt bold, centered in box)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(HexColor('#FFFFFF'))
        c.drawString(role_box_x + 0.08 * inch, role_box_y + 0.08 * inch, role)

        # Calculate available width for names and details (accounting for both side margins)
        name_available_width = width - (2 * side_padding)
        name_x = x + side_padding

        # Position names below role box with proper spacing
        # Role box bottom is at role_box_y, so position first name below it
        first_name_y = role_box_y - 0.42 * inch  # 0.42" below role box

        # FIRST NAME (auto-sizing, start at 26pt, bold)
        c.setFillColor(HexColor('#000000'))
        # Try sizes: 26, 24, 22, 20, 18, 16, 14, 12, 10
        name_sizes = [26, 24, 22, 20, 18, 16, 14, 12, 10]
        first_name_size = 10
        for size in name_sizes:
            text_width = c.stringWidth(first_name, "Helvetica-Bold", size)
            if text_width <= name_available_width:
                first_name_size = size
                break
        c.setFont("Helvetica-Bold", first_name_size)
        c.drawString(name_x, first_name_y, first_name)

        # LAST NAME (auto-sizing, start at 26pt, bold) - positioned below first name
        last_name_y = first_name_y - 0.45 * inch  # 0.45" below first name
        last_name_size = 10
        for size in name_sizes:
            text_width = c.stringWidth(last_name, "Helvetica-Bold", size)
            if text_width <= name_available_width:
                last_name_size = size
                break
        c.setFont("Helvetica-Bold", last_name_size)
        c.drawString(name_x, last_name_y, last_name)

        # SPORT (auto-sizing, start at 14pt) - positioned below last name (closer)
        sport_text = f"Sport: {sport}"
        sport_y = last_name_y - 0.35 * inch  # 0.35" below last name (reduced from 0.70)
        detail_sizes = [14, 12, 11, 10, 9, 8]
        sport_size = 8
        for size in detail_sizes:
            text_width = c.stringWidth(sport_text, "Helvetica", size)
            if text_width <= name_available_width:
                sport_size = size
                break
        c.setFont("Helvetica", sport_size)
        c.setFillColor(HexColor('#000000'))
        c.drawString(name_x, sport_y, sport_text)

        # DELEGATION/REGION (auto-sizing, start at 14pt) - positioned below sport (closer)
        delegation_text = f"Region: {delegation}"
        delegation_y = sport_y - 0.25 * inch  # 0.25" below sport (reduced from 0.35)
        delegation_size = 8
        for size in detail_sizes:
            text_width = c.stringWidth(delegation_text, "Helvetica", size)
            if text_width <= name_available_width:
                delegation_size = size
                break
        c.setFont("Helvetica", delegation_size)
        c.drawString(name_x, delegation_y, delegation_text)
