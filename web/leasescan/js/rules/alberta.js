// Alberta Lease Red Flag Rules
// Based on: Residential Tenancies Act, RSA 2000, c. R-17.1
// Phase 2 — Coming Month 2–3

export const albertaRules = {
  province: 'Alberta',
  legislation: 'Residential Tenancies Act, RSA 2000, c. R-17.1',
  lastUpdated: '2024',
  legalAidUrl: 'https://www.alberta.ca/rental-housing',
  comingSoon: false,

  rules: [
    {
      id: 'ab_excess_security_deposit',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Security Deposit Exceeds One Month\'s Rent',
      patterns: [
        /security\s+deposit\s+(?:of\s+)?(?:two|three|2|3)\s+months?(?:'?s)?\s+rent/i,
        /damage\s+deposit\s+(?:of\s+)?(?:two|three|2|3)\s+months?(?:'?s)?\s+rent/i,
      ],
      description:
        'In Alberta, a security deposit (damage deposit) cannot exceed one month\'s rent, regardless of the lease term. Deposits exceeding one month\'s rent are illegal.',
      legislation: 'Section 24, Residential Tenancies Act (Alberta)',
      recommendation:
        'If charged more than one month\'s rent as a deposit, the excess must be returned. File a complaint with the Residential Tenancy Dispute Resolution Service (RTDRS).',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'ab_entry_no_notice',
      category: 'Entry & Privacy',
      severity: 'high',
      title: 'Landlord Entry Without 24 Hours Notice',
      patterns: [
        /landlord\s+(?:may|can)\s+enter\s+(?:at\s+any\s+time|without\s+notice)/i,
        /entry\s+without\s+(?:prior\s+)?notice/i,
      ],
      description:
        'Alberta landlords must provide reasonable notice (generally accepted as 24 hours) before entering a rental unit, except in emergencies.',
      legislation: 'Section 23, Residential Tenancies Act (Alberta)',
      recommendation:
        'You can expect reasonable notice before entry. Document any unauthorized entry by your landlord.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'ab_late_fees',
      category: 'Deposits & Fees',
      severity: 'medium',
      title: 'Late Payment Fee (Review Carefully)',
      patterns: [
        /\blate\s+(?:payment\s+)?(?:fee|penalty|charge)\b/i,
        /\bpenalty\s+for\s+late\s+(?:rent\s+)?payment\b/i,
      ],
      description:
        'Alberta does not explicitly prohibit all late fees. However, excessive or punitive late fees may be challenged as illegal additional charges.',
      legislation: 'Section 15, Residential Tenancies Act (Alberta)',
      recommendation:
        'Review the fee amount carefully. Nominal late fees may be enforceable, but large penalties likely are not. Seek advice from the RTDRS.',
      actionable: false,
      isBill60: false,
    },
    {
      id: 'ab_rent_increase_notice',
      category: 'Rent Increases',
      severity: 'high',
      title: 'Insufficient Rent Increase Notice (Less Than 3 Months)',
      patterns: [
        /(?:30|60)\s+days?\s+(?:written\s+)?notice\s+(?:of\s+(?:a\s+)?)?rent\s+increase/i,
      ],
      description:
        'Alberta requires a minimum of 3 months notice before a rent increase on a periodic tenancy. Shorter notice is insufficient.',
      legislation: 'Section 11, Residential Tenancies Act (Alberta)',
      recommendation:
        'You are entitled to 3 full rental periods notice before a rent increase. A shorter notice period means the increase is not valid.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'ab_no_rent_control',
      category: 'Rent Increases',
      severity: 'low',
      title: 'Uncapped Rent Increase (Note: No Rent Control in Alberta)',
      patterns: [
        /rent\s+(?:may|can|shall)\s+(?:be\s+)?(?:increased|raised)\s+(?:by\s+)?(?:any\s+amount|unlimited|at\s+landlord'?s?\s+discretion)/i,
      ],
      description:
        'Unlike Ontario, Alberta has no rent increase guideline or cap — landlords can raise rent by any amount with proper notice (3 months). This is legal but worth knowing.',
      legislation: 'Residential Tenancies Act (Alberta) — no rent cap provisions',
      recommendation:
        'You cannot challenge the amount of a rent increase in Alberta — only the notice period. Budget accordingly and ensure you receive 3 months notice.',
      actionable: false,
      isBill60: false,
    },
    {
      id: 'ab_eviction_no_ltb',
      category: 'Eviction',
      severity: 'high',
      title: 'Illegal Immediate Eviction Clause',
      patterns: [
        /landlord\s+(?:may|can|shall)\s+(?:immediately|forthwith)\s+(?:terminate|evict|end)\s+(?:the\s+)?(?:tenancy|lease)/i,
        /tenant\s+(?:shall|must)\s+(?:immediately|forthwith)\s+vacate/i,
      ],
      description:
        'In Alberta, landlords must follow the proper notice process to end a tenancy. Immediate eviction without proper notice or dispute resolution is illegal.',
      legislation: 'Sections 7–9, Residential Tenancies Act (Alberta)',
      recommendation:
        'Evictions require proper written notice. Contact the RTDRS or a legal aid clinic if threatened with immediate eviction.',
      actionable: true,
      isBill60: false,
    },
  ],
};
