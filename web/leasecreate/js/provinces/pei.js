// Prince Edward Island — Rental of Residential Property Act (RSNPEI 1988, c. R-13.1)

export const pei = {
  name: 'Prince Edward Island',
  code: 'PE',
  legislation: 'Rental of Residential Property Act, RSNPEI 1988, c. R-13.1',
  legislationShort: 'RRPA',
  regulator: 'Island Regulatory and Appeals Commission (IRAC)',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'PEI does not mandate a standard lease form.',
    'Security deposit max is one week\'s rent (weekly) or one month (monthly).',
    'Rent increases require IRAC approval.',
  ],

  rentRules: {
    maxDeposit: 'First and last month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: true,
    guidelineNote: 'Rent increases require IRAC approval. Annual allowable percentage published by IRAC.',
    postDatedCheques: false,
    postDatedNote: 'Cannot be required.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Unit Address', required: true },
    { id: 'term', label: 'Tenancy Term', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'securityDeposit', label: 'Security Deposit', required: false },
    { id: 'services', label: 'Services Included', required: true },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Clauses contracting out of the Act',
    'No-children clauses',
  ],

  schedules: [
    { id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
  ],

  terminationNotice: {
    tenantMonthly: '1 month (on or before 1st of month)',
    tenantFixed: 'Ends on term date',
  },
};
