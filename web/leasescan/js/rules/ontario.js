// Ontario Lease Red Flag Rules
// Based on: Residential Tenancies Act, 2006 (RTA) + Bill 60 (2025) amendments

export const ontarioRules = {
  province: 'Ontario',
  legislation: 'Residential Tenancies Act, 2006',
  lastUpdated: 'November 2025 (Bill 60 amendments)',
  legalAidUrl: 'https://tribunalsontario.ca/ltb/',

  rules: [
    // ─── DEPOSITS & FEES ────────────────────────────────────────────────────
    {
      id: 'on_security_deposit',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Illegal Security or Damage Deposit',
      patterns: [
        /\bsecurity\s+deposit\b/i,
        /\bdamage\s+deposit\b/i,
        /\brefundable\s+deposit\b/i,
        /\bdeposit\s+to\s+cover\s+damages?\b/i,
      ],
      description:
        'Ontario landlords can only collect a last month\'s rent deposit. Demanding a security or damage deposit of any kind is illegal under the RTA.',
      legislation: 'Sections 105–106, Residential Tenancies Act, 2006',
      recommendation:
        'Refuse to pay. You can file an application (T1) with the Landlord and Tenant Board (LTB) to recover any illegal deposit already paid.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_pet_deposit',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Illegal Pet Deposit',
      patterns: [/\bpet\s+deposit\b/i, /\banimal\s+deposit\b/i, /\bpet\s+fee\b/i],
      description:
        'Pet deposits are illegal in Ontario. Landlords cannot charge any extra deposit or fee specifically for having a pet.',
      legislation: 'Section 105, Residential Tenancies Act, 2006',
      recommendation:
        'Do not pay a pet deposit. This is illegal regardless of what the lease says.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_key_deposit',
      category: 'Deposits & Fees',
      severity: 'medium',
      title: 'Key / Fob Deposit (Potentially Illegal)',
      patterns: [
        /\bkey\s+deposit\b/i,
        /\bfob\s+deposit\b/i,
        /\baccess\s+card\s+deposit\b/i,
        /\bparking\s+(?:pass|tag)\s+deposit\b/i,
      ],
      description:
        'Key or fob deposits are legally questionable in Ontario. The LTB has found them illegal unless the amount is a direct pass-through of the landlord\'s actual cost and is fully refundable.',
      legislation: 'Section 134, Residential Tenancies Act, 2006',
      recommendation:
        'Ask for written confirmation that it is fully refundable and request a receipt showing the actual cost. File a T1 with the LTB if the landlord refuses to refund it.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_application_fee',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Illegal Application or Credit Check Fee',
      patterns: [
        /\bapplication\s+fee\b/i,
        /\bcredit\s+(?:check|report)\s+fee\b/i,
        /\bscreening\s+fee\b/i,
        /\bbackground\s+check\s+fee\b/i,
      ],
      description:
        'Landlords cannot charge application fees or credit check fees in Ontario. These are explicitly prohibited additional charges under the RTA.',
      legislation: 'Section 134, Residential Tenancies Act, 2006',
      recommendation:
        'Do not pay any application or credit-check fee. Report the landlord to the LTB — this is a violation even before you move in.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_admin_fee',
      category: 'Deposits & Fees',
      severity: 'medium',
      title: 'Suspicious Administrative Fee',
      patterns: [
        /\badmin(?:istrative)?\s+fee\b/i,
        /\bprocessing\s+fee\b/i,
        /\bsetup\s+fee\b/i,
        /\bmove-?in\s+fee\b/i,
        /\bbooking\s+fee\b/i,
      ],
      description:
        'Administrative fees not tied to a specific service actually rendered are generally illegal. Landlords cannot charge fees beyond lawful rent and last-month\'s-rent deposit.',
      legislation: 'Section 134, Residential Tenancies Act, 2006',
      recommendation:
        'Ask for a written explanation of exactly what the fee covers. If it does not correspond to an actual service, it is likely illegal.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_late_fee',
      category: 'Deposits & Fees',
      severity: 'high',
      title: 'Illegal Late Payment Penalty',
      patterns: [
        /\blate\s+(?:payment\s+)?(?:fee|penalty|charge)\b/i,
        /\bpenalty\s+for\s+late\s+(?:rent\s+)?payment\b/i,
        /\blate\s+rent\s+(?:fee|penalty|surcharge)\b/i,
        /\$[\d,]+\s+(?:per\s+day\s+)?(?:for\s+)?late\s+(?:rent|payment)\b/i,
      ],
      description:
        'Late fees on rent are illegal in Ontario. Landlords cannot charge any extra money because rent was paid late.',
      legislation: 'Section 134, Residential Tenancies Act, 2006',
      recommendation:
        'Strike out this clause. It is unenforceable under Ontario law and the landlord cannot collect it.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_nsf_fee',
      category: 'Deposits & Fees',
      severity: 'low',
      title: 'NSF / Returned Cheque Fee (Check the Amount)',
      patterns: [
        /\bnsf\s+(?:fee|charge|penalty)\b/i,
        /\breturned\s+(?:cheque|check)\s+(?:fee|charge)\b/i,
        /\binsufficient\s+funds?\s+(?:fee|charge|penalty)\b/i,
        /\bbounced\s+(?:cheque|check)\s+fee\b/i,
      ],
      description:
        'A reasonable NSF fee that reflects the landlord\'s actual bank charge may be acceptable, but fees significantly above the bank\'s actual cost (typically $20–$45) likely violate the prohibition on additional charges.',
      legislation: 'Section 134, Residential Tenancies Act, 2006',
      recommendation:
        'Ask for the landlord\'s bank NSF charge as proof. If the lease fee far exceeds the actual bank charge, it is likely illegal.',
      actionable: false,
      isBill60: false,
    },

    // ─── PETS ────────────────────────────────────────────────────────────────
    {
      id: 'on_no_pets',
      category: 'Pets',
      severity: 'medium',
      title: 'No-Pets Clause (Unenforceable in Ontario)',
      patterns: [
        /\bno\s+pets?\s+(?:allowed|permitted)\b/i,
        /\bpets?\s+(?:are\s+)?(?:strictly\s+)?(?:not\s+)?(?:allowed|permitted|prohibited)\b/i,
        /\btenant\s+shall\s+not\s+(?:keep|have|own|harbour)\s+(?:any\s+)?(?:pets?|animals?)\b/i,
        /\bno\s+animals?\s+(?:of\s+any\s+kind\s+)?(?:are\s+)?(?:permitted|allowed)\b/i,
      ],
      description:
        'No-pets clauses in Ontario leases are legally unenforceable under the RTA. You have the right to keep a pet regardless of this clause — with one exception: condo buildings where the condo corporation\'s declaration validly prohibits pets.',
      legislation: 'Section 14, Residential Tenancies Act, 2006',
      recommendation:
        'You can legally keep a pet despite this clause. If you are in a condo, ask the landlord if the condo corporation\'s declaration restricts pets — that is the only enforceable exception.',
      actionable: false,
      isBill60: false,
    },

    // ─── ENTRY & PRIVACY ─────────────────────────────────────────────────────
    {
      id: 'on_entry_anytime',
      category: 'Entry & Privacy',
      severity: 'high',
      title: 'Landlord Entry Without Proper Notice',
      patterns: [
        /landlord\s+(?:may|can|shall|reserves?\s+the\s+right\s+to)\s+enter\s+(?:the\s+)?(?:unit|premises|rental\s+unit|property)\s+at\s+any\s+time/i,
        /entry\s+(?:may\s+be\s+)?made\s+(?:at\s+any\s+time|without\s+(?:prior\s+)?notice)/i,
        /(?:without|no)\s+(?:prior\s+)?notice\s+(?:is\s+required\s+)?(?:for\s+)?(?:entry|inspection|access)/i,
        /landlord\s+(?:may|can)\s+enter\s+without\s+notice/i,
      ],
      description:
        'Ontario law requires landlords to give at least 24 hours written notice before entering a rental unit, stating the reason and the time of entry. Entry "at any time" or "without notice" (outside genuine emergencies) is illegal.',
      legislation: 'Section 27, Residential Tenancies Act, 2006',
      recommendation:
        'This clause is unenforceable. You can refuse entry if 24 hours written notice has not been given (except in a genuine emergency such as fire or flood).',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_entry_insufficient_notice',
      category: 'Entry & Privacy',
      severity: 'high',
      title: 'Insufficient Entry Notice (Less Than 24 Hours)',
      patterns: [
        /(?:12|8|6|4|2|1|one|two|four|six|eight|twelve)\s+hours?\s+(?:written\s+)?notice\s+(?:of\s+)?(?:entry|inspection|access)/i,
        /(?:entry|inspection)\s+(?:with|upon|after)\s+(?:12|8|6|4|2|1|one|two|four|six|eight|twelve)\s+hours?\s+notice/i,
      ],
      description:
        'The minimum notice period before a landlord can enter a rental unit is 24 hours. Anything less violates the RTA.',
      legislation: 'Section 27, Residential Tenancies Act, 2006',
      recommendation:
        'You are legally entitled to 24 hours written notice. This clause is unenforceable.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_excessive_inspections',
      category: 'Entry & Privacy',
      severity: 'medium',
      title: 'Excessively Frequent Inspection Rights',
      patterns: [
        /monthly\s+(?:routine\s+)?inspections?\b/i,
        /weekly\s+inspections?\b/i,
        /landlord\s+(?:may|can|shall)\s+(?:conduct\s+)?(?:regular|monthly|weekly|periodic)\s+inspections?/i,
        /inspection\s+(?:every|each)\s+(?:month|week)/i,
      ],
      description:
        'While landlords can conduct inspections, overly frequent inspection schedules can amount to harassment. Even valid inspections require 24 hours written notice each time.',
      legislation: 'Section 27, Residential Tenancies Act, 2006',
      recommendation:
        'Ensure every inspection is preceded by 24 hours written notice. If inspections feel harassing, document them and contact the LTB.',
      actionable: false,
      isBill60: false,
    },

    // ─── RENT ─────────────────────────────────────────────────────────────────
    {
      id: 'on_rent_increase_short_notice',
      category: 'Rent Increases',
      severity: 'high',
      title: 'Insufficient Rent Increase Notice (Less Than 90 Days)',
      patterns: [
        /(?:30|60)\s+days?\s+(?:written\s+)?notice\s+(?:of\s+(?:a\s+)?)?rent\s+increase/i,
        /rent\s+(?:may|can)\s+(?:be\s+)?increas(?:ed|e)\s+(?:with|upon|after)\s+(?:30|60)\s+days?/i,
        /(?:30|60)[\s-]day\s+(?:written\s+)?notice\s+(?:for\s+)?(?:a\s+)?rent\s+increase/i,
      ],
      description:
        'Ontario law requires a minimum of 90 days written notice before any rent increase can take effect. A lease clause specifying 30 or 60 days is insufficient and unenforceable.',
      legislation: 'Section 116, Residential Tenancies Act, 2006',
      recommendation:
        'You are entitled to 90 days written notice. A rent increase given with less notice is void — you do not have to pay the increased amount.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_rent_increase_at_will',
      category: 'Rent Increases',
      severity: 'high',
      title: 'Open-Ended Rent Increase Clause',
      patterns: [
        /landlord\s+(?:may|can)\s+(?:increase|raise)\s+(?:the\s+)?rent\s+at\s+(?:any\s+time|(?:the\s+)?(?:landlord'?s?\s+)?discretion)/i,
        /rent\s+(?:shall|will|may)\s+(?:be\s+)?(?:increased|adjusted)\s+(?:at\s+)?(?:the\s+)?landlord'?s?\s+(?:sole\s+)?discretion/i,
        /rent\s+(?:shall|will)\s+increase\s+(?:automatically\s+)?(?:each|every)\s+year\s+by/i,
      ],
      description:
        'Rent increases in Ontario are strictly governed by the RTA: only once per 12-month period, with 90 days notice, and generally limited to the annual Rent Increase Guideline (RIG) set by the province.',
      legislation: 'Sections 116–120, Residential Tenancies Act, 2006',
      recommendation:
        'Any open-ended rent increase clause is unenforceable. Always check the current RIG on the Ontario government website before any increase takes effect.',
      actionable: true,
      isBill60: false,
    },

    // ─── MAINTENANCE & REPAIRS ────────────────────────────────────────────────
    {
      id: 'on_tenant_all_maintenance',
      category: 'Maintenance & Repairs',
      severity: 'medium',
      title: 'Tenant Responsible for All Repairs',
      patterns: [
        /tenant\s+(?:shall|will|must|agrees?\s+to)\s+(?:be\s+responsible\s+for\s+all|pay\s+for\s+all|maintain)\s+(?:repairs?|maintenance)/i,
        /all\s+repairs?\s+(?:and\s+maintenance\s+)?(?:shall\s+be\s+)?(?:at\s+the\s+)?tenant'?s?\s+(?:expense|cost|responsibility)/i,
        /tenant\s+is\s+(?:solely\s+)?responsible\s+for\s+(?:all|any)\s+(?:repairs?|maintenance|upkeep)/i,
      ],
      description:
        'Landlords are legally responsible for maintaining rental units in a good state of repair and complying with health and safety standards. Broad clauses shifting all repair costs to the tenant contradict the RTA.',
      legislation: 'Sections 20–21, Residential Tenancies Act, 2006',
      recommendation:
        'Tenants are only responsible for damage they deliberately or negligently cause. You can file a T6 (Maintenance) application with the LTB if the landlord fails to repair.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_hvac_maintenance',
      category: 'Maintenance & Repairs',
      severity: 'medium',
      title: 'Tenant Required to Maintain HVAC or Major Appliances',
      patterns: [
        /tenant\s+(?:shall|will|must)\s+(?:maintain|service|repair|replace)\s+(?:the\s+)?(?:hvac|furnace|air\s+conditioner|boiler|water\s+heater|appliances?)/i,
        /furnace\s+(?:filters?\s+)?(?:to\s+be\s+)?(?:changed|replaced|maintained|serviced)\s+by\s+(?:the\s+)?tenant/i,
        /tenant\s+(?:shall|must)\s+(?:annually\s+)?service\s+(?:the\s+)?(?:furnace|hvac|boiler)/i,
      ],
      description:
        'Major appliances, HVAC systems, and structural elements are the landlord\'s responsibility to maintain. While minor tasks (e.g., changing furnace filters) may be agreed upon, requiring tenants to fully service or replace these systems is beyond what the RTA allows.',
      legislation: 'Section 20, Residential Tenancies Act, 2006',
      recommendation:
        'Routine filter changes may be negotiated. Any requirement to repair or replace major systems at your own cost should be challenged.',
      actionable: false,
      isBill60: false,
    },

    // ─── LEASE TERMINATION ────────────────────────────────────────────────────
    {
      id: 'on_lease_break_penalty',
      category: 'Lease Termination',
      severity: 'medium',
      title: 'Excessive Lease-Break Penalty',
      patterns: [
        /(?:two|three|four|five|2|3|4|5)\s+months?\s+(?:rent\s+as\s+a?\s+)?(?:penalty|fee|liquidated\s+damages?)\s+(?:for\s+)?(?:early\s+termination|breaking\s+(?:the\s+)?lease)/i,
        /early\s+termination\s+(?:fee|penalty)\s+of\s+(?:\$[\d,]+|\w+\s+months?\s+(?:rent)?)/i,
        /(?:break|terminate)\s+(?:this\s+)?lease\s+early\s+.{0,60}(?:pay|owing|charge|penalty)\s+\$[\d,]+/i,
      ],
      description:
        'Landlords have a legal duty to mitigate losses when a tenant breaks a lease early. They must make a reasonable effort to re-rent the unit. Fixed "lease break" penalties that don\'t reflect actual losses are likely unenforceable.',
      legislation: 'Section 16, Residential Tenancies Act, 2006 (Duty to Mitigate)',
      recommendation:
        'Your liability is generally limited to rent owed until a new tenant is found or the lease expires — whichever comes first. A fixed penalty does not override the landlord\'s duty to mitigate.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_no_subletting',
      category: 'Lease Termination',
      severity: 'medium',
      title: 'Blanket Prohibition on Subletting or Assignment',
      patterns: [
        /(?:no|not\s+permitted\s+to|shall\s+not|may\s+not)\s+sublet(?:ting)?\b/i,
        /subletting\s+(?:is\s+)?(?:strictly\s+)?prohibited\b/i,
        /tenant\s+(?:shall|may)\s+not\s+assign\s+(?:this|the)\s+lease/i,
        /no\s+assignment\s+(?:of\s+(?:this|the)\s+)?lease\b/i,
        /sublease\s+(?:is\s+)?not\s+(?:allowed|permitted)\b/i,
      ],
      description:
        'Ontario tenants have the right to sublet their unit or assign their lease, subject to the landlord\'s consent. The landlord cannot unreasonably withhold consent. A blanket prohibition conflicts with the RTA.',
      legislation: 'Sections 95–97, Residential Tenancies Act, 2006',
      recommendation:
        'If you need to sublet or assign, make a written request. The landlord must respond within 7 days; unreasonable refusal gives you additional rights, including the right to terminate.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_auto_renewal_fixed',
      category: 'Lease Termination',
      severity: 'medium',
      title: 'Automatic Renewal to Another Fixed Term',
      patterns: [
        /(?:automatically|auto)\s+renew(?:s|ed)?\s+(?:for\s+)?(?:a(?:nother)?|one|1)\s+(?:additional\s+)?(?:year|annual|12[-\s]month)\s+term/i,
        /shall\s+(?:automatically\s+)?(?:be\s+)?renewed\s+for\s+a\s+(?:further|additional|new|subsequent)\s+(?:fixed[\s-]term|year|annual)\s+(?:term|period)/i,
        /absent\s+(?:written\s+)?notice\s+.{0,60}(?:lease|tenancy)\s+(?:shall|will)\s+(?:automatically\s+)?renew/i,
      ],
      description:
        'Under the RTA, when a fixed-term lease ends without a new agreement, the tenancy automatically becomes month-to-month — it does not roll into another fixed term. A clause forcing automatic renewal to another fixed-term without explicit consent is inconsistent with the RTA.',
      legislation: 'Section 38, Residential Tenancies Act, 2006',
      recommendation:
        'You cannot be locked into another fixed term without agreeing to it. After your lease term ends, you continue as a month-to-month tenant with the same rent and full RTA protections.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_excessive_vacate_notice',
      category: 'Lease Termination',
      severity: 'medium',
      title: 'Tenant Required to Give More Than 60 Days Notice',
      patterns: [
        /tenant\s+(?:shall|must|will|agrees?\s+to)\s+(?:provide|give)\s+(?:at\s+least\s+)?(?:90|120|3|4|6)\s+(?:months?\s+|days?\s+)?notice\s+(?:to\s+vacate|of\s+(?:their\s+)?intention\s+to\s+(?:vacate|terminate|end))/i,
        /(?:90|120)[-\s]days?\s+(?:written\s+)?notice\s+(?:to\s+vacate|from\s+(?:the\s+)?tenant)/i,
      ],
      description:
        'For most month-to-month tenancies in Ontario, tenants are only required to give 60 days notice before the end of a rental period. Requiring more notice than the RTA allows is unenforceable.',
      legislation: 'Section 44, Residential Tenancies Act, 2006',
      recommendation:
        'Standard notice for month-to-month tenants is 60 days before the last day of a rental period. You are not legally bound to give more than this.',
      actionable: true,
      isBill60: false,
    },

    // ─── EVICTION ─────────────────────────────────────────────────────────────
    {
      id: 'on_immediate_eviction',
      category: 'Eviction',
      severity: 'high',
      title: 'Illegal Immediate Eviction Clause',
      patterns: [
        /landlord\s+(?:may|can|shall|reserves?\s+the\s+right\s+to)\s+(?:immediately|forthwith)\s+(?:terminate|evict|end)\s+(?:the\s+)?(?:tenancy|lease|rental)/i,
        /tenant\s+(?:shall|must|will)\s+(?:immediately|forthwith)\s+vacate/i,
        /immediate\s+(?:termination|eviction|removal)\s+(?:of\s+the\s+tenant\s+)?(?:upon|for|in\s+the\s+event\s+of)/i,
        /tenancy\s+(?:shall|will|may)\s+be\s+(?:immediately\s+)?terminated\s+(?:for|upon|in\s+the\s+event\s+of)\s+(?:any\s+)?breach/i,
      ],
      description:
        'Landlords in Ontario cannot evict a tenant without first obtaining an order from the Landlord and Tenant Board (LTB). No clause in a lease can give a landlord the right to immediately terminate or require a tenant to immediately vacate.',
      legislation: 'Section 37, Residential Tenancies Act, 2006',
      recommendation:
        'This clause is completely unenforceable. If a landlord tries to evict you without an LTB order, contact duty counsel at the LTB immediately and call local police if necessary.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_lockout',
      category: 'Eviction',
      severity: 'high',
      title: 'Illegal Lockout or Property Seizure Clause',
      patterns: [
        /landlord\s+(?:may|can|shall)\s+(?:change|re-?key)\s+(?:the\s+)?locks?\b/i,
        /(?:change|re-?key)\s+(?:the\s+)?locks?\s+.{0,50}\s+(?:remove|seize|withhold)\s+(?:the\s+)?tenant'?s?\s+(?:belongings|property|possessions)/i,
        /tenant'?s?\s+(?:belongings|property|possessions)\s+(?:may\s+be\s+)?(?:removed|seized|withheld|stored)/i,
        /landlord\s+(?:may|can)\s+(?:remove|dispose\s+of)\s+(?:the\s+)?tenant'?s?\s+(?:belongings|property|possessions)/i,
      ],
      description:
        'Changing locks, seizing a tenant\'s belongings, or cutting off utilities to force a tenant to leave is an illegal "self-help eviction" — a serious offence under the RTA regardless of the reason.',
      legislation: 'Sections 29–31, Residential Tenancies Act, 2006',
      recommendation:
        'This clause is illegal. If your landlord locks you out or removes your belongings, call the LTB emergency line and local police immediately. You may be awarded damages.',
      actionable: true,
      isBill60: false,
    },

    // ─── UTILITIES ────────────────────────────────────────────────────────────
    {
      id: 'on_utility_cutoff',
      category: 'Utilities',
      severity: 'high',
      title: 'Landlord Can Cut Off Utilities',
      patterns: [
        /landlord\s+(?:may|can|reserves?\s+the\s+right\s+to)\s+(?:discontinue|cut\s+off|terminate|withhold|shut\s+off)\s+(?:utilities?|heat|hydro|water|electricity|gas|internet)/i,
        /(?:heat|hydro|water|electricity|utilities?)\s+(?:may\s+be\s+)?(?:discontinued|cut\s+off|withheld|shut\s+off)\s+(?:by\s+(?:the\s+)?landlord|for\s+non-payment)/i,
      ],
      description:
        'Landlords are legally required to maintain access to vital services. Cutting off utilities — even for non-payment of rent — is an illegal eviction tactic.',
      legislation: 'Section 21, Residential Tenancies Act, 2006',
      recommendation:
        'If your landlord cuts off utilities, contact the LTB immediately and file a T2 application. You may be entitled to an abatement of rent and damages.',
      actionable: true,
      isBill60: false,
    },

    // ─── TENANT RIGHTS ────────────────────────────────────────────────────────
    {
      id: 'on_rights_waiver',
      category: 'Tenant Rights',
      severity: 'high',
      title: 'Waiver of RTA Rights',
      patterns: [
        /tenant\s+(?:hereby\s+)?waive(?:s)?\s+(?:any\s+(?:and\s+all\s+)?)?(?:rights?|protections?)\s+(?:under|afforded\s+by)\s+(?:the\s+)?(?:rta|residential\s+tenancies\s+act)/i,
        /waiver\s+of\s+(?:any\s+)?(?:rights?\s+)?under\s+(?:the\s+)?(?:rta|residential\s+tenancies\s+act)/i,
        /tenant\s+agrees?\s+to\s+waive\s+(?:all\s+)?(?:statutory\s+)?(?:rights?|protections?)/i,
        /tenant\s+(?:hereby\s+)?release(?:s)?\s+(?:the\s+)?landlord\s+from\s+(?:all|any)\s+(?:legal\s+)?(?:obligations?|responsibilities?|duties?)\s+under\s+(?:the\s+)?(?:rta|act)/i,
      ],
      description:
        'The RTA is a mandatory statute. Any agreement to waive, modify, or contract out of its protections is void and unenforceable — even if you sign it willingly.',
      legislation: 'Section 3, Residential Tenancies Act, 2006',
      recommendation:
        'This clause is void. Your RTA rights cannot be waived by contract. Landlords who insist on such clauses can be reported to the LTB.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_landlord_liability_waiver',
      category: 'Tenant Rights',
      severity: 'medium',
      title: 'Broad Landlord Liability Waiver',
      patterns: [
        /landlord\s+(?:shall\s+)?(?:not\s+be\s+)?(?:is\s+not\s+)?(?:held\s+)?(?:responsible|liable)\s+for\s+(?:any|all)\s+(?:damage|loss|injury|accident)/i,
        /tenant\s+(?:holds?\s+harmless|releases?)\s+(?:the\s+)?landlord\s+from\s+(?:any|all)\s+(?:claims?|liability|damages?)/i,
        /landlord\s+assumes?\s+no\s+(?:responsibility|liability)\s+for\s+(?:tenant'?s?\s+)?(?:property|belongings|damage|injury)/i,
      ],
      description:
        'Clauses that broadly waive the landlord\'s liability — including for their own negligence — are questionable and may be unenforceable, particularly when the damage results from the landlord\'s failure to maintain the property.',
      legislation: 'Sections 20–22, Residential Tenancies Act, 2006',
      recommendation:
        'While tenants can be responsible for their own negligence, landlords cannot escape liability for failing to maintain the unit. Ensure you have tenant insurance regardless.',
      actionable: false,
      isBill60: false,
    },

    // ─── BILL 60 (2025) ───────────────────────────────────────────────────────
    {
      id: 'on_bill60_arrears',
      category: 'Bill 60 (2025 Changes)',
      severity: 'medium',
      title: 'Rent Arrears Clause — Review Under Bill 60 (2025)',
      patterns: [
        /\barrears?\s+(?:of\s+)?(?:rent|payment)\b/i,
        /\bnon-payment\s+of\s+rent\b/i,
        /\boverdue\s+(?:rent|amount)\b/i,
        /\bunpaid\s+rent\b/i,
      ],
      description:
        'Ontario\'s Bill 60 (November 2025) significantly changed the eviction process for rent arrears. The LTB can now process N4 (non-payment) applications on an expedited basis. Tenants have fewer opportunities to "pay and stay" at the last minute compared to prior rules.',
      legislation: 'Bill 60 (2025), amending Sections 59–68 of the Residential Tenancies Act, 2006',
      recommendation:
        'Under Bill 60, if you receive an N4 Notice, pay the full amount owing within the 14-day window. Waiting until a hearing to pay is now riskier. Seek LTB duty counsel immediately if you receive any eviction notice.',
      actionable: true,
      isBill60: true,
    },
    {
      id: 'on_bill60_own_use',
      category: 'Bill 60 (2025 Changes)',
      severity: 'medium',
      title: 'Landlord Own-Use / Personal Use Clause — Bill 60 Updates',
      patterns: [
        /landlord'?s?\s+(?:own\s+)?(?:use|occupation)\b/i,
        /personal\s+use\s+(?:by|of)\s+(?:the\s+)?(?:landlord|owner)\b/i,
        /(?:owner|landlord)\s+(?:intends?\s+to|will)\s+(?:occupy|move\s+into|use)\s+(?:the\s+)?(?:unit|premises)\b/i,
        /\bn12\b/i,
      ],
      description:
        'Bill 60 (2025) strengthened penalties for bad-faith "landlord own use" (N12) evictions. If a landlord serves an N12 and does not move in, or moves out within 12 months without a legitimate reason, penalties are now significantly higher.',
      legislation: 'Bill 60 (2025), amending Section 48 of the Residential Tenancies Act, 2006',
      recommendation:
        'You are entitled to at least 3 months\' rent compensation and 60 days notice for an N12. Document everything. If the landlord doesn\'t move in after eviction, file a T5 application immediately — fines have increased under Bill 60.',
      actionable: true,
      isBill60: true,
    },
    {
      id: 'on_bill60_virtual_hearings',
      category: 'Bill 60 (2025 Changes)',
      severity: 'low',
      title: 'Dispute Resolution / Hearing Process Clause',
      patterns: [
        /arbitration\s+(?:in\s+lieu\s+of|instead\s+of)\s+(?:ltb|landlord\s+and\s+tenant\s+board)/i,
        /disputes?\s+(?:shall\s+be|to\s+be)\s+(?:resolved|settled)\s+(?:by\s+binding\s+)?arbitration/i,
        /tenant\s+agrees?\s+not\s+to\s+(?:file|make|bring)\s+(?:a\s+)?(?:complaint|application|claim)\s+(?:to|with|at)\s+(?:the\s+)?ltb/i,
      ],
      description:
        'Landlords cannot require tenants to use private arbitration instead of the LTB. Bill 60 (2025) also standardized virtual hearings at the LTB — tenants now have the right to participate remotely.',
      legislation: 'Section 3, Residential Tenancies Act, 2006; Bill 60 (2025) LTB procedural amendments',
      recommendation:
        'Your right to access the LTB cannot be contracted away. If the lease attempts to force private arbitration, that clause is void.',
      actionable: true,
      isBill60: true,
    },

    // ─── GENERAL ──────────────────────────────────────────────────────────────
    {
      id: 'on_standard_lease',
      category: 'General',
      severity: 'low',
      title: 'Ontario Standard Lease Form Required',
      patterns: [
        /this\s+(?:lease|agreement)\s+supersedes?\s+the\s+(?:ontario\s+)?standard\s+(?:lease|form)/i,
        /in\s+lieu\s+of\s+the\s+(?:ontario\s+)?standard\s+(?:lease|form)/i,
      ],
      description:
        'Most Ontario residential landlords are required to use the provincial Standard Lease Form (Form 2229E). Clauses that try to override or replace the standard form may be unenforceable.',
      legislation: 'Section 12.1, Residential Tenancies Act, 2006',
      recommendation:
        'You have the right to request the Standard Lease Form in writing. If the landlord doesn\'t provide it within 21 days, you can withhold one month\'s rent. Get a copy at ontario.ca/standardlease.',
      actionable: true,
      isBill60: false,
    },
    {
      id: 'on_illegal_rent_form',
      category: 'Rent',
      severity: 'medium',
      title: 'Mandatory Post-Dated Cheques or Single Payment Method',
      patterns: [
        /tenant\s+(?:shall|must|will|agrees?\s+to)\s+(?:provide|give|submit)\s+post-?dated\s+(?:cheques?|checks?)\b/i,
        /payment\s+(?:by\s+)?(?:only\s+)?(?:cash|e-?transfer|cheque|check)\s+only\b/i,
        /no\s+(?:other\s+)?method\s+of\s+payment\s+(?:shall\s+be\s+)?accepted\b/i,
      ],
      description:
        'Landlords cannot require post-dated cheques as the only payment method. Tenants have the right to choose how they pay, and landlords must accept any lawful form of payment.',
      legislation: 'Section 108, Residential Tenancies Act, 2006',
      recommendation:
        'You cannot be forced to provide post-dated cheques. If you do provide them, the landlord must still give you a receipt for each one cashed.',
      actionable: true,
      isBill60: false,
    },
  ],
};
