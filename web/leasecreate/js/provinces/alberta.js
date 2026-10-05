// Alberta — Residential Tenancies Act (RSA 2004) c. R-17.1

export const alberta = {
  name: 'Alberta',
  code: 'AB',
  legislation: 'Residential Tenancies Act, RSA 2004, c. R-17.1',
  legislationShort: 'RTRA',
  regulator: 'Residential Tenancy Dispute Resolution Service (RTDRS)',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'Alberta does not mandate a standard lease form.',
    'Security deposit cannot exceed one month\'s rent.',
    'Landlord must place deposit in a trust account and pay interest.',
    'No rent control — landlords can increase rent with proper notice.',
  ],

  rentRules: {
    maxDeposit: 'One month\'s rent (security deposit)',
    securityDepositAllowed: true,
    rentIncreaseGuideline: false,
    guidelineNote: 'No rent control. Landlord must give 3 months\' notice for periodic tenancy increases. Only one increase per year.',
    postDatedCheques: true,
    postDatedNote: 'Post-dated cheques can be requested but not required by law.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Premises Address', required: true },
    { id: 'term', label: 'Tenancy Term & Type', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'securityDeposit', label: 'Security Deposit Amount', required: false },
    { id: 'services', label: 'Services & Utilities Included', required: true },
    { id: 'pets', label: 'Pet Permission', required: false },
    { id: 'smoking', name: 'Smoking Policy', required: false },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Security deposit exceeding one month\'s rent',
    'Clauses contracting out of the RTRA',
    'Seizure of tenant\'s property for unpaid rent',
    'Lockouts without proper legal process',
    'No-children clauses (Alberta Human Rights Act)',
  ],

  schedules: [
    { id: 'moveInInspection', name: 'Move-In Inspection Report', description: 'Unit condition documentation (strongly recommended)' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet rules and conditions (can restrict or prohibit pets)' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },
    { id: 'storage', name: 'Storage Agreement', description: 'Storage space terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
    { id: 'condominium', name: 'Condominium Bylaws', description: 'Applicable condo bylaws' },
  ],

  terminationNotice: {
    tenantFixed: 'Ends on term date (no notice required unless periodic)',
    tenantMonthly: '1 calendar month (must be given before 1st of month)',
    tenantWeekly: '1 full tenancy week',
    landlordSubstantialBreach: '14 days',
    landlordDemolition: '365 days',
  },
};
