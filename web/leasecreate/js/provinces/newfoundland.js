// Newfoundland and Labrador — Residential Tenancies Act, 2000 (SNL 2000, c. R-14.1)

export const newfoundland = {
  name: 'Newfoundland and Labrador',
  code: 'NL',
  legislation: 'Residential Tenancies Act, 2000, SNL 2000, c. R-14.1',
  legislationShort: 'NL RTA',
  regulator: 'Residential Tenancies Division, Service NL',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'NL does not mandate a standard lease form.',
    'Security deposit max is 75% of one month\'s rent.',
    'No rent control.',
  ],

  rentRules: {
    maxDeposit: '75% of one month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: false,
    guidelineNote: 'No rent control. Landlord must give 6 months\' notice.',
    postDatedCheques: false,
    postDatedNote: 'Cannot be required.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Unit Address', required: true },
    { id: 'term', label: 'Tenancy Term', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'securityDeposit', label: 'Security Deposit (max 75% of one month)', required: false },
    { id: 'services', label: 'Services Included', required: true },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Security deposit exceeding 75% of one month\'s rent',
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
    tenantMonthly: '1 month',
    tenantWeekly: '1 week',
    tenantFixed: 'Ends on term date',
  },
};
