# INXS Umbrel Stack

This stack keeps the `INXS-Live` site and the three tool backends running 24/7 behind a Cloudflare Tunnel.

## What it serves

- `https://inxs.live` -> static landing page from the repo root
- `https://pdf.inxs.live` -> PDF/DOCX converter
- `https://convert.inxs.live` -> video converter
- `https://download.inxs.live` -> video downloader

## Repo layout

- `index.html` -> public landing page
- `apps/pdf-docs` -> PDF/DOCX service
- `apps/video-converter` -> FFmpeg conversion service
- `apps/video-downloader` -> yt-dlp download service
- `deploy` -> Caddy, Cloudflare Tunnel, and Docker Compose stack

## Cloudflare Tunnel

This deployment does not require opening inbound ports on the Umbrel Pi.

1. In Cloudflare Zero Trust, create a remotely-managed tunnel.
2. Copy the tunnel token.
3. In the tunnel's Public hostnames settings, add:
   - `inxs.live` -> `http://caddy:80`
   - `www.inxs.live` -> `http://caddy:80`
   - `pdf.inxs.live` -> `http://pdf-docs:8000`
   - `convert.inxs.live` -> `http://video-converter:3000`
   - `download.inxs.live` -> `http://video-downloader:4000`
4. Add `CLOUDFLARE_TUNNEL_TOKEN=<your tunnel token>` to the stack environment in Portainer.

Cloudflare will handle the DNS and edge routing for those hostnames automatically through the tunnel.

## Portainer deployment

1. Push this `INXS-Live` repo to GitHub.
2. In Portainer, create a new stack.
3. Use the repository's `deploy/docker-compose.yml`.
4. Deploy the stack.
5. Set the stack environment variable `CLOUDFLARE_TUNNEL_TOKEN`.
6. Deploy the stack.

## Updates

When you change the site or apps, push to GitHub and redeploy or pull/recreate the stack in Portainer.

## Persistence

Docker named volumes keep output files across restarts:

- `video_converter_downloads`
- `video_converter_uploads`
- `video_downloader_downloads`

## Notes

- The video tools depend on `ffmpeg`.
- The PDF tool depends on LibreOffice for DOCX -> PDF.
- The downloader's desktop-only "Open Downloads Folder" button is disabled in the server deployment.
- `cloudflared` only makes outbound connections, so no router port forwarding is required.
