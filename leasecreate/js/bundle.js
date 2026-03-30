// LeaseCreate — Bundled Application (works without a server / file:// protocol)
// All modules combined into a single IIFE

(function() {
'use strict';

// ══════════════════════════════════════════════════════════════════════════════
// PROVINCES
// ══════════════════════════════════════════════════════════════════════════════

const ontario = {
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

const bc = {
  name: 'British Columbia', code: 'BC',
  legislation: 'Residential Tenancy Act, SBC 2002, c. 78', legislationShort: 'BC RTA',
  regulator: 'Residential Tenancy Branch (RTB)', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['BC does not mandate a standard lease form but provides a recommended template.','Security deposit max is half of one month\'s rent.','Pet damage deposit is an additional half month\'s rent.','Move-in/move-out condition inspection reports are legally required.'],
  rentRules: { maxDeposit: 'Half month\'s rent (security) + half month\'s rent (pet damage, if applicable)', securityDepositAllowed: true, rentIncreaseGuideline: true, guidelineNote: 'Maximum annual increase set by RTB. Must give 3 months\' notice on approved RTB form.', postDatedCheques: false, postDatedNote: 'Cannot require post-dated cheques.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Start Date & Type', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit (max half month)', required: false },{ id: 'petDeposit', label: 'Pet Damage Deposit (max half month)', required: false },{ id: 'services', label: 'Services & Facilities Included', required: true },{ id: 'conditionReport', label: 'Condition Inspection Report (required by law)', required: true },{ id: 'pets', label: 'Pet Permission', required: false },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding half month\'s rent','Post-dated cheques requirement','Unreasonable restrictions on guests','Automatic lease termination clauses','Penalties that contradict the RTA','No-children clauses (Human Rights Code)'],
  schedules: [{ id: 'conditionReport', name: 'Condition Inspection Report', description: 'REQUIRED — document unit condition at move-in and move-out' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet rules, damage deposit terms, and expectations' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },{ id: 'storage', name: 'Storage Agreement', description: 'Storage space terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibility breakdown' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },{ id: 'commonAreas', name: 'Common Areas & Rules', description: 'Shared amenities rules' },{ id: 'strata', name: 'Strata Rules & Bylaws', description: 'Applicable strata bylaws the tenant must follow' }],
  terminationNotice: { tenantMonthly: '1 full month\'s notice', tenantFixed: 'Ends automatically unless renewed', landlordPersonalUse: '2 months + 1 month rent compensation', landlordRenovation: '4 months + 1 month rent compensation' },
};

const alberta = {
  name: 'Alberta', code: 'AB',
  legislation: 'Residential Tenancies Act, RSA 2004, c. R-17.1', legislationShort: 'RTRA',
  regulator: 'Residential Tenancy Dispute Resolution Service (RTDRS)', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['Alberta does not mandate a standard lease form.','Security deposit cannot exceed one month\'s rent.','Landlord must place deposit in a trust account and pay interest.','No rent control — landlords can increase rent with proper notice.'],
  rentRules: { maxDeposit: 'One month\'s rent (security deposit)', securityDepositAllowed: true, rentIncreaseGuideline: false, guidelineNote: 'No rent control. Landlord must give 3 months\' notice for periodic tenancy increases. Only one increase per year.', postDatedCheques: true, postDatedNote: 'Post-dated cheques can be requested but not required by law.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Premises Address', required: true },{ id: 'term', label: 'Tenancy Term & Type', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit Amount', required: false },{ id: 'services', label: 'Services & Utilities Included', required: true },{ id: 'pets', label: 'Pet Permission', required: false },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding one month\'s rent','Clauses contracting out of the RTRA','Seizure of tenant\'s property for unpaid rent','Lockouts without proper legal process','No-children clauses (Alberta Human Rights Act)'],
  schedules: [{ id: 'moveInInspection', name: 'Move-In Inspection Report', description: 'Unit condition documentation (strongly recommended)' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet rules and conditions (can restrict or prohibit pets)' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },{ id: 'storage', name: 'Storage Agreement', description: 'Storage space terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' },{ id: 'condominium', name: 'Condominium Bylaws', description: 'Applicable condo bylaws' }],
  terminationNotice: { tenantFixed: 'Ends on term date (no notice required unless periodic)', tenantMonthly: '1 calendar month (must be given before 1st of month)', tenantWeekly: '1 full tenancy week', landlordSubstantialBreach: '14 days', landlordDemolition: '365 days' },
};

const quebec = {
  name: 'Quebec', code: 'QC',
  legislation: 'Civil Code of Qu\u00e9bec (CCQ), articles 1851\u20132000', legislationShort: 'CCQ',
  regulator: 'Tribunal administratif du logement (TAL)', standardLeaseRequired: true, standardLeaseForm: 'Bail de logement (mandatory TAL form)',
  notes: ['Quebec REQUIRES the mandatory TAL lease form (Bail de logement) for dwellings.','Security deposits are PROHIBITED \u2014 only first month\'s rent can be collected.','Lease automatically renews unless tenant gives notice (3\u20136 months depending on term).','Landlord must disclose lowest rent paid in previous 12 months.'],
  rentRules: { maxDeposit: 'None \u2014 security deposits are prohibited', securityDepositAllowed: false, rentIncreaseGuideline: true, guidelineNote: 'TAL publishes annual guidelines. Tenant can refuse increase and landlord must apply to TAL to impose it.', postDatedCheques: false, postDatedNote: 'Cannot require post-dated cheques.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord (locateur) & Tenant (locataire) Names', required: true },{ id: 'address', label: 'Dwelling Address (logement)', required: true },{ id: 'term', label: 'Lease Term (dur\u00e9e du bail)', required: true },{ id: 'rent', label: 'Rent Amount & Payment Terms (loyer)', required: true },{ id: 'lowestRent', label: 'Lowest Rent Paid in Previous 12 Months', required: true },{ id: 'services', label: 'Services & Conditions Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Any security deposit or damage deposit','Clauses waiving tenant\'s rights under CCQ','Penalty clauses for exercising legal rights','Clauses giving landlord right to enter without notice/consent (except emergency)','No-children clauses (Charter of Human Rights and Freedoms)','Clauses limiting lease transfer (cession) rights'],
  schedules: [{ id: 'bylaw', name: 'Building Regulations', description: 'Rules for common areas, noise, etc.' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking space terms' },{ id: 'storage', name: 'Storage Agreement', description: 'Storage locker terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibility breakdown' },{ id: 'moveInInspection', name: 'Move-In Inspection Report', description: 'Unit condition at move-in' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions (can be restricted in Quebec)' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantFixed12Months: '3\u20136 months before end of term', tenantMonthly: '1\u20132 months before end', landlordRepossession: '6 months notice + conditions under CCQ', landlordRenovation: '6 months notice + right of first refusal' },
};

const manitoba = {
  name: 'Manitoba', code: 'MB',
  legislation: 'The Residential Tenancies Act, C.C.S.M. c. R119', legislationShort: 'MB RTA',
  regulator: 'Residential Tenancies Branch (RTB)', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['Manitoba does not mandate a standard lease form but written agreement is required.','Security deposit max is half of one month\'s rent.','Rent increases limited to annual guideline set by RTB.','Landlord must provide condition report at move-in.'],
  rentRules: { maxDeposit: 'Half month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: true, guidelineNote: 'Annual guideline set by Residential Tenancies Branch. 3 months\' notice required.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit (max half month)', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding half month\'s rent','Post-dated cheques requirement','Clauses contracting out of the RTA','No-children clauses'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Unit condition at move-in (required by law)' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month', tenantFixed: 'Ends on term date', landlordPersonalUse: '3 months' },
};

const saskatchewan = {
  name: 'Saskatchewan', code: 'SK',
  legislation: 'The Residential Tenancies Act, 2006, SS 2006, c. R-22.0002', legislationShort: 'SK RTA',
  regulator: 'Office of Residential Tenancies (ORT)', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['Saskatchewan does not have a mandatory standard lease form.','Written tenancy agreement is required.','Security deposit cannot exceed one month\'s rent.','No rent control for private market units.'],
  rentRules: { maxDeposit: 'One month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: false, guidelineNote: 'No rent control. Landlord must give 6 months\' written notice.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding one month\'s rent','Clauses contracting out of the Act','Seizure of tenant property','No-children clauses'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Move-in/move-out inspection' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions (can restrict)' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month', tenantFixed: 'Ends on term date', landlordNonPayment: '15 days' },
};

const novaScotia = {
  name: 'Nova Scotia', code: 'NS',
  legislation: 'Residential Tenancies Act, RSNS 1989, c. 401', legislationShort: 'NS RTA',
  regulator: 'Residential Tenancies Program', standardLeaseRequired: true, standardLeaseForm: 'Nova Scotia Standard Form of Lease',
  notes: ['Nova Scotia requires use of the Standard Form of Lease.','Security deposit max is half of one month\'s rent.','Temporary rent cap introduced (currently 5% max annual increase).','Landlord must provide condition report.'],
  rentRules: { maxDeposit: 'Half month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: true, guidelineNote: 'Temporary rent cap of 5% annually. 4 months\' notice required.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit (max half month)', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding half month\'s rent','Clauses contracting out of the Act','No-children clauses','Post-dated cheques requirement'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month', tenantFixed: 'Ends on term date', landlordPersonalUse: 'Varies' },
};

const newBrunswick = {
  name: 'New Brunswick', code: 'NB',
  legislation: 'Residential Tenancies Act, SNB 1975, c. R-10.2', legislationShort: 'NB RTA',
  regulator: 'Residential Tenancies Tribunal', standardLeaseRequired: true, standardLeaseForm: 'New Brunswick Standard Form of Lease',
  notes: ['New Brunswick requires use of the Standard Form of Lease.','Security deposit max is one month\'s rent.','No rent control \u2014 but notice required for increases.'],
  rentRules: { maxDeposit: 'One month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: false, guidelineNote: 'No rent control. Landlord must give notice for rent increase.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding one month\'s rent','Clauses contracting out of the Act','No-children clauses'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month', tenantFixed: 'Ends on term date' },
};

const pei = {
  name: 'Prince Edward Island', code: 'PE',
  legislation: 'Rental of Residential Property Act, RSNPEI 1988, c. R-13.1', legislationShort: 'RRPA',
  regulator: 'Island Regulatory and Appeals Commission (IRAC)', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['PEI does not mandate a standard lease form.','Security deposit max is one week\'s rent (weekly) or one month (monthly).','Rent increases require IRAC approval.'],
  rentRules: { maxDeposit: 'First and last month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: true, guidelineNote: 'Rent increases require IRAC approval. Annual allowable percentage published by IRAC.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Clauses contracting out of the Act','No-children clauses'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month (on or before 1st of month)', tenantFixed: 'Ends on term date' },
};

const newfoundland = {
  name: 'Newfoundland and Labrador', code: 'NL',
  legislation: 'Residential Tenancies Act, 2000, SNL 2000, c. R-14.1', legislationShort: 'NL RTA',
  regulator: 'Residential Tenancies Division, Service NL', standardLeaseRequired: false, standardLeaseForm: null,
  notes: ['NL does not mandate a standard lease form.','Security deposit max is 75% of one month\'s rent.','No rent control.'],
  rentRules: { maxDeposit: '75% of one month\'s rent', securityDepositAllowed: true, rentIncreaseGuideline: false, guidelineNote: 'No rent control. Landlord must give 6 months\' notice.', postDatedCheques: false, postDatedNote: 'Cannot be required.' },
  requiredClauses: [{ id: 'parties', label: 'Landlord & Tenant Names', required: true },{ id: 'address', label: 'Rental Unit Address', required: true },{ id: 'term', label: 'Tenancy Term', required: true },{ id: 'rent', label: 'Rent Amount & Due Date', required: true },{ id: 'securityDeposit', label: 'Security Deposit (max 75% of one month)', required: false },{ id: 'services', label: 'Services Included', required: true },{ id: 'additionalTerms', label: 'Additional Terms', required: false }],
  prohibitedClauses: ['Security deposit exceeding 75% of one month\'s rent','Clauses contracting out of the Act','No-children clauses'],
  schedules: [{ id: 'conditionReport', name: 'Condition Report', description: 'Move-in condition documentation' },{ id: 'petAgreement', name: 'Pet Agreement', description: 'Pet conditions' },{ id: 'parking', name: 'Parking Agreement', description: 'Parking terms' },{ id: 'utilities', name: 'Utilities Schedule', description: 'Utility responsibilities' },{ id: 'maintenance', name: 'Maintenance Schedule', description: 'Maintenance responsibilities' }],
  terminationNotice: { tenantMonthly: '1 month', tenantWeekly: '1 week', tenantFixed: 'Ends on term date' },
};

const provinces = { ON: ontario, BC: bc, AB: alberta, QC: quebec, MB: manitoba, SK: saskatchewan, NS: novaScotia, NB: newBrunswick, PE: pei, NL: newfoundland };
const provinceList = Object.values(provinces).sort((a, b) => a.name.localeCompare(b.name));


// ══════════════════════════════════════════════════════════════════════════════
// GENERATOR (inlined from generator.js — unchanged logic)
// ══════════════════════════════════════════════════════════════════════════════
// Loaded via separate script tag to keep bundle manageable


// ══════════════════════════════════════════════════════════════════════════════
// CLAUSE CHECKER
// ══════════════════════════════════════════════════════════════════════════════

const clausePatterns = {
  ON: [
    { pattern: /\bno\s+pets?\b|\bpets?\s+(not\s+)?allowed\b|\bpets?\s+prohibited\b/i, message: 'No-pet clauses are void and unenforceable in Ontario (RTA s.14)', severity: 'illegal' },
    { pattern: /\bsecurity\s+deposit\b|\bdamage\s+deposit\b/i, message: 'Security/damage deposits are prohibited in Ontario. Only last month\'s rent deposit is allowed (RTA s.105-106)', severity: 'illegal' },
    { pattern: /\bpost[\s-]?dated\s+cheque/i, message: 'Cannot require post-dated cheques in Ontario (RTA s.108)', severity: 'illegal' },
    { pattern: /\bguests?\s+(not\s+)?allowed\b|\bno\s+overnight\s+guests?\b|\brestrict.*guests?\b/i, message: 'Restricting guests/occupants is prohibited (RTA s.21)', severity: 'illegal' },
    { pattern: /\btenant\s+(shall|must|will)\s+(pay\s+for\s+)?all\s+repairs\b/i, message: 'Landlord must maintain the unit. Cannot shift all repair costs to tenant (RTA s.20)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\bno\s+families\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Ontario Human Rights Code)', severity: 'illegal' },
    { pattern: /\blandlord\s+may\s+enter\s+(at\s+)?any\s+time\b|\benter\s+without\s+notice\b/i, message: 'Landlord must give 24 hours written notice and enter between 8am-8pm only (RTA s.25-27)', severity: 'illegal' },
    { pattern: /\bno\s+subletting\b|\bno\s+assignment\b|\bcannot\s+(sublet|assign)\b/i, message: 'Cannot unreasonably refuse subletting or assignment (RTA s.95-98)', severity: 'warning' },
  ],
  BC: [
    { pattern: /\bsecurity\s+deposit.*(?:exceed|more\s+than|over).*half\b/i, message: 'Security deposit cannot exceed half month\'s rent (BC RTA s.19)', severity: 'illegal' },
    { pattern: /\bpost[\s-]?dated\s+cheque/i, message: 'Cannot require post-dated cheques in BC', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (BC Human Rights Code)', severity: 'illegal' },
    { pattern: /\blandlord\s+may\s+enter\s+(at\s+)?any\s+time\b/i, message: 'Landlord must give 24 hours written notice to enter (BC RTA s.29)', severity: 'illegal' },
  ],
  AB: [
    { pattern: /\bsecurity\s+deposit.*(?:exceed|more\s+than|over).*one\s+month\b/i, message: 'Security deposit cannot exceed one month\'s rent (Alberta RTRA s.46)', severity: 'illegal' },
    { pattern: /\bseiz(e|ure).*tenant.*property\b|\block\s*out\b/i, message: 'Seizure of tenant\'s property and lockouts are prohibited (Alberta RTRA)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Alberta Human Rights Act)', severity: 'illegal' },
  ],
  QC: [
    { pattern: /\bsecurity\s+deposit\b|\bdamage\s+deposit\b|\bkey\s+deposit\b/i, message: 'ALL deposits are prohibited in Quebec (CCQ art. 1904)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Quebec Charter)', severity: 'illegal' },
    { pattern: /\blandlord\s+may\s+enter\b|\benter\s+without\b/i, message: 'Landlord cannot enter without consent except in emergency (CCQ art. 1857)', severity: 'illegal' },
    { pattern: /\bno\s+(sublet|assignment|cession)\b|\bcannot\s+(sublet|assign|cede)\b/i, message: 'Cannot prohibit lease assignment (cession) (CCQ art. 1870-1871)', severity: 'illegal' },
  ],
};

const universalPatterns = [
  { pattern: /\bno\s+children\b|\bno\s+families\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited under Canadian human rights legislation', severity: 'illegal' },
  { pattern: /\bwaiv(e|ing)\s+(all\s+)?rights?\b/i, message: 'Clauses that waive statutory tenant rights are void and unenforceable', severity: 'warning' },
];

function checkClause(text, provinceCode) {
  if (!text || text.length < 5) return [];
  const results = [];
  const patterns = [...(clausePatterns[provinceCode] || []), ...universalPatterns];
  for (const rule of patterns) {
    const match = text.match(rule.pattern);
    if (match && !results.find(r => r.message === rule.message)) {
      results.push({ severity: rule.severity, message: rule.message });
    }
  }
  return results;
}

function renderClauseWarnings(warnings) {
  if (!warnings.length) return '';
  return warnings.map(w => {
    const icon = w.severity === 'illegal' ? '&#9888;' : '&#9432;';
    const cls = w.severity === 'illegal' ? 'clause-illegal' : w.severity === 'warning' ? 'clause-warning' : 'clause-info';
    const label = w.severity === 'illegal' ? 'ILLEGAL' : 'WARNING';
    return '<div class="clause-alert ' + cls + '"><span>' + icon + '</span> <strong>' + label + ':</strong> ' + w.message + '</div>';
  }).join('');
}


// ══════════════════════════════════════════════════════════════════════════════
// SIGNATURE PAD
// ══════════════════════════════════════════════════════════════════════════════

class SignaturePad {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.drawing = false;
    this.paths = [];
    this.currentPath = [];
    this.resize();
    this.setupEvents();
  }
  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = 120 * dpr;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = '120px';
    this.ctx.scale(dpr, dpr);
    this.ctx.strokeStyle = '#1a1a1a'; this.ctx.lineWidth = 2;
    this.ctx.lineCap = 'round'; this.ctx.lineJoin = 'round';
    this.redraw();
  }
  setupEvents() {
    const getPos = (e) => { const r = this.canvas.getBoundingClientRect(); const t = e.touches ? e.touches[0] : e; return { x: t.clientX - r.left, y: t.clientY - r.top }; };
    const start = (e) => { e.preventDefault(); this.drawing = true; this.currentPath = [getPos(e)]; };
    const move = (e) => { if (!this.drawing) return; e.preventDefault(); const pos = getPos(e); this.currentPath.push(pos); if (this.currentPath.length > 1) { this.ctx.beginPath(); const p = this.currentPath[this.currentPath.length - 2]; this.ctx.moveTo(p.x, p.y); this.ctx.lineTo(pos.x, pos.y); this.ctx.stroke(); } };
    const end = () => { if (this.drawing && this.currentPath.length > 1) this.paths.push([...this.currentPath]); this.drawing = false; this.currentPath = []; };
    this.canvas.addEventListener('mousedown', start); this.canvas.addEventListener('mousemove', move);
    this.canvas.addEventListener('mouseup', end); this.canvas.addEventListener('mouseleave', end);
    this.canvas.addEventListener('touchstart', start, { passive: false }); this.canvas.addEventListener('touchmove', move, { passive: false }); this.canvas.addEventListener('touchend', end);
    window.addEventListener('resize', () => this.resize());
  }
  redraw() {
    const dpr = window.devicePixelRatio || 1; const w = this.canvas.width / dpr; const h = this.canvas.height / dpr;
    this.ctx.clearRect(0, 0, w, h);
    this.ctx.save(); this.ctx.strokeStyle = '#ddd'; this.ctx.lineWidth = 1; this.ctx.setLineDash([4, 4]);
    this.ctx.beginPath(); this.ctx.moveTo(10, h - 20); this.ctx.lineTo(w - 10, h - 20); this.ctx.stroke(); this.ctx.restore();
    this.ctx.strokeStyle = '#1a1a1a'; this.ctx.lineWidth = 2; this.ctx.setLineDash([]);
    for (const path of this.paths) { if (path.length < 2) continue; this.ctx.beginPath(); this.ctx.moveTo(path[0].x, path[0].y); for (let i = 1; i < path.length; i++) this.ctx.lineTo(path[i].x, path[i].y); this.ctx.stroke(); }
  }
  clear() { this.paths = []; this.currentPath = []; this.redraw(); }
  isEmpty() { return this.paths.length === 0; }
  toDataURL() { return this.canvas.toDataURL('image/png'); }
}

function createSignatureSection() {
  return '<div class="signature-section"><h3>Digital Signatures</h3><p class="sig-instructions">Sign below using your mouse or touchscreen. Signatures will be embedded in the exported PDF.</p><div class="sig-pads"><div class="sig-pad-group"><label>Landlord Signature</label><div class="sig-pad-wrapper"><canvas id="sig-landlord" class="sig-canvas"></canvas></div><div class="sig-pad-actions"><button class="btn btn-sm btn-secondary" data-clear="sig-landlord">Clear</button><input type="text" id="sig-landlord-typed" class="sig-typed-input" placeholder="Or type your name to sign"></div></div><div class="sig-pad-group"><label>Tenant Signature</label><div class="sig-pad-wrapper"><canvas id="sig-tenant" class="sig-canvas"></canvas></div><div class="sig-pad-actions"><button class="btn btn-sm btn-secondary" data-clear="sig-tenant">Clear</button><input type="text" id="sig-tenant-typed" class="sig-typed-input" placeholder="Or type your name to sign"></div></div></div></div>';
}


// ══════════════════════════════════════════════════════════════════════════════
// RIGHTS SIDEBAR
// ══════════════════════════════════════════════════════════════════════════════

const rightsData = {
  ON: { title: 'Ontario Tenant Rights', legislation: 'Residential Tenancies Act, 2006 + Bill 60 (2025)', rights: [
    { title: 'Standard Lease', text: 'Landlord must provide the Ontario Standard Lease within 21 days of your written request. If they refuse, you can withhold one month\'s rent.', section: 'O. Reg. 9/18' },
    { title: 'No-Pet Clauses Void', text: 'No-pet clauses are void and unenforceable. However, you can be evicted if your pet causes damage, noise, or allergic reactions.', section: 'RTA s.14' },
    { title: 'Deposits', text: 'Only a last month\'s rent deposit is allowed. No security deposits, damage deposits, or key deposits exceeding replacement cost.', section: 'RTA s.105-109' },
    { title: 'Rent Increases', text: 'Limited to the annual guideline (2.5% for 2025). Units first occupied after Nov 15, 2018 are exempt.', section: 'RTA s.116-120' },
    { title: 'Maintenance', text: 'Landlord must keep the unit in good repair and comply with health/safety standards.', section: 'RTA s.20' },
    { title: 'Entry Rights', text: 'Landlord must give 24 hours written notice and can only enter between 8am-8pm, except emergencies.', section: 'RTA s.25-27' },
    { title: 'Eviction Protection', text: 'You can only be evicted through the LTB process. Lockouts and self-help evictions are illegal.', section: 'RTA s.39' },
  ]},
  BC: { title: 'BC Tenant Rights', legislation: 'Residential Tenancy Act, SBC 2002, c. 78', rights: [
    { title: 'Deposits', text: 'Security deposit: max half month\'s rent. Pet damage deposit: additional half month. Both returned within 15 days if condition report done.', section: 'RTA s.19-20' },
    { title: 'Condition Reports', text: 'Landlord MUST do a move-in and move-out condition inspection or loses right to claim deposit.', section: 'RTA s.23-24' },
    { title: 'Rent Increases', text: 'Limited to annual allowable amount set by RTB. 3 months notice required.', section: 'RTA s.42-43' },
    { title: 'Entry', text: '24 hours written notice required. Entry only between 8am-9pm.', section: 'RTA s.29' },
  ]},
  AB: { title: 'Alberta Tenant Rights', legislation: 'Residential Tenancies Act, RSA 2004', rights: [
    { title: 'Deposits', text: 'Max one month\'s rent. Must be held in trust with interest.', section: 'RTRA s.46' },
    { title: 'No Rent Control', text: 'No rent control but proper notice (3+ months) required and only one increase per year.', section: 'RTRA s.54' },
    { title: 'No Lockouts', text: 'Self-help evictions and lockouts are illegal. Must go through RTDRS.', section: 'RTRA s.24' },
  ]},
  QC: { title: 'Quebec Tenant Rights', legislation: 'Civil Code of Quebec, arts. 1851-2000', rights: [
    { title: 'No Deposits', text: 'ALL deposits are prohibited in Quebec. Only first month\'s rent in advance.', section: 'CCQ art. 1904' },
    { title: 'Automatic Renewal', text: 'Your lease renews automatically. Landlord must give formal notice to modify terms.', section: 'CCQ art. 1941' },
    { title: 'Rent Disclosure', text: 'Landlord must disclose the lowest rent paid in the previous 12 months.', section: 'CCQ art. 1896' },
    { title: 'Assignment Rights', text: 'You have the right to assign (cede) your lease. Landlord can only refuse for serious reasons.', section: 'CCQ art. 1870-1871' },
    { title: 'Entry', text: 'Landlord cannot enter without your consent except in emergency.', section: 'CCQ art. 1857' },
  ]},
  MB: { title: 'Manitoba Tenant Rights', legislation: 'Residential Tenancies Act, C.C.S.M. c. R119', rights: [
    { title: 'Deposits', text: 'Max half month\'s rent. Must be held in trust.', section: 'RTA s.41' },
    { title: 'Rent Increases', text: 'Limited by annual guideline. 3 months notice required.', section: 'RTA s.31' },
  ]},
  SK: { title: 'Saskatchewan Tenant Rights', legislation: 'Residential Tenancies Act, 2006', rights: [
    { title: 'Deposits', text: 'Max one month\'s rent. Must be held in trust with interest.', section: 'RTA s.25' },
    { title: 'No Rent Control', text: '6 months written notice required for increases.', section: 'RTA s.55' },
  ]},
  NS: { title: 'Nova Scotia Tenant Rights', legislation: 'Residential Tenancies Act, RSNS 1989', rights: [
    { title: 'Deposits', text: 'Max half month\'s rent.', section: 'RTA s.12' },
    { title: 'Rent Cap', text: 'Temporary rent cap of 5% per year. 4 months notice required.', section: 'Emergency measures' },
  ]},
  NB: { title: 'New Brunswick Tenant Rights', legislation: 'Residential Tenancies Act, SNB 1975', rights: [{ title: 'Deposits', text: 'Max one month\'s rent.', section: 'RTA s.10' }]},
  PE: { title: 'PEI Tenant Rights', legislation: 'Rental of Residential Property Act', rights: [{ title: 'Rent Increases', text: 'Require IRAC approval.', section: 'RRPA s.25' }]},
  NL: { title: 'NL Tenant Rights', legislation: 'Residential Tenancies Act, 2000', rights: [{ title: 'Deposits', text: 'Max 75% of one month\'s rent.', section: 'RTA s.14' }]},
};

function renderRightsSidebar(code) {
  const d = rightsData[code]; if (!d) return '';
  return '<div class="rights-header"><h3>' + d.title + '</h3><p class="rights-legislation">' + d.legislation + '</p></div><div class="rights-list">' +
    d.rights.map(function(r) { return '<details class="rights-item"><summary><strong>' + r.title + '</strong><span class="rights-section">' + r.section + '</span></summary><p>' + r.text + '</p></details>'; }).join('') + '</div>';
}


// ══════════════════════════════════════════════════════════════════════════════
// TIMELINE
// ══════════════════════════════════════════════════════════════════════════════

function generateTimeline(formData, province) {
  if (!formData.startDate) return '';
  var start = new Date(formData.startDate + 'T00:00:00');
  var events = [];
  events.push({ date: start, label: 'Move-In Date', type: 'primary', desc: 'Tenancy begins' });
  var firstRent = new Date(start);
  if (formData.rentDueDay === '1st') { firstRent.setMonth(firstRent.getMonth() + (firstRent.getDate() === 1 ? 0 : 1)); firstRent.setDate(1); }
  events.push({ date: firstRent, label: 'First Rent Payment', type: 'info', desc: '$' + formData.rentAmount + ' due' });
  if (formData.termType === 'fixed' && formData.endDate) {
    var end = new Date(formData.endDate + 'T00:00:00');
    events.push({ date: end, label: 'Lease End Date', type: 'danger', desc: 'Fixed term expires' });
    var nd = new Date(end);
    if (['ON', 'MB'].includes(province.code)) { nd.setDate(nd.getDate() - 60); events.push({ date: nd, label: 'Tenant Notice Deadline', type: 'warning', desc: '60 days before end' }); }
    else if (province.code === 'BC') { nd.setMonth(nd.getMonth() - 1); events.push({ date: nd, label: 'Tenant Notice Deadline', type: 'warning', desc: '1 month before end' }); }
  }
  if (province.rentRules.rentIncreaseGuideline) {
    var inc = new Date(start); inc.setFullYear(inc.getFullYear() + 1);
    events.push({ date: inc, label: 'Earliest Rent Increase', type: 'info', desc: '12 months from start' });
  }
  events.sort(function(a, b) { return a.date - b.date; });
  var fmt = function(d) { return d.toLocaleDateString('en-CA', { year: 'numeric', month: 'short', day: 'numeric' }); };
  return '<div class="timeline"><h3 class="timeline-title">Lease Timeline</h3><div class="timeline-track">' +
    events.map(function(e) { return '<div class="timeline-event timeline-' + e.type + '"><div class="timeline-dot"></div><div class="timeline-content"><div class="timeline-date">' + fmt(e.date) + '</div><div class="timeline-label">' + e.label + '</div><div class="timeline-desc">' + e.desc + '</div></div></div>'; }).join('') + '</div></div>';
}


// ══════════════════════════════════════════════════════════════════════════════
// I18N
// ══════════════════════════════════════════════════════════════════════════════

var i18nTranslations = {
  en: { 'app.name': 'LeaseCreate', 'app.tagline': 'Provincial lease agreements made simple', 'app.privacy': 'Private \u2014 nothing leaves your browser', 'hero.title.pre': 'Create a ', 'hero.title.highlight': 'Legally Compliant', 'hero.title.post': ' Lease', 'hero.subtitle': "Generate a residential tenancy agreement tailored to your province\u2019s legislation. Add schedules, review prohibited clauses, and export to PDF \u2014 all in your browser.", 'hero.provinces': 'Provinces', 'hero.schedules': 'Schedules', 'hero.free': 'Free & Private', 'step.1': 'Province & Parties', 'step.2': 'Rental Unit', 'step.3': 'Term & Rent', 'step.4': 'Rules & Details', 'step.5': 'Schedules', 'step.6': 'Preview & Export', 'step1.title': 'Province & Parties', 'step1.desc': 'Select your province and enter landlord/tenant information.', 'step1.province': 'Province', 'step1.landlord': 'Landlord Information', 'step1.landlord.name': 'Full Legal Name', 'step1.landlord.email': 'Email', 'step1.landlord.address': 'Mailing Address', 'step1.landlord.phone': 'Phone', 'step1.tenant': 'Tenant Information', 'step1.tenant.name': 'Full Legal Name', 'step1.tenant.email': 'Email', 'step1.tenant.phone': 'Phone', 'step1.tenant.additional': 'Additional Tenant(s)', 'step2.title': 'Rental Unit Details', 'step2.desc': 'Describe the property being rented.', 'step2.address': 'Street Address', 'step2.unit': 'Unit / Suite #', 'step2.city': 'City', 'step2.postal': 'Postal Code', 'step2.type': 'Unit Type', 'step2.furnished': 'Furnished', 'step2.parking': 'Parking included', 'step2.storage': 'Storage locker included', 'step3.title': 'Tenancy Term & Rent', 'step3.desc': 'Set the lease term, rent amount, and deposit details.', 'step3.fixed': 'Fixed Term (e.g., 1 year)', 'step3.monthly': 'Month-to-Month (Periodic)', 'step3.start': 'Start Date', 'step3.end': 'End Date', 'step3.rent': 'Monthly Rent ($)', 'step3.due': 'Due Day', 'step3.method': 'Payment Method', 'step3.deposits': 'Deposits', 'step4.title': 'Rules, Utilities & Details', 'step4.desc': 'Set house rules, utility responsibilities, and additional terms.', 'step4.smoking': 'Smoking permitted', 'step4.pets': 'Pets permitted', 'step4.insurance': 'Tenant insurance required', 'step4.guest': 'Guest Policy', 'step4.noise': 'Quiet Hours', 'step4.utilities': 'Utilities Included in Rent', 'step4.maintenance': 'Maintenance Notes', 'step4.additional': 'Additional Terms', 'step5.title': 'Schedules (Additional Agreements)', 'step5.desc': 'Select any additional schedules to attach to the lease.', 'step6.title': 'Preview & Export', 'step6.desc': 'Review your lease agreement and export to PDF.', 'step6.export': 'Export as PDF', 'step6.edit': 'Edit Details', 'step6.regenerate': 'Regenerate Preview', 'btn.generate': 'Generate Lease', 'rights.toggle': 'Know Your Rights', 'templates.title': 'Start from a Template', 'drafts.load': 'Saved Drafts', 'footer.disclaimer': 'LeaseCreate generates lease templates for informational purposes only. This is not legal advice.', 'footer.privacy': '100% client-side \u2014 your data never leaves your browser.' },
  fr: { 'app.name': 'LeaseCreate', 'app.tagline': 'Baux provinciaux simplifi\u00e9s', 'app.privacy': 'Priv\u00e9 \u2014 rien ne quitte votre navigateur', 'hero.title.pre': 'Cr\u00e9ez un bail ', 'hero.title.highlight': 'conforme \u00e0 la loi', 'hero.title.post': '', 'hero.subtitle': "G\u00e9n\u00e9rez un bail d\u2019habitation adapt\u00e9 \u00e0 la l\u00e9gislation de votre province.", 'hero.provinces': 'Provinces', 'hero.schedules': 'Annexes', 'hero.free': 'Gratuit et priv\u00e9', 'step.1': 'Province et parties', 'step.2': 'Logement', 'step.3': 'Dur\u00e9e et loyer', 'step.4': 'R\u00e8gles et d\u00e9tails', 'step.5': 'Annexes', 'step.6': 'Aper\u00e7u et export', 'step1.title': 'Province et parties', 'step1.desc': 'S\u00e9lectionnez votre province et entrez les informations.', 'step1.province': 'Province', 'step1.landlord': 'Information du locateur', 'step1.landlord.name': 'Nom l\u00e9gal complet', 'step1.landlord.email': 'Courriel', 'step1.landlord.address': 'Adresse postale', 'step1.landlord.phone': 'T\u00e9l\u00e9phone', 'step1.tenant': 'Information du locataire', 'step1.tenant.name': 'Nom l\u00e9gal complet', 'step1.tenant.email': 'Courriel', 'step1.tenant.phone': 'T\u00e9l\u00e9phone', 'step1.tenant.additional': 'Locataire(s) additionnel(s)', 'step2.title': 'D\u00e9tails du logement', 'step2.desc': 'D\u00e9crivez la propri\u00e9t\u00e9 lou\u00e9e.', 'step2.address': 'Adresse civique', 'step2.unit': 'Unit\u00e9 / Appt #', 'step2.city': 'Ville', 'step2.postal': 'Code postal', 'step2.type': 'Type de logement', 'step2.furnished': 'Meubl\u00e9', 'step2.parking': 'Stationnement inclus', 'step2.storage': 'Casier inclus', 'step3.title': 'Dur\u00e9e du bail et loyer', 'step3.desc': 'D\u00e9finissez la dur\u00e9e et le montant du loyer.', 'step3.fixed': 'Dur\u00e9e d\u00e9termin\u00e9e (ex. 1 an)', 'step3.monthly': 'Mois par mois', 'step3.start': 'Date de d\u00e9but', 'step3.end': 'Date de fin', 'step3.rent': 'Loyer mensuel ($)', 'step3.due': "Jour d'\u00e9ch\u00e9ance", 'step3.method': 'Mode de paiement', 'step3.deposits': 'D\u00e9p\u00f4ts', 'step4.title': 'R\u00e8gles, services et d\u00e9tails', 'step4.desc': 'D\u00e9finissez les r\u00e8gles et conditions.', 'step4.smoking': 'Tabagisme permis', 'step4.pets': 'Animaux permis', 'step4.insurance': 'Assurance locataire requise', 'step4.guest': 'Politique invit\u00e9s', 'step4.noise': 'Heures de tranquillit\u00e9', 'step4.utilities': 'Services inclus dans le loyer', 'step4.maintenance': "Notes d'entretien", 'step4.additional': 'Conditions suppl\u00e9mentaires', 'step5.title': 'Annexes (ententes additionnelles)', 'step5.desc': 'S\u00e9lectionnez les annexes \u00e0 joindre au bail.', 'step6.title': 'Aper\u00e7u et exportation', 'step6.desc': 'R\u00e9visez votre bail et exportez en PDF.', 'step6.export': 'Exporter en PDF', 'step6.edit': 'Modifier', 'step6.regenerate': "R\u00e9g\u00e9n\u00e9rer l'aper\u00e7u", 'btn.generate': 'G\u00e9n\u00e9rer le bail', 'rights.toggle': 'Connaissez vos droits', 'templates.title': "Commencer \u00e0 partir d'un mod\u00e8le", 'drafts.load': 'Brouillons sauvegard\u00e9s', 'footer.disclaimer': "LeaseCreate g\u00e9n\u00e8re des mod\u00e8les de bail \u00e0 titre informatif. Consultez un avocat.", 'footer.privacy': '100% c\u00f4t\u00e9 client \u2014 vos donn\u00e9es ne quittent jamais votre navigateur.' },
};

var currentLang = 'en';
function setLanguage(lang) { currentLang = lang; applyTranslations(); }
function getLanguage() { return currentLang; }
function t(key) { return (i18nTranslations[currentLang] && i18nTranslations[currentLang][key]) || i18nTranslations.en[key] || key; }
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.dataset.i18n; var text = t(key); if (!text) return;
    if (el.children.length === 0) { el.textContent = text; }
    else { var w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null); var n = w.nextNode(); if (n) n.textContent = text; }
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(function(el) {
    var key = el.dataset.i18nPlaceholder; var text = t(key); if (text) el.placeholder = text;
  });
  document.documentElement.lang = currentLang;
}


// ══════════════════════════════════════════════════════════════════════════════
// DRAFTS
// ══════════════════════════════════════════════════════════════════════════════

var DRAFT_KEY = 'leaseCreate_drafts';
function saveDraft(name, data) { var d = getAllDrafts(); d[name] = { data: data, savedAt: new Date().toISOString() }; localStorage.setItem(DRAFT_KEY, JSON.stringify(d)); }
function loadDraft(name) { var d = getAllDrafts(); return d[name] ? d[name].data : null; }
function deleteDraft(name) { var d = getAllDrafts(); delete d[name]; localStorage.setItem(DRAFT_KEY, JSON.stringify(d)); }
function getAllDrafts() { try { return JSON.parse(localStorage.getItem(DRAFT_KEY) || '{}'); } catch(e) { return {}; } }
function getDraftList() { var d = getAllDrafts(); return Object.entries(d).filter(function(e){return e[0]!=='__autosave__';}).map(function(e) { return { name: e[0], savedAt: e[1].savedAt }; }).sort(function(a,b){ return new Date(b.savedAt) - new Date(a.savedAt); }); }
function hasAutoSave() { return !!getAllDrafts().__autosave__; }
function getAutoSave() { return loadDraft('__autosave__'); }
var autoSaveInterval = null;
function startAutoSave(fn) { if (autoSaveInterval) clearInterval(autoSaveInterval); autoSaveInterval = setInterval(function(){ try { var d = fn(); if (d && d.province) saveDraft('__autosave__', d); } catch(e){} }, 30000); }

function renderDraftManager() {
  var drafts = getDraftList();
  var list = drafts.length === 0 ? '<p class="drafts-empty">No saved drafts yet.</p>' :
    drafts.map(function(d) { return '<div class="draft-item"><div class="draft-info"><strong>' + escH(d.name) + '</strong><span>' + new Date(d.savedAt).toLocaleString() + '</span></div><div class="draft-actions"><button class="btn btn-sm btn-primary draft-load" data-draft="' + escH(d.name) + '">Load</button><button class="btn btn-sm btn-danger draft-delete" data-draft="' + escH(d.name) + '">Delete</button></div></div>'; }).join('');
  return '<div class="drafts-panel"><div class="drafts-save"><input type="text" id="draftName" class="draft-name-input" placeholder="Name this draft..."><button class="btn btn-sm btn-primary" id="btn-save-draft">Save Draft</button></div><div class="drafts-list" id="drafts-list">' + list + '</div></div>';
}


// ══════════════════════════════════════════════════════════════════════════════
// TEMPLATES
// ══════════════════════════════════════════════════════════════════════════════

var templates = [
  { id: 'standard-apartment', name: 'Standard Apartment', description: 'Typical 1-year apartment lease', icon: '&#127970;', data: { termType: 'fixed', unitType: 'Apartment', isFurnished: false, parkingIncluded: false, storageIncluded: false, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, petsAllowed: false, tenantInsuranceRequired: true, noisePolicy: '10 PM to 8 AM', utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' } } },
  { id: 'condo-rental', name: 'Condo Rental', description: 'Condo with amenities and parking', icon: '&#127959;', data: { termType: 'fixed', unitType: 'Condo', isFurnished: false, parkingIncluded: true, storageIncluded: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, petsAllowed: false, tenantInsuranceRequired: true, noisePolicy: '10 PM to 7 AM', utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'included' } } },
  { id: 'pet-friendly', name: 'Pet-Friendly', description: 'Includes pet agreement', icon: '&#128054;', data: { termType: 'fixed', unitType: 'Apartment', petsAllowed: true, tenantInsuranceRequired: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, noisePolicy: '10 PM to 8 AM', utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' } } },
  { id: 'furnished-short', name: 'Furnished Short-Term', description: 'All utilities included', icon: '&#128717;', data: { termType: 'fixed', unitType: 'Apartment', isFurnished: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, petsAllowed: false, tenantInsuranceRequired: true, guestPolicy: 'Guests may stay up to 7 days', noisePolicy: '10 PM to 8 AM', utilities: { heat: 'included', water: 'included', electricity: 'included', internet: 'included', cabletv: 'included', laundry: 'included', airconditioning: 'included' } } },
  { id: 'house-rental', name: 'Whole House', description: 'House with yard maintenance', icon: '&#127968;', data: { termType: 'fixed', unitType: 'House', parkingIncluded: true, parkingDetails: 'Driveway \u2014 2 vehicles', petsAllowed: true, tenantInsuranceRequired: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, noisePolicy: '11 PM to 7 AM', maintenanceNotes: 'Tenant responsible for lawn care and snow removal.', utilities: { heat: 'tenant', water: 'tenant', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'tenant' } } },
  { id: 'room-shared', name: 'Room in Shared Dwelling', description: 'Single room, shared areas', icon: '&#128719;', data: { termType: 'monthly', unitType: 'Room', isFurnished: true, petsAllowed: false, tenantInsuranceRequired: false, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, noisePolicy: '10 PM to 8 AM', guestPolicy: 'Guests must be approved for stays over 3 nights', utilities: { heat: 'included', water: 'included', electricity: 'included', internet: 'included', cabletv: 'included', laundry: 'included', airconditioning: 'included' } } },
  { id: 'month-to-month', name: 'Month-to-Month', description: 'Flexible periodic tenancy', icon: '&#128197;', data: { termType: 'monthly', unitType: 'Apartment', tenantInsuranceRequired: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, petsAllowed: false, noisePolicy: '10 PM to 8 AM', utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' } } },
  { id: 'basement-unit', name: 'Basement Apartment', description: 'Separate entrance, shared laundry', icon: '&#127978;', data: { termType: 'fixed', unitType: 'Basement', parkingIncluded: true, parkingDetails: '1 driveway spot', tenantInsuranceRequired: true, rentDueDay: '1st', paymentMethod: 'E-transfer', smokingAllowed: false, petsAllowed: false, noisePolicy: '10 PM to 8 AM', utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'tenant' } } },
];

function renderTemplateSelector() {
  return '<div class="template-grid">' + templates.map(function(t) {
    return '<div class="template-card" data-template="' + t.id + '"><div class="template-icon">' + t.icon + '</div><div class="template-info"><strong>' + t.name + '</strong><span>' + t.description + '</span></div></div>';
  }).join('') + '</div>';
}
function getTemplate(id) { return templates.find(function(t) { return t.id === id; }); }


// ══════════════════════════════════════════════════════════════════════════════
// LEASESCAN IMPORT
// ══════════════════════════════════════════════════════════════════════════════

function parseLeaseText(text) {
  var r = {};
  var m;
  if ((m = text.match(/landlord[:\s]+([A-Z][a-zA-Z\s.']+?)(?:\n|,|\()/i))) r.landlordName = m[1].trim();
  if ((m = text.match(/tenant[:\s]+([A-Z][a-zA-Z\s.']+?)(?:\n|,|\()/i))) r.tenantName = m[1].trim();
  if ((m = text.match(/[A-Z]\d[A-Z]\s?\d[A-Z]\d/))) r.postalCode = m[0].trim();
  if ((m = text.match(/(?:rent|monthly\s+rent|loyer)[:\s]*\$?\s*([\d,]+\.?\d*)/i))) r.rentAmount = m[1].replace(/,/g, '');
  if (/month[\s-]to[\s-]month|periodic/i.test(text)) r.termType = 'monthly';
  else if (/fixed\s+term|one\s+year/i.test(text)) r.termType = 'fixed';
  if (/pets?\s+(are\s+)?permitted|pets?\s+allowed/i.test(text)) r.petsAllowed = true;
  if (/no\s+smoking|smoke[\s-]?free/i.test(text)) r.smokingAllowed = false;
  if (/furnished/i.test(text) && !/unfurnished/i.test(text)) r.isFurnished = true;
  return r;
}

function renderImportSection() {
  return '<div class="import-section"><h4>Import from Existing Lease</h4><div class="import-options"><button class="btn btn-sm btn-secondary" id="btn-import-paste">Paste Lease Text</button></div></div>';
}


// ══════════════════════════════════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════════════════════════════════

function escH(str) { return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

function showToast(message) {
  var existing = document.querySelector('.toast');
  if (existing) existing.remove();
  var toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(function() { toast.classList.add('show'); });
  setTimeout(function() { toast.classList.remove('show'); setTimeout(function() { toast.remove(); }, 300); }, 2500);
}


// ══════════════════════════════════════════════════════════════════════════════
// MAIN APPLICATION
// ══════════════════════════════════════════════════════════════════════════════

var $ = function(sel) { return document.querySelector(sel); };
var $$ = function(sel) { return document.querySelectorAll(sel); };

var currentProvince = null;
var selectedSchedules = [];
var sigPadLandlord = null;
var sigPadTenant = null;

// ══════════════════════════════════════════════════════════════════════════════
// GENERATOR
// ══════════════════════════════════════════════════════════════════════════════

function escG(str) { if (!str) return ''; return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function formatKey(key) { return key.replace(/([A-Z])/g,' $1').replace(/^./,function(s){return s.toUpperCase();}); }
function buildUtilityRow(name, utilities) { var included = utilities && utilities[name.toLowerCase().replace(/\s|\//g,'')] === 'included'; return '<tr><td>'+name+'</td><td>'+(included?'Yes':'')+'</td><td>'+(included?'':'Yes')+'</td></tr>'; }

function generateLease(formData, selectedSchedules) {
  var province = provinces[formData.province];
  if (!province) return '<p>Please select a province.</p>';
  var today = new Date().toLocaleDateString('en-CA', {year:'numeric',month:'long',day:'numeric'});
  var html = '';

  html += '<div class="lease-header"><h1>RESIDENTIAL TENANCY AGREEMENT</h1><p class="lease-subtitle">Province of '+province.name+'</p><p class="lease-legislation">Governed by: '+province.legislation+'</p>'+(province.standardLeaseRequired?'<p class="lease-note">Note: '+province.standardLeaseForm+' is required in '+province.name+'. This document supplements — it does not replace — the official form.</p>':'')+'<p class="lease-date">Date: '+today+'</p></div>';

  html += '<div class="lease-section"><h2>1. PARTIES</h2><div class="lease-field-group"><div class="lease-field"><label>LANDLORD</label><p><strong>'+escG(formData.landlordName)+'</strong></p>'+(formData.landlordAddress?'<p>'+escG(formData.landlordAddress)+'</p>':'')+(formData.landlordPhone?'<p>Phone: '+escG(formData.landlordPhone)+'</p>':'')+(formData.landlordEmail?'<p>Email: '+escG(formData.landlordEmail)+'</p>':'')+'</div><div class="lease-field"><label>TENANT</label><p><strong>'+escG(formData.tenantName)+'</strong></p>'+(formData.tenantPhone?'<p>Phone: '+escG(formData.tenantPhone)+'</p>':'')+(formData.tenantEmail?'<p>Email: '+escG(formData.tenantEmail)+'</p>':'')+'</div>'+(formData.additionalTenants?'<div class="lease-field full-width"><label>Additional Tenant(s)</label><p>'+escG(formData.additionalTenants)+'</p></div>':'')+'</div></div>';

  html += '<div class="lease-section"><h2>2. RENTAL UNIT</h2><p><strong>Address:</strong> '+escG(formData.unitAddress)+'</p>'+(formData.unitNumber?'<p><strong>Unit/Suite:</strong> '+escG(formData.unitNumber)+'</p>':'')+'<p><strong>City:</strong> '+escG(formData.city)+', <strong>Province:</strong> '+province.name+', <strong>Postal Code:</strong> '+escG(formData.postalCode)+'</p>'+(formData.unitType?'<p><strong>Type:</strong> '+escG(formData.unitType)+'</p>':'')+(formData.isFurnished?'<p><strong>Furnished:</strong> Yes</p>':'')+(formData.parkingIncluded?'<p><strong>Parking:</strong> Included'+(formData.parkingDetails?' — '+escG(formData.parkingDetails):'')+'</p>':'')+(formData.storageIncluded?'<p><strong>Storage:</strong> Included</p>':'')+'</div>';

  html += '<div class="lease-section lease-section-term"><h2>3. TERM OF TENANCY</h2><p><strong>Type:</strong> '+(formData.termType==='fixed'?'Fixed Term':'Month-to-Month (Periodic)')+'</p><p><strong>Start Date:</strong> '+escG(formData.startDate)+'</p>'+(formData.termType==='fixed'?'<p><strong>End Date:</strong> '+escG(formData.endDate)+'</p>':'')+'<p class="lease-info">Termination notice requirements per '+province.legislationShort+':</p><ul>'+Object.entries(province.terminationNotice).map(function(e){return '<li>'+formatKey(e[0])+': '+e[1]+'</li>';}).join('')+'</ul></div>';

  html += '<div class="lease-section"><h2>4. RENT</h2><p><strong>Monthly Rent:</strong> $'+escG(formData.rentAmount)+'</p><p><strong>Due Date:</strong> '+escG(formData.rentDueDay)+' of each month</p><p><strong>Payment Method:</strong> '+escG(formData.paymentMethod||'As agreed between parties')+'</p>'+(province.rentRules.rentIncreaseGuideline?'<p class="lease-info">Rent increases: '+province.rentRules.guidelineNote+'</p>':'<p class="lease-info">Note: '+province.rentRules.guidelineNote+'</p>')+'</div>';

  html += '<div class="lease-section"><h2>5. DEPOSITS</h2>';
  if (!province.rentRules.securityDepositAllowed && province.code !== 'ON') {
    html += '<p class="lease-warning">Security deposits are <strong>prohibited</strong> in '+province.name+'.</p>'+(province.code==='QC'?'<p>Only the first month\'s rent may be collected in advance.</p>':'');
  } else if (province.code === 'ON') {
    html += '<p><strong>Last Month\'s Rent Deposit:</strong> $'+escG(formData.lastMonthDeposit||formData.rentAmount)+'</p><p class="lease-info">Ontario prohibits security deposits. Only a last month\'s rent deposit is allowed (RTA s.106).</p>';
  } else {
    html += '<p><strong>Security Deposit:</strong> $'+escG(formData.securityDeposit||'0.00')+'</p><p class="lease-info">Maximum allowed: '+province.rentRules.maxDeposit+'</p>'+(formData.petDeposit?'<p><strong>Pet Damage Deposit:</strong> $'+escG(formData.petDeposit)+'</p>':'');
  }
  html += '</div>';

  html += '<div class="lease-section"><h2>6. SERVICES & UTILITIES</h2><table class="lease-table"><thead><tr><th>Service</th><th>Included in Rent</th><th>Tenant Pays Separately</th></tr></thead><tbody>'+buildUtilityRow('Heat',formData.utilities)+buildUtilityRow('Electricity',formData.utilities)+buildUtilityRow('Water',formData.utilities)+buildUtilityRow('Internet',formData.utilities)+buildUtilityRow('Cable/TV',formData.utilities)+buildUtilityRow('Laundry',formData.utilities)+buildUtilityRow('Air Conditioning',formData.utilities)+'</tbody></table></div>';

  html += '<div class="lease-section"><h2>7. RULES & CONDITIONS</h2><p><strong>Smoking:</strong> '+(formData.smokingAllowed?'Permitted in designated areas':'Not permitted on the premises')+'</p><p><strong>Pets:</strong> '+(formData.petsAllowed?'Permitted':'Not permitted')+(province.code==='ON'?' <em>(Note: No-pet clauses are void and unenforceable in Ontario per RTA s.14)</em>':'')+'</p>'+(formData.guestPolicy?'<p><strong>Guest Policy:</strong> '+escG(formData.guestPolicy)+'</p>':'')+(formData.noisePolicy?'<p><strong>Noise/Quiet Hours:</strong> '+escG(formData.noisePolicy)+'</p>':'')+'</div>';

  html += '<div class="lease-section lease-section-maintenance"><h2>8. MAINTENANCE & REPAIRS</h2><p>The <strong>Landlord</strong> is responsible for maintaining the rental unit in a good state of repair and in compliance with the '+province.legislationShort+'.</p><p>The <strong>Tenant</strong> is responsible for:</p><ul><li>Keeping the unit reasonably clean</li><li>Promptly reporting maintenance issues or damage</li><li>Repairing or paying for damage caused by the tenant, guests, or pets</li><li>Not altering the unit without written consent</li></ul>'+(formData.maintenanceNotes?'<p><strong>Additional Notes:</strong> '+escG(formData.maintenanceNotes)+'</p>':'')+'</div>';

  html += '<div class="lease-section"><h2>9. LANDLORD\'S RIGHT OF ENTRY</h2><p>The Landlord may enter only in accordance with the '+province.legislationShort+'. Except in emergencies, the Landlord must provide:</p><ul><li><strong>Written notice</strong> of at least 24 hours</li><li>Entry only between <strong>8:00 AM and 8:00 PM</strong></li><li>A valid reason as permitted by law</li></ul></div>';

  html += '<div class="lease-section"><h2>10. INSURANCE</h2><p><strong>Tenant Insurance:</strong> '+(formData.tenantInsuranceRequired?'Required — Tenant must obtain and maintain renter\'s insurance.':'Recommended but not required.')+'</p><p>The Landlord\'s insurance does not cover the Tenant\'s personal belongings or liability.</p></div>';

  var sectionNum = 11;
  if (formData.additionalTerms) {
    html += '<div class="lease-section"><h2>'+sectionNum+'. ADDITIONAL TERMS</h2><div class="lease-additional">'+escG(formData.additionalTerms).replace(/\n/g,'<br>')+'</div><p class="lease-info">Any term that conflicts with the '+province.legislationShort+' is void and unenforceable.</p></div>';
    sectionNum++;
  }

  html += '<div class="lease-section"><h2>'+sectionNum+'. IMPORTANT LEGAL INFORMATION</h2><div class="lease-legal"><p>This agreement is governed by the <strong>'+province.legislation+'</strong>.</p><p>Disputes may be resolved through the <strong>'+province.regulator+'</strong>.</p><h3>Prohibited Clauses in '+province.name+':</h3><ul>'+province.prohibitedClauses.map(function(c){return '<li>'+c+'</li>';}).join('')+'</ul>'+province.notes.map(function(n){return '<p class="lease-info">'+n+'</p>';}).join('')+'</div></div>';
  sectionNum++;

  if (selectedSchedules && selectedSchedules.length > 0) {
    html += '<div class="lease-section"><h2>'+sectionNum+'. SCHEDULES</h2><p>The following schedules are attached to and form part of this Agreement:</p><ul>'+selectedSchedules.map(function(s,i){return '<li><strong>Schedule '+String.fromCharCode(65+i)+':</strong> '+s.name+'</li>';}).join('')+'</ul></div>';
    selectedSchedules.forEach(function(schedule, i) { html += generateScheduleContent(schedule, i, formData, province); });
  }

  html += '<div class="lease-section lease-signatures"><h2>SIGNATURES</h2><p>By signing below, the parties agree to the terms and conditions of this Residential Tenancy Agreement.</p><div class="sig-grid"><div class="sig-block"><div class="sig-line"></div><p>Landlord Signature</p><p class="sig-name">'+escG(formData.landlordName)+'</p><p class="sig-date">Date: _______________________</p></div><div class="sig-block"><div class="sig-line"></div><p>Tenant Signature</p><p class="sig-name">'+escG(formData.tenantName)+'</p><p class="sig-date">Date: _______________________</p></div></div>'+(formData.additionalTenants?'<div class="sig-grid" style="margin-top:30px;"><div class="sig-block"><div class="sig-line"></div><p>Additional Tenant Signature</p><p class="sig-date">Date: _______________________</p></div><div class="sig-block"><div class="sig-line"></div><p>Witness Signature (if applicable)</p><p class="sig-date">Date: _______________________</p></div></div>':'')+'</div>';

  return html;
}

function generateScheduleContent(schedule, index, formData, province) {
  var letter = String.fromCharCode(65+index);
  var html = '<div class="lease-section lease-schedule" style="page-break-before:always;"><h2>SCHEDULE '+letter+': '+schedule.name.toUpperCase()+'</h2><p class="lease-subtitle">'+schedule.description+'</p>';
  switch(schedule.id) {
    case 'moveInInspection': case 'conditionReport': html += generateInspectionSchedule(formData); break;
    case 'petAgreement': html += generatePetSchedule(formData, province); break;
    case 'parking': html += generateParkingSchedule(formData); break;
    case 'storage': html += generateStorageSchedule(formData); break;
    case 'utilities': html += generateUtilitiesSchedule(formData); break;
    case 'maintenance': html += generateMaintenanceSchedule(formData, province); break;
    case 'keyReceipt': html += generateKeySchedule(formData); break;
    case 'smoking': html += generateSmokingSchedule(formData); break;
    case 'commonAreas': html += generateCommonAreasSchedule(formData); break;
    case 'renovation': html += generateRenovationSchedule(formData, province); break;
    case 'bylaw': case 'strata': case 'condominium': html += generateBylawSchedule(formData, province); break;
    default: html += '<div class="schedule-blank"><p>Additional terms as agreed between the parties:</p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(15)+'</div></div>';
  }
  html += '<div class="schedule-sig"><div class="sig-grid"><div class="sig-block"><div class="sig-line"></div><p>Landlord Initials / Date</p></div><div class="sig-block"><div class="sig-line"></div><p>Tenant Initials / Date</p></div></div></div></div>';
  return html;
}

function generateInspectionSchedule(formData) {
  var rooms = ['Living Room','Kitchen','Bedroom 1','Bedroom 2','Bathroom','Hallway/Entrance','Balcony/Patio','Other'];
  var conditions = ['Walls & Ceiling','Flooring','Windows & Blinds','Doors & Locks','Light Fixtures','Outlets/Switches','Appliances','Plumbing/Fixtures','Cleanliness'];
  return '<p><strong>Unit Address:</strong> '+escG(formData.unitAddress)+'</p><p><strong>Inspection Date:</strong> _______________________</p><p><strong>Inspected By:</strong> Landlord: _________________ Tenant: _________________</p><table class="lease-table inspection-table"><thead><tr><th>Room</th><th>Item</th><th>Condition (Move-In)</th><th>Condition (Move-Out)</th><th>Notes</th></tr></thead><tbody>'+rooms.map(function(room){return conditions.map(function(cond,ci){return '<tr>'+(ci===0?'<td rowspan="'+conditions.length+'" class="room-cell">'+room+'</td>':'')+'<td>'+cond+'</td><td class="condition-cell"></td><td class="condition-cell"></td><td class="notes-cell"></td></tr>';}).join('');}).join('')+'</tbody></table><p><strong>General Notes:</strong></p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(5)+'</div>';
}
function generatePetSchedule(formData, province) {
  return '<p>This Pet Agreement forms part of the Residential Tenancy Agreement.</p>'+(province.code==='ON'?'<p class="lease-warning"><strong>Ontario Note:</strong> No-pet clauses are void under RTA s.14.</p>':'')+'<table class="lease-table"><thead><tr><th>Pet Type</th><th>Breed</th><th>Name</th><th>Weight</th></tr></thead><tbody><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr></tbody></table><h3>Pet Rules</h3><ul><li>Tenant is responsible for all damage caused by pets</li><li>Pets must be supervised in common areas</li><li>Tenant must clean up after pets immediately</li><li>Excessive noise from pets may constitute a disturbance</li><li>Tenant must comply with all municipal animal bylaws</li></ul><p><strong>Additional pet conditions:</strong></p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(4)+'</div>';
}
function generateParkingSchedule(formData) {
  return '<h3>Parking Details</h3><p><strong>Parking Space Number:</strong> _______________________</p><p><strong>Location:</strong> _______________________</p><p><strong>Type:</strong> Indoor / Outdoor / Underground (circle one)</p><p><strong>Included in Rent:</strong> Yes / No</p><p><strong>Additional Monthly Cost:</strong> $ _______________________</p><h3>Parking Rules</h3><ul><li>Only registered vehicles may use the assigned space</li><li>Vehicle must be insured and in operable condition</li><li>No storage of hazardous materials</li></ul><table class="lease-table"><thead><tr><th>Make/Model</th><th>Year</th><th>Colour</th><th>License Plate</th></tr></thead><tbody><tr><td></td><td></td><td></td><td></td></tr></tbody></table>';
}
function generateStorageSchedule(formData) {
  return '<h3>Storage Details</h3><p><strong>Storage Unit/Locker Number:</strong> _______________________</p><p><strong>Location:</strong> _______________________</p><p><strong>Included in Rent:</strong> Yes / No</p><h3>Storage Rules</h3><ul><li>No hazardous, flammable, or perishable items</li><li>Tenant must provide their own lock</li><li>Landlord is not responsible for theft or damage to stored items</li></ul>';
}
function generateUtilitiesSchedule(formData) {
  return '<h3>Utility Responsibilities</h3><table class="lease-table"><thead><tr><th>Utility</th><th>Landlord Pays</th><th>Tenant Pays</th><th>Estimated Monthly Cost</th></tr></thead><tbody><tr><td>Electricity</td><td></td><td></td><td></td></tr><tr><td>Natural Gas / Heat</td><td></td><td></td><td></td></tr><tr><td>Water / Sewer</td><td></td><td></td><td></td></tr><tr><td>Internet</td><td></td><td></td><td></td></tr><tr><td>Cable / TV</td><td></td><td></td><td></td></tr></tbody></table><p><strong>Notes:</strong></p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(4)+'</div>';
}
function generateMaintenanceSchedule(formData, province) {
  return '<h3>Maintenance Responsibilities</h3><table class="lease-table"><thead><tr><th>Item</th><th>Landlord</th><th>Tenant</th><th>Notes</th></tr></thead><tbody><tr><td>Lawn Care / Snow Removal</td><td></td><td></td><td></td></tr><tr><td>Appliance Repairs</td><td></td><td></td><td></td></tr><tr><td>Plumbing Issues</td><td></td><td></td><td></td></tr><tr><td>Electrical Issues</td><td></td><td></td><td></td></tr><tr><td>HVAC / Furnace</td><td></td><td></td><td></td></tr><tr><td>Pest Control</td><td></td><td></td><td></td></tr></tbody></table><p class="lease-info">Per '+province.legislationShort+', the landlord must maintain the unit in a good state of repair.</p>';
}
function generateKeySchedule(formData) {
  return '<h3>Keys & Access Devices Issued</h3><table class="lease-table"><thead><tr><th>Item</th><th>Quantity</th><th>Deposit (if any)</th></tr></thead><tbody><tr><td>Unit Key</td><td></td><td></td></tr><tr><td>Mailbox Key</td><td></td><td></td></tr><tr><td>Building Fob/Card</td><td></td><td></td></tr><tr><td>Garage Remote</td><td></td><td></td></tr><tr><td>Storage Key</td><td></td><td></td></tr></tbody></table><p>All keys/devices must be returned at end of tenancy.</p>';
}
function generateSmokingSchedule(formData) {
  return '<h3>Smoking Policy</h3><p><strong>Smoking (tobacco):</strong> '+(formData.smokingAllowed?'Permitted in designated areas only':'Prohibited on premises')+'</p><p><strong>Cannabis smoking/vaping:</strong> _______________________</p><p><strong>Designated smoking area(s):</strong> _______________________</p><h3>Rules</h3><ul><li>No smoking near building entrances, windows, or air intakes</li><li>Tenant is responsible for any damage caused by smoking</li></ul>';
}
function generateCommonAreasSchedule(formData) {
  return '<h3>Common Areas & Amenities</h3><table class="lease-table"><thead><tr><th>Amenity</th><th>Available</th><th>Hours</th><th>Rules/Notes</th></tr></thead><tbody><tr><td>Laundry Room</td><td></td><td></td><td></td></tr><tr><td>Gym/Fitness Room</td><td></td><td></td><td></td></tr><tr><td>Pool</td><td></td><td></td><td></td></tr><tr><td>Party/Meeting Room</td><td></td><td></td><td></td></tr><tr><td>Bike Storage</td><td></td><td></td><td></td></tr></tbody></table><h3>General Rules</h3><ul><li>Common areas must be left clean after use</li><li>Guests must be accompanied by tenant</li></ul>';
}
function generateRenovationSchedule(formData, province) {
  return '<h3>Renovation / Alteration Agreement</h3><p>The Tenant requests permission to make the following alterations:</p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(5)+'</div><h3>Conditions</h3><ul><li>All work must be completed professionally</li><li>Landlord must approve all changes in writing before work begins</li><li>Tenant is responsible for all costs</li></ul>';
}
function generateBylawSchedule(formData, province) {
  return '<h3>'+(province.code==='BC'?'Strata':province.code==='AB'?'Condominium':'Building')+' Rules & Bylaws</h3><p>The Tenant acknowledges receipt of and agrees to comply with the following rules and bylaws:</p><div class="blank-lines">'+'<div class="blank-line"></div>'.repeat(10)+'</div><p><strong>Date provided:</strong> _______________________</p>';
}

document.addEventListener('DOMContentLoaded', function() {
  // Populate provinces
  var select = $('#province');
  provinceList.forEach(function(p) {
    var opt = document.createElement('option');
    opt.value = p.code;
    opt.textContent = p.name;
    select.appendChild(opt);
  });

  // Core event listeners
  setupAllEvents();
  showStep(1);

  // Enhanced features
  try { setupClauseChecker(); } catch(e) { console.warn('ClauseChecker:', e); }
  try { setupDraftsUI(); } catch(e) { console.warn('Drafts:', e); }
  try { setupTemplatesUI(); } catch(e) { console.warn('Templates:', e); }
  try { setupImportUI(); } catch(e) { console.warn('Import:', e); }
  try { startAutoSave(collectFormData); } catch(e) { console.warn('AutoSave:', e); }

  // Auto-save recovery
  try {
    if (hasAutoSave()) {
      var banner = document.createElement('div');
      banner.className = 'autosave-banner';
      banner.innerHTML = '<span>You have an unsaved draft from a previous session.</span><button class="btn btn-sm btn-primary" id="btn-restore-autosave">Restore</button><button class="btn btn-sm btn-secondary" id="btn-dismiss-autosave">Dismiss</button>';
      $('main .container').prepend(banner);
      var restoreBtn = $('#btn-restore-autosave');
      if (restoreBtn) restoreBtn.addEventListener('click', function() { var d = getAutoSave(); if (d) applyFormData(d); banner.remove(); });
      var dismissBtn = $('#btn-dismiss-autosave');
      if (dismissBtn) dismissBtn.addEventListener('click', function() { deleteDraft('__autosave__'); banner.remove(); });
    }
  } catch(e) {}
});


function showStep(step) {
  $$('.form-step').forEach(function(s) { s.classList.remove('active'); });
  var target = $('.form-step[data-step="' + step + '"]');
  if (target) target.classList.add('active');
  $$('.step-indicator .step').forEach(function(s, i) {
    s.classList.toggle('active', i + 1 === step);
    s.classList.toggle('completed', i + 1 < step);
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextStep(current) {
  if (!validateStep(current)) return;
  if (current === 1) onProvinceSelected();
  if (current === 4) buildScheduleSelector();
  if (current === 5) generatePreview();
  showStep(current + 1);
}

function onProvinceSelected() {
  var code = $('#province').value;
  currentProvince = provinces[code];
  if (!currentProvince) return;
  var info = $('#province-info');
  info.innerHTML = '<strong>' + currentProvince.name + '</strong> \u2014 ' + currentProvince.legislationShort +
    (currentProvince.standardLeaseRequired ? '<br><span class="info-warning">This province requires the official <strong>' + currentProvince.standardLeaseForm + '</strong>. This tool generates a supplemental agreement.</span>' : '') +
    '<br>Regulator: ' + currentProvince.regulator + '<br>Deposit rules: ' + currentProvince.rentRules.maxDeposit;
  info.hidden = false;
  updateDepositFields();
  updateRightsSidebar();
  if (code === 'QC' && getLanguage() !== 'fr') showLanguagePrompt();
}

function showLanguagePrompt() {
  var existing = $('#lang-prompt');
  if (existing) existing.remove();
  var p = document.createElement('div');
  p.id = 'lang-prompt'; p.className = 'lang-prompt';
  p.innerHTML = '<span>Quebec selected \u2014 switch to French?</span><button class="btn btn-sm btn-primary" id="btn-lang-fr">Oui, en fran\u00e7ais</button><button class="btn btn-sm btn-secondary" id="btn-lang-en">No, keep English</button>';
  $('#province-info').after(p);
  $('#btn-lang-fr').addEventListener('click', function() { setLanguage('fr'); var b = $('#lang-switch'); if (b) b.textContent = 'EN'; p.remove(); });
  $('#btn-lang-en').addEventListener('click', function() { p.remove(); });
}

function updateDepositFields() {
  if (!currentProvince) return;
  var el = $('#deposit-fields'); var html = '';
  if (currentProvince.code === 'ON') {
    html = '<div class="form-group"><label for="lastMonthDeposit">Last Month\'s Rent Deposit ($)</label><input type="number" id="lastMonthDeposit" step="0.01" placeholder="Same as rent amount"><span class="field-help">Ontario only allows a last month\'s rent deposit (RTA s.106)</span></div>';
  } else if (currentProvince.code === 'QC') {
    html = '<p class="form-notice">Security deposits are <strong>prohibited</strong> in Quebec. Only first month\'s rent may be collected.</p>';
  } else {
    html = '<div class="form-group"><label for="securityDeposit">Security Deposit ($)</label><input type="number" id="securityDeposit" step="0.01" placeholder="0.00"><span class="field-help">Maximum: ' + currentProvince.rentRules.maxDeposit + '</span></div>';
    if (currentProvince.code === 'BC') html += '<div class="form-group"><label for="petDeposit">Pet Damage Deposit ($)</label><input type="number" id="petDeposit" step="0.01" placeholder="0.00"><span class="field-help">Max half month\'s rent</span></div>';
  }
  el.innerHTML = html;
  var petNotice = $('#pet-notice');
  if (currentProvince.code === 'ON') { petNotice.textContent = 'Note: No-pet clauses are void and unenforceable in Ontario (RTA s.14)'; petNotice.hidden = false; }
  else { petNotice.hidden = true; }
}

function updateRightsSidebar() {
  if (!currentProvince) return;
  var sb = $('#rights-sidebar');
  sb.innerHTML = renderRightsSidebar(currentProvince.code);
  sb.classList.add('has-content');
}

function setupClauseChecker() {
  var ta = $('#additionalTerms'); var res = $('#clause-check-results'); var timer = null;
  ta.addEventListener('input', function() {
    clearTimeout(timer);
    timer = setTimeout(function() { if (!currentProvince) return; var w = checkClause(ta.value, currentProvince.code); res.innerHTML = renderClauseWarnings(w); res.hidden = w.length === 0; }, 400);
  });
}

function setupDraftsUI() {
  var c = $('#drafts-container'); c.innerHTML = renderDraftManager();
  c.addEventListener('click', function(e) {
    if (e.target.id === 'btn-save-draft') { var ni = $('#draftName'); var name = ni.value.trim() || ('Draft ' + new Date().toLocaleDateString()); saveDraft(name, collectFormData()); ni.value = ''; c.innerHTML = renderDraftManager(); showToast('Draft saved!'); }
    if (e.target.classList.contains('draft-load')) { var d = loadDraft(e.target.dataset.draft); if (d) { applyFormData(d); showToast('Loaded: ' + e.target.dataset.draft); } }
    if (e.target.classList.contains('draft-delete')) { deleteDraft(e.target.dataset.draft); c.innerHTML = renderDraftManager(); showToast('Draft deleted'); }
  });
}

function setupTemplatesUI() {
  var c = $('#template-container'); c.innerHTML = renderTemplateSelector();
  c.addEventListener('click', function(e) {
    var card = e.target.closest('.template-card'); if (!card) return;
    var tmpl = getTemplate(card.dataset.template); if (!tmpl) return;
    applyFormData(tmpl.data); showToast('Template: ' + tmpl.name);
  });
}

function setupImportUI() {
  var c = $('#import-container'); c.innerHTML = renderImportSection();
  var btn = $('#btn-import-paste');
  if (btn) btn.addEventListener('click', function() {
    var modal = document.createElement('div'); modal.className = 'modal-overlay';
    modal.innerHTML = '<div class="modal-content"><h3>Paste Lease Text</h3><p>Paste the text of an existing lease below. We\'ll extract key fields.</p><textarea id="import-paste-text" rows="12" placeholder="Paste your lease text here..."></textarea><div class="modal-actions"><button class="btn btn-primary" id="btn-import-go">Import</button><button class="btn btn-secondary" id="btn-import-cancel">Cancel</button></div></div>';
    document.body.appendChild(modal);
    $('#btn-import-go').addEventListener('click', function() { var txt = $('#import-paste-text').value; if (txt) { applyFormData(parseLeaseText(txt)); showToast('Imported from text'); } modal.remove(); });
    $('#btn-import-cancel').addEventListener('click', function() { modal.remove(); });
    modal.addEventListener('click', function(e) { if (e.target === modal) modal.remove(); });
  });
}

function buildScheduleSelector() {
  if (!currentProvince) return;
  var c = $('#schedule-list'); c.innerHTML = '';
  currentProvince.schedules.forEach(function(s) {
    var div = document.createElement('div'); div.className = 'schedule-option';
    div.innerHTML = '<label><input type="checkbox" value="' + s.id + '"><div class="schedule-info"><strong>' + s.name + '</strong><span>' + s.description + '</span></div></label>';
    c.appendChild(div);
  });
}

function collectFormData() {
  var utilities = {};
  $$('.utility-toggle').forEach(function(el) { utilities[el.dataset.utility] = el.checked ? 'included' : 'tenant'; });
  var termRadio = $('input[name="termType"]:checked');
  return {
    province: $('#province').value,
    landlordName: $('#landlordName').value.trim(),
    landlordAddress: $('#landlordAddress').value.trim(),
    landlordPhone: $('#landlordPhone').value.trim(),
    landlordEmail: $('#landlordEmail').value.trim(),
    tenantName: $('#tenantName').value.trim(),
    tenantPhone: $('#tenantPhone').value.trim(),
    tenantEmail: $('#tenantEmail').value.trim(),
    additionalTenants: $('#additionalTenants').value.trim(),
    unitAddress: $('#unitAddress').value.trim(),
    unitNumber: $('#unitNumber').value.trim(),
    city: $('#city').value.trim(),
    postalCode: $('#postalCode').value.trim(),
    unitType: $('#unitType').value,
    isFurnished: $('#isFurnished').checked,
    parkingIncluded: $('#parkingIncluded').checked,
    parkingDetails: ($('#parkingDetails') || {}).value || '',
    storageIncluded: $('#storageIncluded').checked,
    termType: termRadio ? termRadio.value : 'fixed',
    startDate: $('#startDate').value,
    endDate: $('#endDate').value,
    rentAmount: $('#rentAmount').value,
    rentDueDay: $('#rentDueDay').value || '1st',
    paymentMethod: $('#paymentMethod').value,
    lastMonthDeposit: ($('#lastMonthDeposit') || {}).value || '',
    securityDeposit: ($('#securityDeposit') || {}).value || '',
    petDeposit: ($('#petDeposit') || {}).value || '',
    utilities: utilities,
    smokingAllowed: $('#smokingAllowed').checked,
    petsAllowed: $('#petsAllowed').checked,
    guestPolicy: $('#guestPolicy').value.trim(),
    noisePolicy: $('#noisePolicy').value.trim(),
    tenantInsuranceRequired: $('#tenantInsurance').checked,
    maintenanceNotes: $('#maintenanceNotes').value.trim(),
    additionalTerms: $('#additionalTerms').value.trim(),
  };
}

function applyFormData(data) {
  if (!data) return;
  if (data.province) { $('#province').value = data.province; currentProvince = provinces[data.province]; if (currentProvince) onProvinceSelected(); }
  ['landlordName','landlordAddress','landlordPhone','landlordEmail','tenantName','tenantPhone','tenantEmail','additionalTenants','unitAddress','unitNumber','city','postalCode','startDate','endDate','rentAmount','guestPolicy','noisePolicy','maintenanceNotes','additionalTerms','parkingDetails'].forEach(function(f) { var el = $('#' + f); if (el && data[f] !== undefined) el.value = data[f]; });
  ['unitType','rentDueDay','paymentMethod'].forEach(function(f) { var el = $('#' + f); if (el && data[f]) el.value = data[f]; });
  ['isFurnished','parkingIncluded','storageIncluded','smokingAllowed','petsAllowed'].forEach(function(f) { var el = $('#' + f); if (el && data[f] !== undefined) el.checked = !!data[f]; });
  if (data.tenantInsuranceRequired !== undefined) $('#tenantInsurance').checked = data.tenantInsuranceRequired;
  if (data.termType) { var r = $('input[name="termType"][value="' + data.termType + '"]'); if (r) { r.checked = true; $('#endDateGroup').style.display = data.termType === 'fixed' ? '' : 'none'; } }
  if (data.utilities) { $$('.utility-toggle').forEach(function(el) { var k = el.dataset.utility; if (data.utilities[k] !== undefined) el.checked = data.utilities[k] === 'included'; }); }
  setTimeout(function() {
    if (data.lastMonthDeposit) { var el = $('#lastMonthDeposit'); if (el) el.value = data.lastMonthDeposit; }
    if (data.securityDeposit) { var el = $('#securityDeposit'); if (el) el.value = data.securityDeposit; }
    if (data.petDeposit) { var el = $('#petDeposit'); if (el) el.value = data.petDeposit; }
  }, 100);
}

function generatePreview() {
  selectedSchedules = [];
  $$('#schedule-list input[type="checkbox"]:checked').forEach(function(cb) {
    var ps = currentProvince.schedules.find(function(s) { return s.id === cb.value; });
    if (ps) selectedSchedules.push(ps);
  });
  var formData = collectFormData();
  // Use the generator from the separate script
  var leaseHtml = generateLease(formData, selectedSchedules);
  var timelineHtml = currentProvince ? generateTimeline(formData, currentProvince) : '';
  var sigHtml = createSignatureSection();
  $('#lease-preview').innerHTML = leaseHtml + sigHtml + timelineHtml;
  setTimeout(function() {
    var lc = $('#sig-landlord'); var tc = $('#sig-tenant');
    if (lc) sigPadLandlord = new SignaturePad(lc);
    if (tc) sigPadTenant = new SignaturePad(tc);
    $$('[data-clear]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        if (btn.dataset.clear === 'sig-landlord' && sigPadLandlord) sigPadLandlord.clear();
        if (btn.dataset.clear === 'sig-tenant' && sigPadTenant) sigPadTenant.clear();
      });
    });
  }, 100);
}

function exportPDF() {
  var preview = $('#lease-preview');
  var content = preview.innerHTML;
  if (sigPadLandlord && !sigPadLandlord.isEmpty()) content = content.replace(/<canvas id="sig-landlord"[^>]*><\/canvas>/, '<img src="' + sigPadLandlord.toDataURL() + '" style="width:100%;height:120px;object-fit:contain;">');
  if (sigPadTenant && !sigPadTenant.isEmpty()) content = content.replace(/<canvas id="sig-tenant"[^>]*><\/canvas>/, '<img src="' + sigPadTenant.toDataURL() + '" style="width:100%;height:120px;object-fit:contain;">');
  var tl = ($('#sig-landlord-typed') || {}).value || '';
  var tt = ($('#sig-tenant-typed') || {}).value || '';
  if (tl.trim() && (!sigPadLandlord || sigPadLandlord.isEmpty())) content = content.replace(/<canvas id="sig-landlord"[^>]*><\/canvas>/, '<div style="font-family:cursive;font-size:28px;padding:20px 0;border-bottom:1px solid #333;">' + escH(tl.trim()) + '</div>');
  if (tt.trim() && (!sigPadTenant || sigPadTenant.isEmpty())) content = content.replace(/<canvas id="sig-tenant"[^>]*><\/canvas>/, '<div style="font-family:cursive;font-size:28px;padding:20px 0;border-bottom:1px solid #333;">' + escH(tt.trim()) + '</div>');
  content = content.replace(/<button[^>]*>.*?<\/button>/gs, '');
  content = content.replace(/<input[^>]*class="sig-typed-input"[^>]*>/g, '');
  content = content.replace(/<div class="sig-pad-actions">[\s\S]*?<\/div>/g, '');
  content = content.replace(/<p class="sig-instructions">[\s\S]*?<\/p>/g, '');
  var pw = window.open('', '_blank');
  pw.document.write('<!DOCTYPE html><html><head><title>Residential Tenancy Agreement</title><style>' + getPrintCSS() + '</style></head><body>' + content + '</body></html>');
  pw.document.close();
  pw.onload = function() { pw.print(); };
}

function getPrintCSS() {
  return '@page{margin:20mm;size:letter}body{font-family:Georgia,serif;font-size:11pt;line-height:1.5;color:#1a1a1a}h1{font-size:18pt;text-align:center;margin-bottom:4px;letter-spacing:2px}h2{font-size:13pt;border-bottom:2px solid #1a4fd8;padding-bottom:4px;margin:24px 0 12px;color:#1a4fd8}h3{font-size:11pt;margin:16px 0 8px}.lease-header{text-align:center;margin-bottom:30px;border-bottom:3px double #333;padding-bottom:20px}.lease-subtitle{color:#555;font-style:italic}.lease-legislation{font-size:9pt;color:#666}.lease-note{background:#fff3cd;padding:8px 12px;border-left:4px solid #ffc107;margin:10px 0;font-size:9pt}.lease-section{margin-bottom:20px}.lease-field-group{display:grid;grid-template-columns:1fr 1fr;gap:16px}.lease-field label{font-weight:bold;font-size:9pt;text-transform:uppercase;color:#555}.full-width{grid-column:1/-1}.lease-info{font-size:9pt;color:#555;font-style:italic}.lease-warning{background:#fee;border-left:4px solid #dc2626;padding:8px 12px;font-size:9pt}.lease-table{width:100%;border-collapse:collapse;margin:12px 0;font-size:10pt}.lease-table th,.lease-table td{border:1px solid #ccc;padding:6px 10px;text-align:left}.lease-table th{background:#f0f0f0;font-weight:bold}.lease-legal{background:#f8f9fa;padding:16px;border:1px solid #ddd;border-radius:4px}.sig-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:40px}.sig-block{text-align:center}.sig-line{border-bottom:1px solid #333;height:50px;margin-bottom:8px}.sig-name{font-weight:bold}.sig-date{font-size:9pt;color:#555}.blank-line{border-bottom:1px solid #ccc;height:28px;margin-bottom:4px}.lease-schedule{border-top:3px solid #1a4fd8;padding-top:20px}ul{margin:8px 0;padding-left:24px}li{margin-bottom:4px}.timeline{margin-bottom:30px}.timeline-title{font-size:14pt;margin-bottom:16px;color:#1a4fd8}.timeline-event{display:flex;gap:16px;margin-bottom:16px;padding-left:20px;border-left:3px solid #ddd}.timeline-date{font-weight:bold;font-size:10pt}.timeline-label{font-weight:bold}.timeline-desc{font-size:9pt;color:#555}.signature-section{margin-top:40px;border-top:2px solid #1a4fd8;padding-top:20px}.sig-pads{display:grid;grid-template-columns:1fr 1fr;gap:30px}.sig-pad-group label{font-weight:bold;display:block;margin-bottom:8px}.room-cell{font-weight:bold;background:#f8f8f8;vertical-align:top}';
}

function validateStep(step) {
  var valid = true;
  var stepEl = $('.form-step[data-step="' + step + '"]');
  stepEl.querySelectorAll('[required]').forEach(function(input) {
    var group = input.closest('.form-group');
    if (!input.value.trim()) { if (group) group.classList.add('error'); valid = false; }
    else { if (group) group.classList.remove('error'); }
  });
  if (!valid) { var fe = stepEl.querySelector('.form-group.error'); if (fe) fe.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
  return valid;
}

function setupAllEvents() {
  $$('.btn-next').forEach(function(btn) { btn.addEventListener('click', function() { nextStep(parseInt(btn.closest('.form-step').dataset.step)); }); });
  $$('.btn-prev').forEach(function(btn) { btn.addEventListener('click', function() { showStep(parseInt(btn.closest('.form-step').dataset.step) - 1); }); });
  $('#province').addEventListener('change', function() { var c = $('#province').value; if (c) { currentProvince = provinces[c]; onProvinceSelected(); } });
  $$('input[name="termType"]').forEach(function(r) { r.addEventListener('change', function() { $('#endDateGroup').style.display = r.value === 'fixed' ? '' : 'none'; }); });
  $('#btn-export').addEventListener('click', exportPDF);
  $('#btn-edit').addEventListener('click', function() { showStep(1); });
  $('#btn-regenerate').addEventListener('click', generatePreview);
  var rt = $('#rights-toggle');
  if (rt) rt.addEventListener('click', function() { $('#rights-sidebar').classList.toggle('open'); });
  var ls = $('#lang-switch');
  if (ls) ls.addEventListener('click', function() { var nl = getLanguage() === 'en' ? 'fr' : 'en'; setLanguage(nl); ls.textContent = nl === 'fr' ? 'EN' : 'FR'; });
}

})();
