// New Brunswick — Residential Tenancies Act (SNB 1975, c. R-10.2)

export const newBrunswick = {
  name: 'New Brunswick',
  code: 'NB',
  legislation: 'Residential Tenancies Act, SNB 1975, c. R-10.2',
  legislationShort: 'NB RTA',
  regulator: 'Residential Tenancies Tribunal',
  standardLeaseRequired: true,
  standardLeaseForm: 'New Brunswick Standard Form of Lease',
  notes: [
    'New Brunswick requires use of the Standard Form of Lease.',
    'Security deposit max is one month\'s rent.',
    'No rent control — but notice required for increases.',
  ],

  rentRules: {
    maxDeposit: 'One month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: false,
    guidelineNote: 'No rent control. Landlord must give notice for rent increase.',
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
    'Security deposit exceeding one month\'s rent',
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
    tenantFixed: 'Ends on term date',
  },
};
