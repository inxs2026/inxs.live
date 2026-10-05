// British Columbia Lease Red Flag Rules
// Based on: Residential Tenancy Act, RSBC 2002 c. 78
// Phase 2 — Coming Month 2–3

export const bcRules = {
  province: 'British Columbia',
  legislation: 'Residential Tenancy Act, RSBC 2002 c. 78',
  lastUpdated: '2024',
  legalAidUrl: 'https://www2.gov.bc.ca/gov/content/housing-tenancy/residential-tenancies',
  comingSoon: false,

  rules: [
    {
      id: 'bc_excess_security_deposit',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Security Deposit Exceeds Half of First Month\'s Rent',
      patterns: [
        /security\s+deposit\s+(?:of\s+)?(?:one|1|full)\s+month(?:'?s)?\s+rent/i,
        /damage\s+deposit\s+(?:of\s+)?(?:one|1|full)\s+month(?:'?s)?\s+rent/i,
      ],
      description:
        'In BC, a security deposit cannot exceed half of one month\'s rent. A deposit of a full month\'s rent is illegal.',
      legislation: 'Section 19, Residential Tenancy Act (BC)',
      recommendation:
        'If charged more than half a month\'s rent as a security deposit, the excess is recoverable through the Residential Tenancy Branch (RTB).',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'bc_entry_no_notice',
      category: 'Entry & Privacy',
      severity: 'high',
      title: 'Landlord Entry Without 24 Hours Notice',
      patterns: [
        /landlord\s+(?:may|can)\s+enter\s+(?:at\s+any\s+time|without\s+notice)/i,
        /entry\s+without\s+(?:prior\s+)?notice/i,
      ],
      description:
        'BC landlords must give at least 24 hours written notice before entering a rental unit. Entry without notice (outside emergencies) violates the Residential Tenancy Act.',
      legislation: 'Section 29, Residential Tenancy Act (BC)',
      recommendation:
        'You can refuse entry without proper 24-hour written notice. Document any unauthorized entry.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'bc_pet_damage_deposit',
      category: 'Deposits & Fees',
      severity: 'low',
      title: 'Pet Damage Deposit (Legal in BC — Check Amount)',
      patterns: [
        /\bpet\s+(?:damage\s+)?deposit\b/i,
        /\bpet\s+(?:security\s+)?deposit\b/i,
      ],
      description:
        'Unlike Ontario, pet damage deposits ARE legal in BC. However, the amount cannot exceed half of one month\'s rent.',
      legislation: 'Section 19, Residential Tenancy Act (BC)',
      recommendation:
        'A pet damage deposit is legal in BC but cannot exceed half a month\'s rent. Confirm the amount is within this limit.',
      actionable: false,
      isBill60: false,
    },
    {
      id: 'bc_rent_increase_notice',
      category: 'Rent Increases',
      severity: 'high',
      title: 'Rent Increase With Less Than 3 Months Notice',
      patterns: [
        /(?:30|60)\s+days?\s+(?:written\s+)?notice\s+(?:of\s+(?:a\s+)?)?rent\s+increase/i,
      ],
      description:
        'BC requires at least 3 full rental months notice before a rent increase takes effect. 30 or 60 days is insufficient.',
      legislation: 'Section 42, Residential Tenancy Act (BC)',
      recommendation:
        'You are entitled to 3 full rental months notice. A shorter notice period means the increase is invalid.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'bc_no_subletting',
      category: 'Lease Termination',
      severity: 'medium',
      title: 'Prohibition on Subletting',
      patterns: [
        /(?:no|not\s+permitted)\s+sublet(?:ting)?\b/i,
        /subletting\s+(?:is\s+)?(?:strictly\s+)?prohibited\b/i,
      ],
      description:
        'In BC, tenants have the right to sublet with the landlord\'s written consent. The landlord may not unreasonably withhold consent.',
      legislation: 'Section 34, Residential Tenancy Act (BC)',
      recommendation:
        'You can apply to sublet. If the landlord unreasonably refuses, you can dispute it through the RTB.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'bc_late_fees',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Illegal Late Payment Fee',
      patterns: [
        /\blate\s+(?:payment\s+)?(?:fee|penalty|charge)\b/i,
        /\bpenalty\s+for\s+late\s+(?:rent\s+)?payment\b/i,
      ],
      description:
        'Late payment fees are illegal in BC. Landlords cannot charge additional fees for late rent.',
      legislation: 'Section 13, Residential Tenancy Act (BC)',
      recommendation:
        'This clause is unenforceable. The landlord\'s only remedy for late rent is to issue a Notice to End Tenancy.',
      actionable: true,
      isBill60: false,
    },
  ],
};
