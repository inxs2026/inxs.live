// Feature 1: Clause Legality Checker
// Real-time checking of additional terms against provincial prohibited clauses

const clausePatterns = {
  ON: [
    { pattern: /\bno\s+pets?\b|\bpets?\s+(not\s+)?allowed\b|\bpets?\s+prohibited\b/i, message: 'No-pet clauses are void and unenforceable in Ontario (RTA s.14)', severity: 'illegal' },
    { pattern: /\bsecurity\s+deposit\b|\bdamage\s+deposit\b/i, message: 'Security/damage deposits are prohibited in Ontario. Only last month\'s rent deposit is allowed (RTA s.105-106)', severity: 'illegal' },
    { pattern: /\bpost[\s-]?dated\s+cheque/i, message: 'Cannot require post-dated cheques in Ontario (RTA s.108)', severity: 'illegal' },
    { pattern: /\bguests?\s+(not\s+)?allowed\b|\bno\s+overnight\s+guests?\b|\brestrict.*guests?\b/i, message: 'Restricting guests/occupants is prohibited (RTA s.21)', severity: 'illegal' },
    { pattern: /\btenant\s+(shall|must|will)\s+(pay\s+for\s+)?all\s+repairs\b/i, message: 'Landlord must maintain the unit in good repair. Cannot shift all repair costs to tenant (RTA s.20)', severity: 'illegal' },
    { pattern: /\bautomatic\s+rent\s+increase\b|\brent\s+increase.*without\s+notice\b/i, message: 'Rent increases require 90 days notice and are limited by the annual guideline (RTA s.116-120)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\bno\s+families\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Ontario Human Rights Code)', severity: 'illegal' },
    { pattern: /\bkey\s+deposit.*\$?\d{3,}\b/i, message: 'Key deposits cannot exceed the actual replacement cost of the key (RTA s.109)', severity: 'warning' },
    { pattern: /\blandlord\s+may\s+enter\s+(at\s+)?any\s+time\b|\benter\s+without\s+notice\b/i, message: 'Landlord must give 24 hours written notice and enter between 8am-8pm only (RTA s.25-27)', severity: 'illegal' },
    { pattern: /\bno\s+subletting\b|\bno\s+assignment\b|\bcannot\s+(sublet|assign)\b/i, message: 'Cannot unreasonably refuse subletting or assignment (RTA s.95-98)', severity: 'warning' },
    { pattern: /\bforfeit.*deposit\b|\bdeposit.*non[\s-]?refundable\b/i, message: 'Deposits in Ontario must be refundable. Last month\'s rent deposit must be applied to final month (RTA s.106)', severity: 'illegal' },
  ],
  BC: [
    { pattern: /\bsecurity\s+deposit.*(?:exceed|more\s+than|over).*half\b/i, message: 'Security deposit cannot exceed half month\'s rent (BC RTA s.19)', severity: 'illegal' },
    { pattern: /\bpost[\s-]?dated\s+cheque/i, message: 'Cannot require post-dated cheques in BC', severity: 'illegal' },
    { pattern: /\bautomatic.*terminat/i, message: 'Automatic lease termination clauses are prohibited in BC', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (BC Human Rights Code)', severity: 'illegal' },
    { pattern: /\bno\s+pets?\b|\bpets?\s+prohibited\b/i, message: 'Pet restrictions are allowed in BC but must be clearly stated at lease signing. Pet damage deposit (max half month) may apply.', severity: 'info' },
    { pattern: /\blandlord\s+may\s+enter\s+(at\s+)?any\s+time\b/i, message: 'Landlord must give 24 hours written notice to enter (BC RTA s.29)', severity: 'illegal' },
  ],
  AB: [
    { pattern: /\bsecurity\s+deposit.*(?:exceed|more\s+than|over).*one\s+month\b/i, message: 'Security deposit cannot exceed one month\'s rent (Alberta RTRA s.46)', severity: 'illegal' },
    { pattern: /\bseiz(e|ure).*tenant.*property\b|\block\s*out\b/i, message: 'Seizure of tenant\'s property and lockouts are prohibited (Alberta RTRA)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Alberta Human Rights Act)', severity: 'illegal' },
    { pattern: /\bwaiv(e|ing).*right/i, message: 'Clauses contracting out of the RTRA are void', severity: 'warning' },
  ],
  QC: [
    { pattern: /\bsecurity\s+deposit\b|\bdamage\s+deposit\b|\bkey\s+deposit\b/i, message: 'ALL deposits are prohibited in Quebec (CCQ art. 1904)', severity: 'illegal' },
    { pattern: /\bno\s+children\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited (Quebec Charter)', severity: 'illegal' },
    { pattern: /\blandlord\s+may\s+enter\b|\benter\s+without\b/i, message: 'Landlord cannot enter without consent except in emergency (CCQ art. 1857)', severity: 'illegal' },
    { pattern: /\bwaiv(e|ing).*right|\bgive\s+up.*right/i, message: 'Clauses waiving tenant rights under CCQ are void', severity: 'illegal' },
    { pattern: /\bno\s+(sublet|assignment|cession)\b|\bcannot\s+(sublet|assign|cede)\b/i, message: 'Cannot prohibit lease assignment (cession) — can only set reasonable conditions (CCQ art. 1870-1871)', severity: 'illegal' },
  ],
};

// Fallback patterns that apply to all provinces
const universalPatterns = [
  { pattern: /\bno\s+children\b|\bno\s+families\b|\badults?\s+only\b/i, message: 'Discrimination based on family status is prohibited under Canadian human rights legislation', severity: 'illegal' },
  { pattern: /\bwaiv(e|ing)\s+(all\s+)?rights?\b/i, message: 'Clauses that waive statutory tenant rights are void and unenforceable', severity: 'warning' },
];

export function checkClause(text, provinceCode) {
  if (!text || text.length < 5) return [];

  const results = [];
  const patterns = clausePatterns[provinceCode] || [];
  const allPatterns = [...patterns, ...universalPatterns];

  for (const rule of allPatterns) {
    const match = text.match(rule.pattern);
    if (match) {
      // Avoid duplicate messages
      if (!results.find(r => r.message === rule.message)) {
        results.push({
          severity: rule.severity,
          message: rule.message,
          matchedText: match[0],
          index: match.index,
        });
      }
    }
  }

  return results;
}

export function renderClauseWarnings(warnings) {
  if (!warnings.length) return '';

  return warnings.map(w => {
    const icon = w.severity === 'illegal' ? '&#9888;' : w.severity === 'warning' ? '&#9432;' : '&#8505;';
    const cls = w.severity === 'illegal' ? 'clause-illegal' : w.severity === 'warning' ? 'clause-warning' : 'clause-info';
    return `<div class="clause-alert ${cls}"><span>${icon}</span> <strong>${w.severity === 'illegal' ? 'ILLEGAL' : w.severity === 'warning' ? 'WARNING' : 'INFO'}:</strong> ${w.message}</div>`;
  }).join('');
}
