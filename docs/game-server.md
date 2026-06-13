# Game Server Infrastructure

Discovered via `/proc/net/tcp` analysis from the running game on emulator and API probing.

## Network Map

| Service | Domain / IP | Purpose |
|---|---|---|
| Game API | `rising.89trillion.com` → `ingress.89tgame.com` → EC2 (us-west-2) | Game backend API. Returns HTTP 200 but requires auth tokens. |
| CDN | `server-*.cloudfront.net` IP range `52.85.25.x` | AWS CloudFront distribution serving game assets (portraits, configs, etc.) |
| Analytics | `1e100.net` (Google) | Firebase Analytics, Crashlytics |
| Google Services | `*.googleapis.com` | Firebase/Play Services |

## API

- `rising.89trillion.com` returns a Vue.js SPA (the official game website)
- The CNAME target `ingress.89tgame.com` (AWS EC2 us-west-2) returns 404 for all probed paths
- API probably uses a different protocol (gRPC, WebSockets) or path
- Direct requests return nothing — needs in-game session token

## CDN

- Serves from `https://file.89tgame.com/assets/298/Bundles/`
- AWS CloudFront distribution behind S3 (us-west-2)
- Returns HTTP 403 without proper authentication
- Bundle manifests list 860+ builtin, 2041+ battle, 21 seasonal, 155 DLC bundles
- CDN likely uses signed CloudFront URLs (not bearer tokens)

## Auth Token

Located at (pulled from game's app data on a running emulator):
```
/sdcard/Android/data/com.i89trillion.strategy.rising/files/UserInfo/UserInfo_Guest
```

JWT token format:
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
Payload:
```json
{
  "uid": 7841390,
  "iss": "gin-blog"
}
```

The token is issued per-installation. User ID increments per install.

## Bundle Manifests

Pulled from game's app data cache:
```
/sdcard/Android/data/com.i89trillion.strategy.rising/files/Bundles/
```

Key files:
- `versions.json` — CDN base URL + client version
- `builtin_v6_*.json` — 860 builtin asset bundles
- `battle_v1_*.json` — 2041 battle asset bundles
- `season_v5_*.json` — 21 seasonal bundles
- `dlc_v3_*.json` — 155 DLC bundles

Each bundle has: `id`, `name`, `size`, `hash`, `deps`, `isRaw`

Bundle download URL pattern: `https://file.89tgame.com/assets/298/Bundles/{bundle_name}`
