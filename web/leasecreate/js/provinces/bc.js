// British Columbia — Residential Tenancy Act (RTA) [SBC 2002] c. 78

export const bc = {
  name: 'British Columbia',
  code: 'BC',
  legislation: 'Residential Tenancy Act, SBC 2002, c. 78',
  legislationShort: 'BC RTA',
  regulator: 'Residential Tenancy Branch (RTB)',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'BC does not mandate a standard lease form but provides a recommended template.',
    'Security deposit max is half of one month\'s rent.',
    'Pet damage deposit is an additional half month\'s rent.',
    'Move-in/move-out condition inspection reports are legally required.',
  ],

  rentRules: {
    maxDeposit: 'Half month\'s rent (security) + half month\'s rent (pet damage, if applicable)',
    securityDepositAllowed: true,
    rentIncreaseGuideline: true,
    guidelineNote: 'Maximum annual increase set by RTB. Must give 3 months\' notice on approved RTB form.',
    postDatedCheques: false,
    postDatedNote: 'Cannot require post-dated cheques.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord & Tenant Names', required: true },
    { id: 'address', label: 'Rental Unit Address', required: true },
    { id: 'term', label: 'Tenancy Start Date & Type (Fixed/Periodic)', required: true },
    { id: 'rent', label: 'Rent Amount & Due Date', required: true },
    { id: 'securityDeposit', label: 'Security Deposit (max half month)', required: false },
    { id: 'petDeposit', label: 'Pet Damage Deposit (max half month)', required: false },
    { id: 'services', label: 'Services & Facilities Included', required: true },
    { id: 'conditionReport', label: 'Condition Inspection Report (required by law)', required: true },
    { id: 'pets', label: 'Pet Permission', required: false },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Security deposit exceeding half month\'s rent',
    'Post-dated cheques requirement',
    'Unreasonable restrictions on guests',
    'Automatic lease termination clauses',
    'Penalties that contradict the RTA',
    'No-children clauses (Human Rights Code)',
  ],

  schedules: [
    { id: 'conditionReport', name: 'Condition Inspection Report', description: 'REQUIRED — document unit condition at move-in and move-out' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet rules, damage deposit terms, and expectations' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },
    { id: 'storage', name: 'Storage Agreement', description: 'Storage space terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibility breakdown' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
    { id: 'commonAreas', name: 'Common Areas & Rules', description: 'Shared amenities rules' },
    { id: 'strata', name: 'Strata Rules & Bylaws', description: 'Applicable strata bylaws the tenant must follow' },
  ],

  terminationNotice: {
    tenantMonthly: '1 full month\'s notice',
    tenantFixed: 'Ends automatically unless renewed',
    landlordPersonalUse: '2 months + 1 month rent compensation',
    landlordRenovation: '4 months + 1 month rent compensation',
  },
};
