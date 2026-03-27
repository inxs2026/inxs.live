# inxs.live

Self-contained monorepo for the `inxs.live` landing page and its deployable tool stack.

## Repo structure

- `index.html` -> public homepage
- `apps/pdf-docs` -> PDF/DOCX converter
- `apps/video-converter` -> video conversion app
- `apps/video-downloader` -> media downloader
- `deploy` -> Caddy + Docker Compose for Portainer/Umbrel

## Live endpoints

- `https://inxs.live`
- `https://pdf.inxs.live`
- `https://convert.inxs.live`
- `https://download.inxs.live`

## Deployment

Use [deploy/docker-compose.yml](/home/damato/Projects/INXS-Live/deploy/docker-compose.yml) as the Portainer stack file from this repo.

This repo is set up to work with Cloudflare Tunnel, so the Umbrel host does not need inbound `80` or `443` port mappings.
