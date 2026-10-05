// Quebec — Civil Code of Québec (CCQ) + Tribunal administratif du logement (TAL)

export const quebec = {
  name: 'Quebec',
  code: 'QC',
  legislation: 'Civil Code of Québec (CCQ), articles 1851–2000',
  legislationShort: 'CCQ',
  regulator: 'Tribunal administratif du logement (TAL)',
  standardLeaseRequired: true,
  standardLeaseForm: 'Bail de logement (mandatory TAL form)',
  notes: [
    'Quebec REQUIRES the mandatory TAL lease form (Bail de logement) for dwellings.',
    'Security deposits are PROHIBITED — only first month\'s rent can be collected.',
    'Lease automatically renews unless tenant gives notice (3-6 months depending on term).',
    'Landlord must disclose lowest rent paid in previous 12 months.',
  ],

  rentRules: {
    maxDeposit: 'None — security deposits are prohibited',
    securityDepositAllowed: false,
    rentIncreaseGuideline: true,
    guidelineNote: 'TAL publishes annual guidelines. Tenant can refuse increase and landlord must apply to TAL to impose it.',
    postDatedCheques: false,
    postDatedNote: 'Cannot require post-dated cheques.',
  },

  requiredClauses: [
    { id: 'parties', label: 'Landlord (locateur) & Tenant (locataire) Names', required: true },
    { id: 'address', label: 'Dwelling Address (logement)', required: true },
    { id: 'term', label: 'Lease Term (durée du bail)', required: true },
    { id: 'rent', label: 'Rent Amount & Payment Terms (loyer)', required: true },
    { id: 'lowestRent', label: 'Lowest Rent Paid in Previous 12 Months', required: true },
    { id: 'services', label: 'Services & Conditions Included', required: true },
    { id: 'bylaw', label: 'Building Regulations (règlement de l\'immeuble)', required: false },
    { id: 'additionalTerms', label: 'Additional Terms', required: false },
  ],

  prohibitedClauses: [
    'Any security deposit or damage deposit',
    'Clauses waiving tenant\'s rights under CCQ',
    'Penalty clauses for exercising legal rights',
    'Clauses giving landlord right to enter without notice/consent (except emergency)',
    'No-children clauses (Charter of Human Rights and Freedoms)',
    'Clauses limiting lease transfer (cession) rights',
  ],

  schedules: [
    { id: 'bylaw', name: 'Building Regulations (Règlement d\'immeuble)', description: 'Rules for common areas, noise, etc.' },
    { id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },
    { id: 'storage', name: 'Storage Agreement', description: 'Storage locker terms' },
    { id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibility breakdown' },
    { id: 'moveInInspection', name: 'Move-In Inspection Report (État des lieux)', description: 'Unit condition at move-in' },
    { id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions (can be restricted in Quebec)' },
    { id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },
  ],

  terminationNotice: {
    tenantFixed12Months: '3–6 months before end of term',
    tenantMonthly: '1–2 months before end',
    landlordRepossession: '6 months notice + conditions under CCQ',
    landlordRenovation: '6 months notice + right of first refusal',
  },
};
