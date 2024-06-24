from flask import Flask, render_template, request
from scraper import get_logo_url, get_primary_colors, get_button_colors
import colorsys

app = Flask(__name__)

def is_shade_of_white_or_black(hex_color):
    if not hex_color or len(hex_color) != 7 or not hex_color.startswith('#'):
        return False  
    color = hex_color.lstrip('#')
    try:
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        if (r > 200 and g > 200 and b > 200) or (r < 55 and g < 55 and b < 55):
            return True
    except ValueError:
        return False 
    return False

def get_complementary_color(hex_color):
    if not hex_color or len(hex_color) != 7 or not hex_color.startswith('#'):
        return '#000000'  
    color = hex_color.lstrip('#')
    try:
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)
        comp_h = (h + 0.5) % 1.0 
        comp_r, comp_g, comp_b = colorsys.hls_to_rgb(comp_h, l, s)
        return '#{:02x}{:02x}{:02x}'.format(int(comp_r * 255), int(comp_g * 255), int(comp_b * 255))
    except ValueError:
        return '#000000' 

@app.route('/', methods=['GET', 'POST'])
def index():
    logo_url = None
    primary_colors = []
    button_colors = []
    recommended_colors = []
    
    if request.method == 'POST':
        website_url = request.form['website_url']
        logo_url = get_logo_url(website_url)
        primary_colors = get_primary_colors(website_url)
        button_colors = get_button_colors(website_url)
        
        
        all_colors = primary_colors + [(color, 1) for color in button_colors]
        for color, _ in all_colors:
            if not is_shade_of_white_or_black(color):
                comp_color = get_complementary_color(color)
                recommended_colors.append((color, comp_color))
    
    return render_template('index.html', logo_url=logo_url, primary_colors=primary_colors, button_colors=button_colors, recommended_colors=recommended_colors)

if __name__ == '__main__':
    app.run(debug=True)
