// Feature 5: Tenant Rights Sidebar
// Collapsible sidebar showing key rights for the selected province

const rightsData = {
  ON: {
    title: 'Ontario Tenant Rights',
    legislation: 'Residential Tenancies Act, 2006 + Bill 60 (2025)',
    rights: [
      { title: 'Standard Lease', text: 'Landlord must provide the Ontario Standard Lease within 21 days of your written request. If they refuse, you can withhold one month\'s rent.', section: 'O. Reg. 9/18' },
      { title: 'No-Pet Clauses Void', text: 'No-pet clauses are void and unenforceable. However, you can be evicted if your pet causes damage, noise, or allergic reactions to others.', section: 'RTA s.14' },
      { title: 'Deposits', text: 'Only a last month\'s rent deposit is allowed. No security deposits, damage deposits, or key deposits exceeding replacement cost.', section: 'RTA s.105-109' },
      { title: 'Rent Increases', text: 'Limited to the annual guideline (2.5% for 2025). Units first occupied after Nov 15, 2018 are exempt from rent control.', section: 'RTA s.116-120' },
      { title: 'Maintenance', text: 'Landlord must keep the unit in good repair and comply with health/safety standards, regardless of what the lease says.', section: 'RTA s.20' },
      { title: 'Entry Rights', text: 'Landlord must give 24 hours written notice and can only enter between 8am-8pm, except in emergencies.', section: 'RTA s.25-27' },
      { title: 'Eviction Protection', text: 'You can only be evicted through the LTB process. Lockouts and self-help evictions are illegal.', section: 'RTA s.39' },
      { title: 'Right to Sublet/Assign', text: 'Landlord cannot unreasonably refuse a sublet or assignment request.', section: 'RTA s.95-98' },
    ],
  },
  BC: {
    title: 'BC Tenant Rights',
    legislation: 'Residential Tenancy Act, SBC 2002, c. 78',
    rights: [
      { title: 'Deposits', text: 'Security deposit: max half month\'s rent. Pet damage deposit: additional half month. Both must be returned within 15 days of move-out if condition report done.', section: 'RTA s.19-20' },
      { title: 'Condition Reports', text: 'Landlord MUST do a move-in and move-out condition inspection. Without it, landlord cannot claim against your deposit.', section: 'RTA s.23-24' },
      { title: 'Rent Increases', text: 'Limited to annual allowable amount set by RTB. 3 months notice required on the approved form.', section: 'RTA s.42-43' },
      { title: 'Repairs', text: 'Landlord must maintain the unit. If they don\'t, you can apply to the RTB for a rent reduction or repair order.', section: 'RTA s.32' },
      { title: 'Entry', text: '24 hours written notice required. Entry only between 8am-9pm. Emergency entry excepted.', section: 'RTA s.29' },
      { title: 'Fixed-Term Leases', text: '"Vacate clauses" at end of fixed term are restricted. Most fixed-term leases convert to month-to-month automatically.', section: 'RTA s.44' },
    ],
  },
  AB: {
    title: 'Alberta Tenant Rights',
    legislation: 'Residential Tenancies Act, RSA 2004, c. R-17.1',
    rights: [
      { title: 'Deposits', text: 'Max one month\'s rent. Must be held in a trust account. Landlord must pay interest annually.', section: 'RTRA s.46' },
      { title: 'No Rent Control', text: 'Alberta has no rent control, but landlord must give proper notice (3+ months for periodic tenancy) and only one increase per year.', section: 'RTRA s.54' },
      { title: 'Inspections', text: 'Move-in inspection reports are mandatory. Both parties should sign.', section: 'RTRA s.19' },
      { title: 'Repairs', text: 'Landlord must keep the unit habitable and in good repair.', section: 'RTRA s.16' },
      { title: 'No Lockouts', text: 'Self-help evictions and lockouts are illegal. Must go through RTDRS.', section: 'RTRA s.24' },
    ],
  },
  QC: {
    title: 'Quebec Tenant Rights',
    legislation: 'Civil Code of Quebec, arts. 1851-2000',
    rights: [
      { title: 'No Deposits', text: 'ALL deposits are prohibited in Quebec. Landlord can only collect first month\'s rent in advance. No damage, security, or key deposits.', section: 'CCQ art. 1904' },
      { title: 'Automatic Renewal', text: 'Your lease renews automatically. Landlord must give formal notice to modify rent or conditions. You can refuse increases.', section: 'CCQ art. 1941' },
      { title: 'Rent Disclosure', text: 'Landlord must disclose the lowest rent paid in the previous 12 months. You can contest increases at the TAL.', section: 'CCQ art. 1896' },
      { title: 'Assignment Rights', text: 'You have the right to assign (cede) your lease. Landlord can only refuse for serious reasons.', section: 'CCQ art. 1870-1871' },
      { title: 'Repairs', text: 'Landlord must deliver and maintain the dwelling in good habitable condition.', section: 'CCQ art. 1854' },
      { title: 'Entry', text: 'Landlord cannot enter without your consent except in case of emergency.', section: 'CCQ art. 1857' },
      { title: 'Repossession Protection', text: 'Landlord can only repossess for personal use with 6 months notice and meeting strict legal requirements.', section: 'CCQ art. 1957' },
    ],
  },
  MB: {
    title: 'Manitoba Tenant Rights',
    legislation: 'Residential Tenancies Act, C.C.S.M. c. R119',
    rights: [
      { title: 'Deposits', text: 'Max half month\'s rent. Must be held in trust.', section: 'RTA s.41' },
      { title: 'Rent Increases', text: 'Limited by annual guideline. 3 months notice required.', section: 'RTA s.31' },
      { title: 'Repairs', text: 'Landlord must maintain the unit in good repair and comply with health/safety standards.', section: 'RTA s.58' },
      { title: 'Entry', text: '24 hours notice required except in emergency.', section: 'RTA s.74' },
    ],
  },
  SK: {
    title: 'Saskatchewan Tenant Rights',
    legislation: 'Residential Tenancies Act, 2006, SS 2006',
    rights: [
      { title: 'Deposits', text: 'Max one month\'s rent. Must be held in trust and interest paid.', section: 'RTA s.25' },
      { title: 'No Rent Control', text: 'No rent control, but 6 months written notice required for increases.', section: 'RTA s.55' },
      { title: 'Repairs', text: 'Landlord must keep unit in good repair and fit for habitation.', section: 'RTA s.49' },
    ],
  },
  NS: {
    title: 'Nova Scotia Tenant Rights',
    legislation: 'Residential Tenancies Act, RSNS 1989',
    rights: [
      { title: 'Deposits', text: 'Max half month\'s rent.', section: 'RTA s.12' },
      { title: 'Rent Cap', text: 'Temporary rent cap of 5% per year. 4 months notice required.', section: 'Emergency measures' },
      { title: 'Repairs', text: 'Landlord must keep unit in good repair.', section: 'RTA s.9' },
    ],
  },
  NB: {
    title: 'New Brunswick Tenant Rights',
    legislation: 'Residential Tenancies Act, SNB 1975',
    rights: [
      { title: 'Deposits', text: 'Max one month\'s rent.', section: 'RTA s.10' },
      { title: 'Standard Lease', text: 'NB requires use of the Standard Form of Lease.', section: 'RTA s.5' },
      { title: 'Repairs', text: 'Landlord must keep unit fit for habitation.', section: 'RTA s.3' },
    ],
  },
  PE: {
    title: 'PEI Tenant Rights',
    legislation: 'Rental of Residential Property Act, RSNPEI 1988',
    rights: [
      { title: 'Deposits', text: 'First and last month\'s rent may be required.', section: 'RRPA s.12' },
      { title: 'Rent Increases', text: 'Require IRAC approval. Annual allowable percentage published.', section: 'RRPA s.25' },
      { title: 'Repairs', text: 'Landlord must maintain premises in good repair.', section: 'RRPA s.8' },
    ],
  },
  NL: {
    title: 'Newfoundland Tenant Rights',
    legislation: 'Residential Tenancies Act, 2000',
    rights: [
      { title: 'Deposits', text: 'Max 75% of one month\'s rent.', section: 'RTA s.14' },
      { title: 'No Rent Control', text: 'No rent control. 6 months notice required for increases.', section: 'RTA s.18' },
      { title: 'Repairs', text: 'Landlord must keep unit in good repair and comply with health standards.', section: 'RTA s.10' },
    ],
  },
};

export function getRightsData(provinceCode) {
  return rightsData[provinceCode] || null;
}

export function renderRightsSidebar(provinceCode) {
  const data = rightsData[provinceCode];
  if (!data) return '';

  return `
    <div class="rights-header">
      <h3>${data.title}</h3>
      <p class="rights-legislation">${data.legislation}</p>
    </div>
    <div class="rights-list">
      ${data.rights.map(r => `
        <details class="rights-item">
          <summary>
            <strong>${r.title}</strong>
            <span class="rights-section">${r.section}</span>
          </summary>
          <p>${r.text}</p>
        </details>
      `).join('')}
    </div>
  `;
}
