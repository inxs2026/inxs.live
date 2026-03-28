# INXS Umbrel Stack

This stack keeps the three backend tools running 24/7 behind a Cloudflare Tunnel while `inxs.live` stays on Vercel.

## What it serves

- `https://pdf.inxs.live` -> PDF/DOCX converter
- `https://convert.inxs.live` -> video converter
- `https://download.inxs.live` -> video downloader
- `https://inxs.live/invoice` -> static invoice builder on Vercel
- `https://inxs.live` remains hosted by Vercel

## Repo layout

- `index.html` -> public landing page for Vercel
- `invoice` -> static invoice builder served by Vercel
- `apps/pdf-docs` -> PDF/DOCX service
- `apps/video-converter` -> FFmpeg conversion service
- `apps/video-downloader` -> yt-dlp download service
- `deploy` -> Cloudflare Tunnel and Docker Compose stack

## Cloudflare Tunnel

This deployment does not require opening inbound ports on the Umbrel Pi.

The invoice builder does not need a backend container. It runs entirely in the browser and should be deployed with the main Vercel site, not through Portainer.

1. In Cloudflare Zero Trust, create a remotely-managed tunnel.
2. Copy the tunnel token.
3. In the tunnel's Public hostnames settings, add:
   - `pdf.inxs.live` -> `http://<UMBREL_LAN_IP>:18000`
   - `convert.inxs.live` -> `http://<UMBREL_LAN_IP>:13000`
   - `download.inxs.live` -> `http://<UMBREL_LAN_IP>:14000`
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
- Keep the existing DNS/Vercel setup for `inxs.live` and `www.inxs.live`.
- The backend ports use high host ports only for the local tunnel origin, not for public Internet exposure.
