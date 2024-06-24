import requests
from bs4 import BeautifulSoup
import cssutils
import re
from collections import Counter
from urllib.parse import urljoin

def rgb_to_hex(rgb):
    if rgb.startswith('rgb'):
        nums = rgb[rgb.index('(') + 1:rgb.index(')')].split(',')
        try:
            return '#{:02x}{:02x}{:02x}'.format(int(nums[0]), int(nums[1]), int(nums[2]))
        except ValueError:
            return None 
    return rgb

def clean_css_url(base_url, css_url):
    return urljoin(base_url, css_url) if not css_url.startswith(('http://', 'https://')) else css_url

def get_logo_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
        if icon_link and icon_link.get('href'):
            logo_url = urljoin(url, icon_link['href'])
            return logo_url
        img = soup.find('img', alt=lambda x: x and 'logo' in x.lower())
        if img and img.get('src'):
            logo_url = urljoin(url, img['src'])
            return logo_url
        return None
    except requests.RequestException:
        return None

def get_primary_colors(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        css_styles = ''
        for style in soup.find_all('style'):
            css_styles += style.string or ''
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_url = clean_css_url(url, href)
                try:
                    css_response = requests.get(css_url)
                    css_response.raise_for_status()
                    css_styles += css_response.text
                except requests.RequestException:
                    pass
        css_parser = cssutils.CSSParser()
        css_sheet = css_parser.parseString(css_styles)
        color_pattern = re.compile(r'(#(?:[0-9a-fA-F]{3}){1,2}|rgb\(.*?\))')
        colors = []
        for rule in css_sheet:
            if rule.type == rule.STYLE_RULE:
                for property in rule.style:
                    if 'color' in property.name or 'background-color' in property.name:
                        match = color_pattern.search(property.value)
                        if match:
                            colors.append(rgb_to_hex(match.group(0)))
        color_counter = Counter(colors)
        primary_colors = color_counter.most_common(7) 
        return primary_colors
    except requests.RequestException:
        return []

def get_button_colors(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        css_styles = ''
        for style in soup.find_all('style'):
            css_styles += style.string or ''
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                css_url = clean_css_url(url, href)
                try:
                    css_response = requests.get(css_url)
                    css_response.raise_for_status()
                    css_styles += css_response.text
                except requests.RequestException:
                    pass
        css_parser = cssutils.CSSParser()
        css_sheet = css_parser.parseString(css_styles)
        button_colors = set()
        buttons = soup.find_all('button')

        for button in buttons:
            style = button.get('style')
            if style:
                style_dict = dict(item.split(":") for item in style.split(";") if item)
                if 'background-color' in style_dict:
                    button_colors.add(rgb_to_hex(style_dict['background-color'].strip()))
                elif 'color' in style_dict:
                    button_colors.add(rgb_to_hex(style_dict['color'].strip()))

        for rule in css_sheet:
            if rule.type == rule.STYLE_RULE and 'button' in rule.selectorText:
                for property in rule.style:
                    if 'background-color' in property.name or 'color' in property.name:
                        match = re.search(r'(#(?:[0-9a-fA-F]{3}){1,2}|rgb\(.*?\))', property.value)
                        if match:
                            button_colors.add(rgb_to_hex(match.group(0)))
        button_colors = list(button_colors)[:5]
        return list(button_colors)
    except requests.RequestException:
        return []
