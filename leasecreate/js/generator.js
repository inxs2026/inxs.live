// Lease document generator — builds structured lease HTML for preview and PDF export
import { provinces } from './provinces/index.js';

export function generateLease(formData, selectedSchedules) {
  const province = provinces[formData.province];
  if (!province) return null;

  const today = new Date().toLocaleDateString('en-CA', { year: 'numeric', month: 'long', day: 'numeric' });
  const keepSectionClass = 'lease-section print-keep-together';
  const flowSectionClass = 'lease-section';
  const signatureClass = 'lease-section lease-signatures print-page-group';

  let html = '';

  // ── Header ──
  html += `
    <div class="lease-header print-page-group">
      <h1>RESIDENTIAL TENANCY AGREEMENT</h1>
      <p class="lease-subtitle">Province of ${province.name}</p>
      <p class="lease-legislation">Governed by: ${province.legislation}</p>
      ${province.standardLeaseRequired ? `<p class="lease-note">Note: ${province.standardLeaseForm} is required in ${province.name}. This document supplements — it does not replace — the official form.</p>` : ''}
      <p class="lease-date">Date: ${today}</p>
    </div>
  `;

  // ── Section 1: Parties ──
  html += `
    <div class="${keepSectionClass}">
      <h2>1. PARTIES</h2>
      <div class="lease-field-group print-keep-together">
        <div class="lease-field">
          <label>LANDLORD (the "Landlord")</label>
          <p><strong>${esc(formData.landlordName)}</strong></p>
          ${formData.landlordAddress ? `<p>${esc(formData.landlordAddress)}</p>` : ''}
          ${formData.landlordPhone ? `<p>Phone: ${esc(formData.landlordPhone)}</p>` : ''}
          ${formData.landlordEmail ? `<p>Email: ${esc(formData.landlordEmail)}</p>` : ''}
        </div>
        <div class="lease-field">
          <label>TENANT (the "Tenant")</label>
          <p><strong>${esc(formData.tenantName)}</strong></p>
          ${formData.tenantPhone ? `<p>Phone: ${esc(formData.tenantPhone)}</p>` : ''}
          ${formData.tenantEmail ? `<p>Email: ${esc(formData.tenantEmail)}</p>` : ''}
        </div>
        ${formData.additionalTenants ? `
        <div class="lease-field full-width">
          <label>Additional Tenant(s)</label>
          <p>${esc(formData.additionalTenants)}</p>
        </div>` : ''}
      </div>
    </div>
  `;

  // ── Section 2: Rental Unit ──
  html += `
    <div class="${keepSectionClass}">
      <h2>2. RENTAL UNIT</h2>
      <p><strong>Address:</strong> ${esc(formData.unitAddress)}</p>
      ${formData.unitNumber ? `<p><strong>Unit/Suite:</strong> ${esc(formData.unitNumber)}</p>` : ''}
      <p><strong>City:</strong> ${esc(formData.city)}, <strong>Province:</strong> ${province.name}, <strong>Postal Code:</strong> ${esc(formData.postalCode)}</p>
      ${formData.unitType ? `<p><strong>Type:</strong> ${esc(formData.unitType)}</p>` : ''}
      ${formData.isFurnished ? '<p><strong>Furnished:</strong> Yes</p>' : ''}
      ${formData.parkingIncluded ? `<p><strong>Parking:</strong> Included${formData.parkingDetails ? ' — ' + esc(formData.parkingDetails) : ''}</p>` : ''}
      ${formData.storageIncluded ? '<p><strong>Storage:</strong> Included</p>' : ''}
    </div>
  `;

  // ── Section 3: Term ──
  html += `
    <div class="${keepSectionClass}">
      <h2>3. TERM OF TENANCY</h2>
      <p><strong>Type:</strong> ${formData.termType === 'fixed' ? 'Fixed Term' : 'Month-to-Month (Periodic)'}</p>
      <p><strong>Start Date:</strong> ${esc(formData.startDate)}</p>
      ${formData.termType === 'fixed' ? `<p><strong>End Date:</strong> ${esc(formData.endDate)}</p>` : ''}
      <p class="lease-info">Termination notice requirements per ${province.legislationShort}:</p>
      <ul>
        ${Object.entries(province.terminationNotice).map(([k, v]) => `<li>${formatKey(k)}: ${v}</li>`).join('')}
      </ul>
    </div>
  `;

  // ── Section 4: Rent ──
  html += `
    <div class="${keepSectionClass}">
      <h2>4. RENT</h2>
      <p><strong>Monthly Rent:</strong> $${esc(formData.rentAmount)}</p>
      <p><strong>Due Date:</strong> ${esc(formData.rentDueDay)} of each month</p>
      <p><strong>Payment Method:</strong> ${esc(formData.paymentMethod || 'As agreed between parties')}</p>
      ${province.rentRules.rentIncreaseGuideline ? `<p class="lease-info">Rent increases: ${province.rentRules.guidelineNote}</p>` : `<p class="lease-info">Note: ${province.rentRules.guidelineNote}</p>`}
    </div>
  `;

  // ── Section 5: Deposits ──
  html += `<div class="${keepSectionClass}"><h2>5. DEPOSITS</h2>`;
  if (!province.rentRules.securityDepositAllowed && province.code !== 'ON') {
    html += `<p class="lease-warning">Security deposits are <strong>prohibited</strong> in ${province.name}.</p>`;
    if (province.code === 'QC') {
      html += `<p>Only the first month's rent may be collected in advance.</p>`;
    }
  } else if (province.code === 'ON') {
    html += `
      <p><strong>Last Month's Rent Deposit:</strong> $${esc(formData.lastMonthDeposit || formData.rentAmount)}</p>
      <p class="lease-info">Ontario prohibits security deposits. Only a last month's rent deposit is allowed (RTA s.106).</p>
    `;
  } else {
    html += `
      <p><strong>Security Deposit:</strong> $${esc(formData.securityDeposit || '0.00')}</p>
      <p class="lease-info">Maximum allowed: ${province.rentRules.maxDeposit}</p>
    `;
    if (formData.petDeposit) {
      html += `<p><strong>Pet Damage Deposit:</strong> $${esc(formData.petDeposit)}</p>`;
    }
  }
  html += `</div>`;

  // ── Section 6: Services & Utilities ──
  html += `
    <div class="${keepSectionClass}">
      <h2>6. SERVICES & UTILITIES</h2>
      <table class="lease-table">
        <thead><tr><th>Service</th><th>Included in Rent</th><th>Tenant Pays Separately</th></tr></thead>
        <tbody>
          ${buildUtilityRow('Heat', formData.utilities)}
          ${buildUtilityRow('Electricity', formData.utilities)}
          ${buildUtilityRow('Water', formData.utilities)}
          ${buildUtilityRow('Internet', formData.utilities)}
          ${buildUtilityRow('Cable/TV', formData.utilities)}
          ${buildUtilityRow('Laundry', formData.utilities)}
          ${buildUtilityRow('Air Conditioning', formData.utilities)}
        </tbody>
      </table>
    </div>
  `;

  // ── Section 7: Rules ──
  html += `
    <div class="${keepSectionClass}">
      <h2>7. RULES & CONDITIONS</h2>
      <p><strong>Smoking:</strong> ${formData.smokingAllowed ? 'Permitted in designated areas' : 'Not permitted on the premises'}</p>
      <p><strong>Pets:</strong> ${formData.petsAllowed ? 'Permitted' : 'Not permitted'}
        ${province.code === 'ON' ? ' <em>(Note: No-pet clauses are void and unenforceable in Ontario per RTA s.14)</em>' : ''}</p>
      ${formData.guestPolicy ? `<p><strong>Guest Policy:</strong> ${esc(formData.guestPolicy)}</p>` : ''}
      ${formData.noisePolicy ? `<p><strong>Noise/Quiet Hours:</strong> ${esc(formData.noisePolicy)}</p>` : ''}
    </div>
  `;

  // ── Section 8: Maintenance ──
  html += `
    <div class="${flowSectionClass}">
      <h2>8. MAINTENANCE & REPAIRS</h2>
      <p>The <strong>Landlord</strong> is responsible for maintaining the rental unit in a good state of repair, fit for habitation, and in compliance with all health, safety, and housing standards as required by the ${province.legislationShort}.</p>
      <p>The <strong>Tenant</strong> is responsible for:</p>
      <ul>
        <li>Keeping the unit reasonably clean</li>
        <li>Promptly reporting any maintenance issues or damage</li>
        <li>Repairing or paying for any damage caused by the tenant, guests, or pets</li>
        <li>Not altering the unit without written consent of the Landlord</li>
      </ul>
      ${formData.maintenanceNotes ? `<p><strong>Additional Notes:</strong> ${esc(formData.maintenanceNotes)}</p>` : ''}
    </div>
  `;

  // ── Section 9: Entry ──
  html += `
    <div class="${keepSectionClass}">
      <h2>9. LANDLORD'S RIGHT OF ENTRY</h2>
      <p>The Landlord may enter the rental unit only in accordance with the ${province.legislationShort}. Except in emergencies, the Landlord must provide:</p>
      <ul>
        <li><strong>Written notice</strong> of at least 24 hours</li>
        <li>Entry only between <strong>8:00 AM and 8:00 PM</strong></li>
        <li>A valid reason as permitted by law (repairs, showing to prospective tenants, inspection, etc.)</li>
      </ul>
    </div>
  `;

  // ── Section 10: Insurance ──
  html += `
    <div class="${keepSectionClass}">
      <h2>10. INSURANCE</h2>
      <p><strong>Tenant Insurance:</strong> ${formData.tenantInsuranceRequired ? 'Required — Tenant must obtain and maintain renter\'s insurance for the duration of the tenancy.' : 'Recommended but not required.'}</p>
      <p>The Landlord\'s insurance does not cover the Tenant\'s personal belongings or liability.</p>
    </div>
  `;

  // ── Section 11: Additional Terms ──
  if (formData.additionalTerms) {
    html += `
      <div class="${flowSectionClass}">
        <h2>11. ADDITIONAL TERMS</h2>
        <div class="lease-additional">${esc(formData.additionalTerms).replace(/\n/g, '<br>')}</div>
        <p class="lease-info">Note: Any term that conflicts with the ${province.legislationShort} is void and unenforceable.</p>
      </div>
    `;
  }

  // ── Section 12: Provincial Legal Notices ──
  html += `
    <div class="${flowSectionClass}">
      <h2>${formData.additionalTerms ? '12' : '11'}. IMPORTANT LEGAL INFORMATION</h2>
      <div class="lease-legal">
        <p>This agreement is governed by the <strong>${province.legislation}</strong>.</p>
        <p>Disputes may be resolved through the <strong>${province.regulator}</strong>.</p>
        <h3>Prohibited Clauses in ${province.name}:</h3>
        <ul>
          ${province.prohibitedClauses.map(c => `<li>${c}</li>`).join('')}
        </ul>
        ${province.notes.map(n => `<p class="lease-info">${n}</p>`).join('')}
      </div>
    </div>
  `;

  // ── Schedules ──
  if (selectedSchedules && selectedSchedules.length > 0) {
    const scheduleSection = formData.additionalTerms ? '13' : '12';
    html += `
      <div class="${keepSectionClass}">
        <h2>${scheduleSection}. SCHEDULES</h2>
        <p>The following schedules are attached to and form part of this Agreement:</p>
        <ul>
          ${selectedSchedules.map((s, i) => `<li><strong>Schedule ${String.fromCharCode(65 + i)}:</strong> ${s.name}</li>`).join('')}
        </ul>
      </div>
    `;

    selectedSchedules.forEach((schedule, i) => {
      html += generateScheduleContent(schedule, i, formData, province);
    });
  }

  // ── Signatures ──
  html += `
    <div class="${signatureClass}">
      <h2>SIGNATURES</h2>
      <p>By signing below, the parties agree to the terms and conditions set out in this Residential Tenancy Agreement and any attached Schedules.</p>
      <div class="sig-grid print-page-group">
        <div class="sig-block">
          <div class="sig-line"></div>
          <p>Landlord Signature</p>
          <p class="sig-name">${esc(formData.landlordName)}</p>
          <p class="sig-date">Date: _______________________</p>
        </div>
        <div class="sig-block">
          <div class="sig-line"></div>
          <p>Tenant Signature</p>
          <p class="sig-name">${esc(formData.tenantName)}</p>
          <p class="sig-date">Date: _______________________</p>
        </div>
      </div>
      ${formData.additionalTenants ? `
      <div class="sig-grid print-page-group" style="margin-top: 30px;">
        <div class="sig-block">
          <div class="sig-line"></div>
          <p>Additional Tenant Signature</p>
          <p class="sig-date">Date: _______________________</p>
        </div>
        <div class="sig-block">
          <div class="sig-line"></div>
          <p>Witness Signature (if applicable)</p>
          <p class="sig-date">Date: _______________________</p>
        </div>
      </div>
      ` : ''}
    </div>
  `;

  return html;
}


// ── Schedule Content Generators ──

function generateScheduleContent(schedule, index, formData, province) {
  const letter = String.fromCharCode(65 + index);
  let html = `
    <div class="lease-section lease-schedule print-page-group">
      <h2>SCHEDULE ${letter}: ${schedule.name.toUpperCase()}</h2>
      <p class="lease-subtitle">${schedule.description}</p>
  `;

  switch (schedule.id) {
    case 'moveInInspection':
    case 'conditionReport':
      html += generateInspectionSchedule(formData);
      break;
    case 'petAgreement':
      html += generatePetSchedule(formData, province);
      break;
    case 'parking':
      html += generateParkingSchedule(formData);
      break;
    case 'storage':
      html += generateStorageSchedule(formData);
      break;
    case 'utilities':
      html += generateUtilitiesSchedule(formData);
      break;
    case 'maintenance':
      html += generateMaintenanceSchedule(formData, province);
      break;
    case 'keyReceipt':
      html += generateKeySchedule(formData);
      break;
    case 'smoking':
      html += generateSmokingSchedule(formData);
      break;
    case 'commonAreas':
      html += generateCommonAreasSchedule(formData);
      break;
    case 'renovation':
      html += generateRenovationSchedule(formData, province);
      break;
    case 'bylaw':
    case 'strata':
    case 'condominium':
      html += generateBylawSchedule(formData, province);
      break;
    default:
      html += `<div class="schedule-blank"><p>Additional terms and conditions as agreed between the parties:</p><div class="blank-lines">${'<div class="blank-line"></div>'.repeat(15)}</div></div>`;
  }

  html += `
    <div class="schedule-sig">
      <div class="sig-grid print-page-group">
        <div class="sig-block"><div class="sig-line"></div><p>Landlord Initials / Date</p></div>
        <div class="sig-block"><div class="sig-line"></div><p>Tenant Initials / Date</p></div>
      </div>
    </div>
  </div>`;

  return html;
}

function generateInspectionSchedule(formData) {
  const rooms = ['Living Room', 'Kitchen', 'Bedroom 1', 'Bedroom 2', 'Bathroom', 'Hallway/Entrance', 'Balcony/Patio', 'Other'];
  const conditions = ['Walls & Ceiling', 'Flooring', 'Windows & Blinds', 'Doors & Locks', 'Light Fixtures', 'Outlets/Switches', 'Appliances', 'Plumbing/Fixtures', 'Cleanliness'];

  return `
    <p><strong>Unit Address:</strong> ${esc(formData.unitAddress)}</p>
    <p><strong>Inspection Date:</strong> _______________________</p>
    <p><strong>Inspected By:</strong> Landlord: _________________ Tenant: _________________</p>
    <table class="lease-table inspection-table">
      <thead>
        <tr><th>Room / Area</th><th>Item</th><th>Condition (Move-In)</th><th>Condition (Move-Out)</th><th>Notes</th></tr>
      </thead>
      <tbody>
        ${rooms.map(room => conditions.map((cond, ci) => `
          <tr>
            ${ci === 0 ? `<td rowspan="${conditions.length}" class="room-cell">${room}</td>` : ''}
            <td>${cond}</td>
            <td class="condition-cell"></td>
            <td class="condition-cell"></td>
            <td class="notes-cell"></td>
          </tr>
        `).join('')).join('')}
      </tbody>
    </table>
    <p><strong>General Notes:</strong></p>
    <div class="blank-lines">${'<div class="blank-line"></div>'.repeat(5)}</div>
  `;
}

function generatePetSchedule(formData, province) {
  return `
    <p>This Pet Agreement forms part of the Residential Tenancy Agreement.</p>
    ${province.code === 'ON' ? '<p class="lease-warning"><strong>Ontario Note:</strong> No-pet clauses are void under RTA s.14. However, a tenant may be evicted if the pet causes damage, noise, or allergic reactions.</p>' : ''}
    <table class="lease-table">
      <thead><tr><th>Pet Type</th><th>Breed</th><th>Name</th><th>Weight</th></tr></thead>
      <tbody>
        <tr><td></td><td></td><td></td><td></td></tr>
        <tr><td></td><td></td><td></td><td></td></tr>
      </tbody>
    </table>
    <h3>Pet Rules</h3>
    <ul>
      <li>Tenant is responsible for all damage caused by pets</li>
      <li>Pets must be supervised in common areas</li>
      <li>Tenant must clean up after pets immediately</li>
      <li>Excessive noise from pets may constitute a disturbance</li>
      <li>Tenant must comply with all municipal animal bylaws</li>
      ${province.rentRules.securityDepositAllowed && province.code === 'BC' ? '<li>Pet damage deposit of up to half month\'s rent may be collected</li>' : ''}
    </ul>
    <p><strong>Additional pet conditions:</strong></p>
    <div class="blank-lines">${'<div class="blank-line"></div>'.repeat(4)}</div>
  `;
}

function generateParkingSchedule(formData) {
  return `
    <h3>Parking Details</h3>
    <p><strong>Parking Space Number:</strong> _______________________</p>
    <p><strong>Location:</strong> _______________________</p>
    <p><strong>Type:</strong> Indoor / Outdoor / Underground (circle one)</p>
    <p><strong>Included in Rent:</strong> Yes / No</p>
    <p><strong>Additional Monthly Cost:</strong> $ _______________________</p>
    <h3>Parking Rules</h3>
    <ul>
      <li>Only registered vehicles may use the assigned space</li>
      <li>Vehicle must be insured and in operable condition</li>
      <li>No storage of hazardous materials</li>
      <li>Snow removal responsibility: _______________________</li>
      <li>Guest parking: _______________________</li>
    </ul>
    <p><strong>Vehicle Information:</strong></p>
    <table class="lease-table">
      <thead><tr><th>Make/Model</th><th>Year</th><th>Colour</th><th>License Plate</th></tr></thead>
      <tbody><tr><td></td><td></td><td></td><td></td></tr></tbody>
    </table>
  `;
}

function generateStorageSchedule(formData) {
  return `
    <h3>Storage Details</h3>
    <p><strong>Storage Unit/Locker Number:</strong> _______________________</p>
    <p><strong>Location:</strong> _______________________</p>
    <p><strong>Included in Rent:</strong> Yes / No</p>
    <p><strong>Additional Monthly Cost:</strong> $ _______________________</p>
    <h3>Storage Rules</h3>
    <ul>
      <li>No hazardous, flammable, or perishable items</li>
      <li>Tenant must provide their own lock</li>
      <li>Landlord is not responsible for theft or damage to stored items</li>
      <li>Contents must not exceed structural weight limits</li>
    </ul>
  `;
}

function generateUtilitiesSchedule(formData) {
  return `
    <h3>Utility Responsibilities</h3>
    <table class="lease-table">
      <thead><tr><th>Utility</th><th>Landlord Pays</th><th>Tenant Pays</th><th>Account Transfer Required</th><th>Estimated Monthly Cost</th></tr></thead>
      <tbody>
        <tr><td>Electricity</td><td></td><td></td><td></td><td></td></tr>
        <tr><td>Natural Gas / Heat</td><td></td><td></td><td></td><td></td></tr>
        <tr><td>Water / Sewer</td><td></td><td></td><td></td><td></td></tr>
        <tr><td>Internet</td><td></td><td></td><td></td><td></td></tr>
        <tr><td>Cable / TV</td><td></td><td></td><td></td><td></td></tr>
        <tr><td>Garbage / Recycling</td><td></td><td></td><td></td><td></td></tr>
      </tbody>
    </table>
    <p><strong>Sub-metering:</strong> Yes / No</p>
    <p><strong>Notes:</strong></p>
    <div class="blank-lines">${'<div class="blank-line"></div>'.repeat(4)}</div>
  `;
}

function generateMaintenanceSchedule(formData, province) {
  return `
    <h3>Maintenance Responsibilities</h3>
    <table class="lease-table">
      <thead><tr><th>Item</th><th>Landlord</th><th>Tenant</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Lawn Care / Snow Removal</td><td></td><td></td><td></td></tr>
        <tr><td>Appliance Repairs</td><td></td><td></td><td></td></tr>
        <tr><td>Plumbing Issues</td><td></td><td></td><td></td></tr>
        <tr><td>Electrical Issues</td><td></td><td></td><td></td></tr>
        <tr><td>HVAC / Furnace Maintenance</td><td></td><td></td><td></td></tr>
        <tr><td>Pest Control</td><td></td><td></td><td></td></tr>
        <tr><td>Light Bulb Replacement</td><td></td><td></td><td></td></tr>
        <tr><td>Smoke/CO Detector Batteries</td><td></td><td></td><td></td></tr>
        <tr><td>Gutter Cleaning</td><td></td><td></td><td></td></tr>
      </tbody>
    </table>
    <p class="lease-info">Per ${province.legislationShort}, the landlord must maintain the unit in a good state of repair regardless of any agreement to the contrary.</p>
  `;
}

function generateKeySchedule(formData) {
  return `
    <h3>Keys & Access Devices Issued</h3>
    <table class="lease-table">
      <thead><tr><th>Item</th><th>Quantity</th><th>Deposit (if any)</th></tr></thead>
      <tbody>
        <tr><td>Unit Key</td><td></td><td></td></tr>
        <tr><td>Mailbox Key</td><td></td><td></td></tr>
        <tr><td>Building Fob/Card</td><td></td><td></td></tr>
        <tr><td>Garage Remote</td><td></td><td></td></tr>
        <tr><td>Storage Key</td><td></td><td></td></tr>
        <tr><td>Other</td><td></td><td></td></tr>
      </tbody>
    </table>
    <p>All keys/devices must be returned at the end of tenancy. Unreturned items may be charged at replacement cost.</p>
  `;
}

function generateSmokingSchedule(formData) {
  return `
    <h3>Smoking Policy</h3>
    <p><strong>Smoking (tobacco):</strong> ${formData.smokingAllowed ? 'Permitted in designated areas only' : 'Prohibited on premises'}</p>
    <p><strong>Cannabis smoking/vaping:</strong> _______________________</p>
    <p><strong>Vaping (e-cigarettes):</strong> _______________________</p>
    <p><strong>Designated smoking area(s):</strong> _______________________</p>
    <h3>Rules</h3>
    <ul>
      <li>No smoking within ______ metres of building entrances, windows, or air intakes</li>
      <li>Tenant is responsible for any damage caused by smoking</li>
      <li>Violation of smoking policy may result in application to terminate tenancy</li>
    </ul>
  `;
}

function generateCommonAreasSchedule(formData) {
  return `
    <h3>Common Areas & Amenities</h3>
    <table class="lease-table">
      <thead><tr><th>Amenity</th><th>Available</th><th>Hours</th><th>Rules/Notes</th></tr></thead>
      <tbody>
        <tr><td>Laundry Room</td><td></td><td></td><td></td></tr>
        <tr><td>Gym/Fitness Room</td><td></td><td></td><td></td></tr>
        <tr><td>Pool</td><td></td><td></td><td></td></tr>
        <tr><td>Rooftop/Terrace</td><td></td><td></td><td></td></tr>
        <tr><td>Party/Meeting Room</td><td></td><td></td><td></td></tr>
        <tr><td>BBQ Area</td><td></td><td></td><td></td></tr>
        <tr><td>Bike Storage</td><td></td><td></td><td></td></tr>
        <tr><td>Other</td><td></td><td></td><td></td></tr>
      </tbody>
    </table>
    <h3>General Rules</h3>
    <ul>
      <li>Common areas must be left clean after use</li>
      <li>Booking may be required for certain amenities</li>
      <li>Guests must be accompanied by tenant</li>
      <li>Quiet hours: _______________________</li>
    </ul>
  `;
}

function generateRenovationSchedule(formData, province) {
  return `
    <h3>Renovation / Alteration Agreement</h3>
    <p>The Tenant requests permission to make the following alterations to the rental unit:</p>
    <div class="blank-lines">${'<div class="blank-line"></div>'.repeat(5)}</div>
    <h3>Conditions</h3>
    <ul>
      <li>All work must be completed in a professional manner</li>
      <li>Tenant must obtain any required municipal permits</li>
      <li>Landlord must approve all changes in writing before work begins</li>
      <li><strong>Restoration:</strong> Tenant will / will not be required to restore the unit to original condition at end of tenancy (circle one)</li>
      <li>Tenant is responsible for all costs associated with the alterations</li>
    </ul>
  `;
}

function generateBylawSchedule(formData, province) {
  return `
    <h3>${province.code === 'BC' ? 'Strata' : province.code === 'AB' ? 'Condominium' : 'Building'} Rules & Bylaws</h3>
    <p>The Tenant acknowledges receipt of and agrees to comply with the following rules and bylaws:</p>
    <div class="blank-lines">${'<div class="blank-line"></div>'.repeat(10)}</div>
    <p class="lease-info">A copy of the full ${province.code === 'BC' ? 'strata bylaws' : 'condominium bylaws'} has been provided to the Tenant.</p>
    <p><strong>Date provided:</strong> _______________________</p>
  `;
}


// ── Helpers ──

function esc(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function formatKey(key) {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase());
}

function buildUtilityRow(name, utilities) {
  const included = utilities && utilities[name.toLowerCase().replace(/\s|\//g, '')] === 'included';
  return `<tr><td>${name}</td><td>${included ? 'Yes' : ''}</td><td>${included ? '' : 'Yes'}</td></tr>`;
}
