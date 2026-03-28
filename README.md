# inxs.live

Self-contained monorepo for the `inxs.live` landing page and its deployable tool stack.

## Repo structure

- `index.html` -> public homepage
- `invoice` -> browser-based invoice builder served at `/invoice`
- `mortgage` -> Canadian mortgage calculator served at `/mortgage`
- `apps/pdf-docs` -> PDF/DOCX converter
- `apps/video-converter` -> video conversion app
- `apps/video-downloader` -> media downloader
- `deploy` -> Caddy + Docker Compose for Portainer/Umbrel

## Live endpoints

- `https://inxs.live` served by Vercel
- `https://inxs.live/invoice`
- `https://inxs.live/mortgage`
- `https://pdf.inxs.live`
- `https://convert.inxs.live`
- `https://download.inxs.live`

## Deployment

Use [deploy/docker-compose.yml](/home/damato/Projects/INXS-Live/deploy/docker-compose.yml) as the Portainer stack file from this repo.

This repo is set up so Vercel serves the frontend, including `/invoice` and `/mortgage`, and Cloudflare Tunnel exposes only the backend tool subdomains, with no inbound `80` or `443` port mappings on the Umbrel host.
