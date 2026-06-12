#!/usr/bin/env python3
"""
Download War Inc: Rising hero portraits from all known sources.

Sources:
  1. warincrising.com characters page (21 mythic heroes)
  2. Individual hero guide pages on warincrising.com
  3. APKPure for APK downloads (version check)
  4. Fallback: placeholder generation

Usage:
  python3 scripts/download_portraits.py --out public/images/heroes
  python3 scripts/download_portraits.py --check-version
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Known image sources ──────────────────────────────────────────────────

OFFICIAL_SITE = 'https://www.warincrising.com'
CHARACTERS_PAGE = f'{OFFICIAL_SITE}/characters/'

# Mythic portraits scraped from characters page
MYTHIC_PORTRAITS = {
    637: ('mythic1', 'Gryphon Knight'),
    638: ('mythic2', 'Geomancer'),
    704: ('mythic3', 'Storm Maiden'),
    706: ('mythic4', 'Starlight Apostle'),
    739: ('mythic5', 'Fury Cannoneer'),
    744: ('mythic6', 'Flame Duelist'),
    749: ('mythic7', 'The Knight King'),
    846: ('mythic8', 'Blazeking'),
    845: ('mythic9', 'Tide Lord'),
    703: ('mythic10', 'Frost Queen'),
    708: ('mythic11', 'Darkmoon Queen'),
    734: ('mythic12', 'Nine-Tailed Fox'),
    762: ('mythic13', 'Radiant Warrior'),
    711: ('mythic14', 'Bone Marksman'),
    735: ('mythic15', 'Woodland Guardian'),
    847: ('mythic17', 'Red Blade'),
    736: ('mythic18', 'Melody Weaver'),
    738: ('mythic19', 'Ripple Wizard'),
    740: ('mythic20', 'Firepower Vanguard'),
    742: ('mythic21', 'Jungle Ranger'),
    743: ('mythic22', 'Barbarian Tyrant'),
}

# Official site guide pages that may have character portraits
GUIDE_SLUGS = [
    'barbarian-tyrant', 'frost-queen', 'melody-weaver',
    'mist-archer-2', 'nine-tailed-fox', 'radiant-warrior',
    'ripple-wizard', 'the-knight-king', 'tide-lord',
    'woodland-guardian',
]


def download_image(url: str, dst: str, retries: int = 3) -> bool:
    """Download an image from URL to local path. Returns True on success."""
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        return True  # Already have it
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; WarIncWiki/1.0)',
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as f:
                    f.write(resp.read())
            print(f'  ✓ {url.split("/")[-1]} -> {dst} ({os.path.getsize(dst)//1024}KB)')
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                print(f'  ✗ {url.split("/")[-1]}: {e}')
    return False


def download_mythic_portraits(out_dir: str):
    """Download the 21 mythic portraits from warincrising.com."""
    base = f'{OFFICIAL_SITE}/wp-content/uploads/2026/04'
    count = 0
    for uid, (img_id, name) in MYTHIC_PORTRAITS.items():
        url = f'{base}/{img_id}.png'
        dst = os.path.join(out_dir, f'{uid}.png')
        if download_image(url, dst):
            count += 1
    print(f'\nDownloaded {count}/{len(MYTHIC_PORTRAITS)} mythic portraits')
    return count


def scrape_characters_page() -> dict:
    """Scrape the characters page for any new images."""
    try:
        req = urllib.request.Request(CHARACTERS_PAGE, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; WarIncWiki/1.0)',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        # Extract image URL + hero name pairs
        images = {}
        # Find mythic blocks: image src + following h5 heading
        blocks = re.findall(
            r'mythic(\d+).*?<h5[^>]*>(?:<a[^>]*>)?([^<]+)(?:</a>)?</h5>',
            html, re.DOTALL
        )
        for img_num, name in blocks:
            url = f'{OFFICIAL_SITE}/wp-content/uploads/2026/04/mythic{img_num}.png'
            images[name.strip()] = url
        
        return images
    except Exception as e:
        print(f'Error scraping characters page: {e}')
        return {}


def check_apk_version() -> str:
    """Check latest APK version from APKPure."""
    try:
        req = urllib.request.Request(
            'https://www.apkpure.com/war-inc-rising/com.i89trillion.strategy.rising/versions',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        
        # Find version numbers
        versions = re.findall(r'(\d+\.\d+\.\d+)', html)
        if versions:
            # Remove duplicates while preserving order
            seen = set()
            unique = []
            for v in versions:
                if v not in seen:
                    seen.add(v)
                    unique.append(v)
            return unique[0] if unique else '1.0.7'
    except Exception as e:
        print(f'Error checking APK version: {e}')
    return '1.0.7'


def generate_placeholder(out_dir: str, uid: int, name: str, size: int = 512):
    """Generate a placeholder silhouette for heroes without portraits."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGBA', (size, size), (30, 30, 40, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple character silhouette
        # Body
        draw.ellipse([size//2 - 60, size//2 - 100, size//2 + 60, size//2 + 20], 
                     fill=(60, 60, 80, 255))
        # Head
        draw.ellipse([size//2 - 35, size//2 - 160, size//2 + 35, size//2 - 90], 
                     fill=(60, 60, 80, 255))
        
        # Draw initials
        initials = ''.join(w[0].upper() for w in name.split()[:2])
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttf', 60)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), initials, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((size - tw)//2, (size - th)//2 - 20), initials, 
                  fill=(120, 120, 160, 255), font=font)
        
        dst = os.path.join(out_dir, f'{uid}.png')
        img.save(dst)
        print(f'  ◌ Generated placeholder for {name} -> {dst}')
        return True
    except ImportError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Download hero portraits')
    parser.add_argument('--out', default='public/images/heroes',
                        help='Output directory')
    parser.add_argument('--check-version', action='store_true',
                        help='Check latest APK version')
    parser.add_argument('--scrape', action='store_true',
                        help='Scrape characters page for new content')
    parser.add_argument('--placeholder', action='store_true',
                        help='Generate placeholders for missing heroes')
    
    args = parser.parse_args()
    
    if args.check_version:
        version = check_apk_version()
        print(f'Latest APK version: {version}')
        return
    
    if args.scrape:
        images = scrape_characters_page()
        print(f'Found {len(images)} character images on official site:')
        for name, url in images.items():
            print(f'  {name}: {url}')
        return
    
    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    
    print('Downloading mythic portraits from warincrising.com...')
    download_mythic_portraits(out_dir)
    
    if args.placeholder:
        print('\nGenerating placeholders for missing heroes...')
        # Load all hero IDs
        growth = json.load(open('data/processed/config/card_growth.json'))
        name_map = json.load(open('data/processed/unit_name_map.json'))
        
        existing = {int(f.replace('.png', '')) for f in os.listdir(out_dir) 
                    if f.endswith('.png') and f.replace('.png', '').isdigit()}
        
        count = 0
        for uid_str in growth['battleUnits']:
            uid = int(uid_str)
            if uid in existing:
                continue
            name = name_map.get(uid_str, f'Unit {uid}')
            if generate_placeholder(out_dir, uid, name):
                count += 1
        
        print(f'Generated {count} placeholders')


if __name__ == '__main__':
    main()
