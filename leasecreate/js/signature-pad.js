// Feature 3: Digital Signature Pad
// Canvas-based signature capture for landlord and tenant

export class SignaturePad {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.drawing = false;
    this.paths = [];
    this.currentPath = [];

    this.resize();
    this.setupEvents();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = 120 * dpr;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = '120px';
    this.ctx.scale(dpr, dpr);
    this.ctx.strokeStyle = '#1a1a1a';
    this.ctx.lineWidth = 2;
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';
    this.redraw();
  }

  setupEvents() {
    const getPos = (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const touch = e.touches ? e.touches[0] : e;
      return { x: touch.clientX - rect.left, y: touch.clientY - rect.top };
    };

    const start = (e) => {
      e.preventDefault();
      this.drawing = true;
      this.currentPath = [getPos(e)];
    };

    const move = (e) => {
      if (!this.drawing) return;
      e.preventDefault();
      const pos = getPos(e);
      this.currentPath.push(pos);
      this.redraw();
      // Draw current stroke
      if (this.currentPath.length > 1) {
        this.ctx.beginPath();
        const prev = this.currentPath[this.currentPath.length - 2];
        this.ctx.moveTo(prev.x, prev.y);
        this.ctx.lineTo(pos.x, pos.y);
        this.ctx.stroke();
      }
    };

    const end = () => {
      if (this.drawing && this.currentPath.length > 1) {
        this.paths.push([...this.currentPath]);
      }
      this.drawing = false;
      this.currentPath = [];
    };

    this.canvas.addEventListener('mousedown', start);
    this.canvas.addEventListener('mousemove', move);
    this.canvas.addEventListener('mouseup', end);
    this.canvas.addEventListener('mouseleave', end);
    this.canvas.addEventListener('touchstart', start, { passive: false });
    this.canvas.addEventListener('touchmove', move, { passive: false });
    this.canvas.addEventListener('touchend', end);

    window.addEventListener('resize', () => this.resize());
  }

  redraw() {
    const dpr = window.devicePixelRatio || 1;
    this.ctx.clearRect(0, 0, this.canvas.width / dpr, this.canvas.height / dpr);

    // Draw baseline
    const h = this.canvas.height / dpr;
    this.ctx.save();
    this.ctx.strokeStyle = '#ddd';
    this.ctx.lineWidth = 1;
    this.ctx.setLineDash([4, 4]);
    this.ctx.beginPath();
    this.ctx.moveTo(10, h - 20);
    this.ctx.lineTo(this.canvas.width / dpr - 10, h - 20);
    this.ctx.stroke();
    this.ctx.restore();

    // Draw paths
    this.ctx.strokeStyle = '#1a1a1a';
    this.ctx.lineWidth = 2;
    this.ctx.setLineDash([]);
    for (const path of this.paths) {
      if (path.length < 2) continue;
      this.ctx.beginPath();
      this.ctx.moveTo(path[0].x, path[0].y);
      for (let i = 1; i < path.length; i++) {
        this.ctx.lineTo(path[i].x, path[i].y);
      }
      this.ctx.stroke();
    }
  }

  clear() {
    this.paths = [];
    this.currentPath = [];
    this.redraw();
  }

  isEmpty() {
    return this.paths.length === 0;
  }

  toDataURL() {
    return this.canvas.toDataURL('image/png');
  }

  toSVG() {
    const dpr = window.devicePixelRatio || 1;
    const w = this.canvas.width / dpr;
    const h = this.canvas.height / dpr;
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`;
    for (const path of this.paths) {
      if (path.length < 2) continue;
      svg += `<path d="M${path[0].x},${path[0].y}`;
      for (let i = 1; i < path.length; i++) {
        svg += ` L${path[i].x},${path[i].y}`;
      }
      svg += `" fill="none" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>`;
    }
    svg += '</svg>';
    return svg;
  }
}

export function createSignatureSection() {
  return `
    <div class="signature-section">
      <div class="signature-section-body print-page-group">
        <h3>Digital Signatures</h3>
        <p class="sig-instructions">Sign below using your mouse or touchscreen. Signatures will be embedded in the exported PDF.</p>
        <div class="sig-pads print-page-group">
          <div class="sig-pad-group">
            <label>Landlord Signature</label>
            <div class="sig-pad-wrapper">
              <canvas id="sig-landlord" class="sig-canvas"></canvas>
            </div>
            <div class="sig-pad-actions">
              <button class="btn btn-sm btn-secondary" data-clear="sig-landlord">Clear</button>
              <input type="text" id="sig-landlord-typed" class="sig-typed-input" placeholder="Or type your name to sign">
            </div>
          </div>
          <div class="sig-pad-group">
            <label>Tenant Signature</label>
            <div class="sig-pad-wrapper">
              <canvas id="sig-tenant" class="sig-canvas"></canvas>
            </div>
            <div class="sig-pad-actions">
              <button class="btn btn-sm btn-secondary" data-clear="sig-tenant">Clear</button>
              <input type="text" id="sig-tenant-typed" class="sig-typed-input" placeholder="Or type your name to sign">
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
