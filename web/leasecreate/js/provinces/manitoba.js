// Manitoba — The Residential Tenancies Act (C.C.S.M. c. R119)

export const manitoba = {
  name: 'Manitoba',
  code: 'MB',
  legislation: 'The Residential Tenancies Act, C.C.S.M. c. R119',
  legislationShort: 'MB RTA',
  regulator: 'Residential Tenancies Branch (RTB)',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'Manitoba does not mandate a standard lease form but written agreement is required.',
    'Security deposit max is half of one month\'s rent.',
    'Rent increases limited to annual guideline set by RTB.',
    'Landlord must provide condition report at move-in.',
  ],

  rentRules: {
    maxDeposit: 'Half month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: true,
    guidelineNote: 'Annual guideline set by Residential Tenancies Branch. 3 months\' notice required.',
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
    'Post-dated cheques requirement',
    'Clauses contracting out of the RTA',
    'No-children clauses',
  ],

  schedules: [
    { id: 'conditionReport', name: 'Condition Report', description: 'Unit condition at move-in (required by law)' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
  ],

  terminationNotice: {
    tenantMonthly: '1 month',
    tenantFixed: 'Ends on term date',
    landlordPersonalUse: '3 months',
  },
};
