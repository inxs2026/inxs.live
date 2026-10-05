// Ontario — Residential Tenancies Act, 2006 (RTA) + Bill 60 (2025)
// Ontario REQUIRES the Standard Lease (Form 2229E) for most residential tenancies

export const ontario = {
  name: 'Ontario',
  code: 'ON',
  legislation: 'Residential Tenancies Act, 2006, S.O. 2006, c. 17',
  legislationShort: 'RTA',
  regulator: 'Landlord and Tenant Board (LTB)',
  standardLeaseRequired: true,
  standardLeaseForm: 'Ontario Standard Lease (Form 2229E)',
  notes: [
    'Ontario REQUIRES use of the Standard Lease for most residential tenancies.',
    'Bill 60 (Homeowner Protection Act, 2025) introduced additional tenant protections.',
    'Landlord must provide standard lease within 21 days of tenant\'s written request.',
    'Rent deposit limited to one month\'s rent (last month\'s rent deposit).',
  ],

  rentRules: {
    maxDeposit: 'Last month\'s rent only',
    securityDepositAllowed: false,
    rentIncreaseGuideline: true,
    guidelineNote: 'Annual guideline set by province (2.5% for 2025). Exemptions for units first occupied after Nov 15, 2018.',
    postDatedCheques: false,
    postDatedNote: 'Cannot require post-dated cheques or automatic payments.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Unit Address', required: true },
    { id: 'term', label: 'Tenancy Term (Fixed / Month-to-Month)', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'rentDeposit', label: 'Last Month\'s Rent Deposit', required: true },
    { id: 'services', label: 'Services & Utilities Included', required: true },
    { id: 'parking', label: 'Parking (if applicable)', required: false },
    { id: 'insurance', label: 'Tenant Insurance Requirement', required: false },
    { id: 'maintenance', label: 'Maintenance & Repairs Obligations', required: true },
    { id: 'smoking', label: 'Smoking Rules', required: false },
    { id: 'pets', label: 'Pet Rules (note: no-pet clauses unenforceable)', required: false },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'No-pet clauses (unenforceable under RTA s.14)',
    'Key deposit exceeding replacement cost',
    'Security deposits of any kind (only last month\'s rent allowed)',
    'Post-dated cheques requirement',
    'Penalties for guests or additional occupants (s.21)',
    'Restricting tenant\'s right to assign or sublet (unreasonably)',
    'Clauses requiring tenant to pay for all repairs',
    'Automatic rent increases beyond guideline',
    'No-children clauses (Human Rights Code)',
  ],

  schedules: [
    { id: 'maintenance', name: 'Maintenance & Repair Schedule', description: 'Details landlord vs tenant maintenance responsibilities' },
    { id: 'parking', name: 'Parking Agreement', description: 'Terms for parking space(s) included or rented separately' },
    { id: 'storage', name: 'Storage Locker Agreement', description: 'Terms for storage space usage' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet rules and damage expectations (cannot prohibit pets)' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Breakdown of utility responsibilities and sub-metering' },
    { id: 'moveInInspection', name: 'Move-In/Move-Out Inspection Report', description: 'Unit condition at start and end of tenancy' },
    { id: 'keyReceipt', name: 'Key & Access Device Receipt', description: 'Record of keys/fobs issued and deposit (if any)' },
    { id: 'smoking', name: 'Smoking Policy', description: 'Designated smoking areas and cannabis policy' },
    { id: 'commonAreas', name: 'Common Areas & Amenities', description: 'Rules for shared spaces (gym, laundry, rooftop, etc.)' },
    { id: 'renovation', name: 'Renovation/Alteration Agreement', description: 'Permission and terms for tenant modifications' },
  ],

  terminationNotice: {
    tenantFixed: '60 days before end of term',
    tenantMonthly: '60 days (must end on last day of rental period)',
    landlordPersonalUse: '60 days + 1 month rent compensation (N12)',
    landlordRenovation: '120 days + 1 month rent compensation + right of first refusal (N13)',
  },
};
