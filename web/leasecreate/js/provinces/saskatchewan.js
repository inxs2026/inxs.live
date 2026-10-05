// Saskatchewan — The Residential Tenancies Act, 2006 (SS 2006, c. R-22.0002)

export const saskatchewan = {
  name: 'Saskatchewan',
  code: 'SK',
  legislation: 'The Residential Tenancies Act, 2006, SS 2006, c. R-22.0002',
  legislationShort: 'SK RTA',
  regulator: 'Office of Residential Tenancies (ORT)',
  standardLeaseRequired: false,
  standardLeaseForm: null,
  notes: [
    'Saskatchewan does not have a mandatory standard lease form.',
    'Written tenancy agreement is required.',
    'Security deposit cannot exceed one month\'s rent.',
    'No rent control for private market units.',
  ],

  rentRules: {
    maxDeposit: 'One month\'s rent',
    securityDepositAllowed: true,
    rentIncreaseGuideline: false,
    guidelineNote: 'No rent control. Landlord must give 6 months\' written notice.',
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
    'Seizure of tenant property',
    'No-children clauses',
  ],

  schedules: [
    { id: 'conditionReport', name: 'Condition Report', description: 'Move-in/move-out inspection' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions (can restrict)' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
  ],

  terminationNotice: {
    tenantMonthly: '1 month',
    tenantFixed: 'Ends on term date',
    landlordNonPayment: '15 days',
  },
};
