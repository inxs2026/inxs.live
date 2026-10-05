// Feature 6: Auto-fill from LeaseScan
// Import scanned lease data from LeaseScan via localStorage or file upload

const LEASESCAN_KEY = 'leaseScan_lastResult';

export function hasLeaseScanData() {
  try {
    const data = localStorage.getItem(LEASESCAN_KEY);
    return !!data;
  } catch {
    return false;
  }
}

export function getLeaseScanData() {
  try {
    return JSON.parse(localStorage.getItem(LEASESCAN_KEY));
  } catch {
    return null;
  }
}

// Parse a text-based lease and extract key fields
export function parseLeaseText(text) {
  const result = {};

  // Extract landlord name
  const landlordMatch = text.match(/landlord[:\s]+([A-Z][a-zA-Z\s.']+?)(?:\n|,|\()/i);
  if (landlordMatch) result.landlordName = landlordMatch[1].trim();

  // Extract tenant name
  const tenantMatch = text.match(/tenant[:\s]+([A-Z][a-zA-Z\s.']+?)(?:\n|,|\()/i);
  if (tenantMatch) result.tenantName = tenantMatch[1].trim();

  // Extract address
  const addressMatch = text.match(/(?:address|premises|unit)[:\s]+(\d+\s+[A-Za-z\s.,']+?)(?:\n|(?:unit|apt|suite))/i);
  if (addressMatch) result.unitAddress = addressMatch[1].trim();

  // Extract unit number
  const unitMatch = text.match(/(?:unit|apt|suite|apartment)[:\s#]+(\w+)/i);
  if (unitMatch) result.unitNumber = unitMatch[1].trim();

  // Extract city
  const cityMatch = text.match(/(?:city|municipality)[:\s]+([A-Za-z\s.'-]+?)(?:\n|,)/i);
  if (cityMatch) result.city = cityMatch[1].trim();

  // Extract postal code
  const postalMatch = text.match(/[A-Z]\d[A-Z]\s?\d[A-Z]\d/);
  if (postalMatch) result.postalCode = postalMatch[0].trim();

  // Extract rent amount
  const rentMatch = text.match(/(?:rent|monthly\s+rent|loyer)[:\s]*\$?\s*([\d,]+\.?\d*)/i);
  if (rentMatch) result.rentAmount = rentMatch[1].replace(/,/g, '');

  // Extract dates
  const datePattern = /(\d{4}[-/]\d{2}[-/]\d{2}|\w+\s+\d{1,2},?\s+\d{4})/g;
  const dates = [...text.matchAll(datePattern)].map(m => m[1]);
  if (dates.length >= 1) {
    const startContext = text.match(/(?:commence|start|begin)[^.]*?(\d{4}[-/]\d{2}[-/]\d{2}|\w+\s+\d{1,2},?\s+\d{4})/i);
    if (startContext) result.startDate = normalizeDate(startContext[1]);
    const endContext = text.match(/(?:end|expire|terminat)[^.]*?(\d{4}[-/]\d{2}[-/]\d{2}|\w+\s+\d{1,2},?\s+\d{4})/i);
    if (endContext) result.endDate = normalizeDate(endContext[1]);
  }

  // Extract phone numbers
  const phones = text.match(/\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g);
  if (phones && phones.length >= 1) result.landlordPhone = phones[0];
  if (phones && phones.length >= 2) result.tenantPhone = phones[1];

  // Extract emails
  const emails = text.match(/[\w.-]+@[\w.-]+\.\w{2,}/g);
  if (emails && emails.length >= 1) result.landlordEmail = emails[0];
  if (emails && emails.length >= 2) result.tenantEmail = emails[1];

  // Detect pets
  if (/pets?\s+(are\s+)?permitted|pets?\s+allowed/i.test(text)) result.petsAllowed = true;
  if (/no\s+pets?|pets?\s+not\s+permitted|pets?\s+prohibited/i.test(text)) result.petsAllowed = false;

  // Detect smoking
  if (/smoking\s+(is\s+)?permitted|smoking\s+allowed/i.test(text)) result.smokingAllowed = true;
  if (/no\s+smoking|smoking\s+prohibited|smoke[\s-]?free/i.test(text)) result.smokingAllowed = false;

  // Detect term type
  if (/month[\s-]to[\s-]month|periodic/i.test(text)) result.termType = 'monthly';
  else if (/fixed\s+term|one\s+year|twelve\s+months/i.test(text)) result.termType = 'fixed';

  // Detect furnished
  if (/furnished/i.test(text) && !/unfurnished/i.test(text)) result.isFurnished = true;

  return result;
}

function normalizeDate(dateStr) {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return '';
    return d.toISOString().split('T')[0];
  } catch {
    return '';
  }
}

export function renderImportSection() {
  const hasData = hasLeaseScanData();
  return `
    <div class="import-section">
      <h4>Import from Existing Lease</h4>
      <div class="import-options">
        ${hasData ? `
          <button class="btn btn-sm btn-primary" id="btn-import-leasescan">
            Import from LeaseScan
          </button>
          <span class="import-note">Data found from a recent LeaseScan analysis</span>
        ` : ''}
        <div class="import-upload">
          <label class="btn btn-sm btn-secondary" for="import-file">
            Paste or Upload Lease Text
          </label>
          <input type="file" id="import-file" accept=".txt,.text" hidden>
        </div>
        <button class="btn btn-sm btn-secondary" id="btn-import-paste">
          Paste Lease Text
        </button>
      </div>
    </div>
  `;
}
