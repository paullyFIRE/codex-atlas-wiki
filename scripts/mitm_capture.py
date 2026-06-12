#!/usr/bin/env python3
"""
MITM proxy capture + analysis for War Inc: Rising.

Captures traffic from the Android emulator through mitmproxy,
then extracts API endpoints, CDN URLs, image URLs, and structured data.

Usage:
  # Start mitmproxy first:
  mitmweb --listen-port 8080 --web-port 8081

  # Set emulator proxy:
  adb shell settings put global http_proxy <host_ip>:8080

  # Then run this to capture and analyze:
  python3 scripts/mitm_capture.py --duration 300 --out data/raw/mitm_capture

  # Or just analyze existing dump:
  python3 scripts/mitm_capture.py --analyze data/raw/mitm_capture/flows.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
import re
from datetime import datetime
from pathlib import Path

# Game-specific patterns
GAME_DOMAINS = [
    '89trillion.com',
    'rising',  # subdomain match
    'fastone',  # developer
]
CDN_PATTERNS = [
    r'cdn.*\.89trillion\.',
    r'\.cloudfront\.net',
    r'\.akamai',
]
IMAGE_EXTS = ('.png', '.jpg', '.jpeg', '.webp')
API_PATTERNS = [
    r'/api/',
    r'/v\d+/',
    r'/graphql',
    r'/config',
    r'/hero',
    r'/unit',
    r'/data',
    r'/asset',
]


def capture_mitmproxy(duration: int, out_dir: str):
    """Capture live traffic from mitmproxy and dump to file."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    flows_file = out_path / 'flows.json'

    # Check mitmproxy is running
    result = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8081/'],
        capture_output=True, text=True
    )
    if result.stdout != '200':
        print('ERROR: mitmweb not running at http://localhost:8081')
        print('Start it with: mitmweb --listen-port 8080 --web-port 8081')
        return False

    # Use mitmproxy's flow export via its API
    # mitmweb has a REST API at localhost:8081
    print(f'Capturing traffic for {duration} seconds...')
    print(f'Go play War Inc: Rising on the emulator now!')
    
    # Poll for flows periodically
    all_flows = []
    start = time.time()
    last_count = 0
    
    while time.time() - start < duration:
        time.sleep(5)
        try:
            resp = subprocess.run(
                ['curl', '-s', 'http://localhost:8081/flows'],
                capture_output=True, text=True, timeout=5
            )
            if resp.stdout:
                flows = json.loads(resp.stdout)
                if len(flows) > last_count:
                    new = len(flows) - last_count
                    print(f'  Captured {len(flows)} flows (+{new})', end='\r')
                    last_count = len(flows)
                    all_flows = flows
        except:
            pass
    
    print(f'\nCapture complete: {len(all_flows)} total flows')
    
    # Save all flows
    with open(flows_file, 'w') as f:
        json.dump(all_flows, f, indent=2)
    
    # Also save a summary
    summary = analyze_flows(all_flows)
    with open(out_path / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f'\nSaved to {out_dir}/')
    print_summary(summary)
    return True


def analyze_flows_file(path: str):
    """Analyze an existing mitmproxy dump."""
    with open(path) as f:
        flows = json.load(f)
    summary = analyze_flows(flows)
    print_summary(summary)
    
    out_dir = os.path.dirname(path)
    with open(os.path.join(out_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    return summary


def analyze_flows(flows):
    """Extract game-relevant information from flows."""
    domains = set()
    image_urls = []
    api_endpoints = []
    game_flows = []
    
    for flow in flows:
        req = flow.get('request', {})
        url = req.get('url', '')
        host = req.get('host', '')
        method = req.get('method', '')
        path = req.get('path', '')
        
        # Collect all domains
        domains.add(host)
        
        # Check if it's game-related
        is_game = any(d in host for d in GAME_DOMAINS)
        is_cdn = any(re.search(p, host) for p in CDN_PATTERNS)
        is_image = any(url.lower().endswith(ext) for ext in IMAGE_EXTS)
        is_api = any(p in path for p in API_PATTERNS)
        
        if is_game or is_cdn or is_image or is_api:
            entry = {
                'url': url,
                'method': method,
                'host': host,
                'path': path,
                'type': ('image' if is_image else 'api' if is_api else 'cdn' if is_cdn else 'game'),
                'status': flow.get('response', {}).get('status_code', '?'),
                'response_size': flow.get('response', {}).get('content_length', 0),
            }
            game_flows.append(entry)
            
            if is_image:
                image_urls.append(url)
            if is_api:
                api_endpoints.append(path)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_flows': len(flows),
        'game_related': len(game_flows),
        'unique_domains': sorted(domains),
        'game_domains': sorted(set(
            f['host'] for f in game_flows
        )),
        'image_urls': image_urls,
        'api_endpoints': sorted(set(api_endpoints)),
        'cdn_urls': sorted(set(
            f['url'] for f in game_flows if f['type'] == 'cdn'
        )),
        'game_flows': game_flows,
    }


def print_summary(summary):
    """Pretty-print the analysis summary."""
    print('\n' + '=' * 60)
    print(f'MITM CAPTURE SUMMARY')
    print(f'Timestamp: {summary["timestamp"]}')
    print(f'Total flows: {summary["total_flows"]}')
    print(f'Game-related: {summary["game_related"]}')
    print('=' * 60)
    
    print(f'\n📡 Unique Domains Encountered ({len(summary["unique_domains"])}):')
    for d in summary['unique_domains']:
        marker = '🎮' if any(g in d for g in GAME_DOMAINS) else '  '
        print(f'  {marker} {d}')
    
    if summary['image_urls']:
        print(f'\n🖼️  Image URLs Found ({len(summary["image_urls"])}):')
        for url in summary['image_urls'][:20]:
            print(f'  {url}')
        if len(summary['image_urls']) > 20:
            print(f'  ... and {len(summary["image_urls"]) - 20} more')
    
    if summary['image_urls']:
        # Group by host to find CDNs
        from collections import Counter
        hosts = Counter(url.split('/')[2] for url in summary['image_urls'])
        print(f'\n📦 Image Hosts:')
        for host, count in hosts.most_common():
            print(f'  {host}: {count} images')
    
    if summary['api_endpoints']:
        print(f'\n🔌 API Endpoints:')
        for ep in summary['api_endpoints'][:20]:
            print(f'  {ep}')
    
    if summary['game_domains']:
        print(f'\n🎯 Game-Specific Domains:')
        for d in summary['game_domains']:
            print(f'  {d}')
    
    print()


def main():
    parser = argparse.ArgumentParser(description='MITM capture for War Inc: Rising')
    parser.add_argument('--duration', type=int, default=300,
                        help='Capture duration in seconds (default: 300)')
    parser.add_argument('--out', type=str, default='data/raw/mitm_capture',
                        help='Output directory')
    parser.add_argument('--analyze', type=str, default=None,
                        help='Analyze existing flow dump instead of capturing')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_flows_file(args.analyze)
    else:
        capture_mitmproxy(args.duration, args.out)


if __name__ == '__main__':
    main()
