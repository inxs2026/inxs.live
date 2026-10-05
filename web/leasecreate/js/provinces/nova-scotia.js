// Nova Scotia — Residential Tenancies Act (RSNS 1989, c. 401)

export const novaScotia = {
  name: 'Nova Scotia',
  code: 'NS',
  legislation: 'Residential Tenancies Act, RSNS 1989, c. 401',
  legislationShort: 'NS RTA',
  regulator: 'Residential Tenancies Program',
  standardLeaseRequired: true,
  standardLeaseForm: 'Nova Scotia Standard Form of Lease',
  notes: [
    'Nova Scotia requires use of the Standard Form of Lease.',
    'Security deposit max is half of one month\'s rent.',
    'Temporary rent cap introduced (currently 5% max annual increase).',
    'Landlord must provide condition report.',
  ],

  rentRules: {
    maxDeposit: 'Half month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: true,
    guidelineNote: 'Temporary rent cap of 5% annually. 4 months\' notice required.',
    postDatedCheques: false,
    postDatedNote: 'Cannot be required.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Unit Address', required: true },
    { id: 'term', label: 'Tenancy Term', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'securityDeposit', label: 'Security Deposit (max half month)', required: false },
    { id: 'services', label: 'Services Included', required: true },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Security deposit exceeding half month\'s rent',
    'Clauses contracting out of the Act',
    'No-children clauses',
    'Post-dated cheques requirement',
  ],

  schedules: [
    { id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
  ],

  terminationNotice: {
    tenantMonthly: '1 month',
    tenantFixed: 'Ends on term date',
    landlordPersonalUse: 'Varies',
  },
};
