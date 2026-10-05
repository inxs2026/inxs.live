// LeaseScan — Core Scanning Engine

import { ontarioRules } from './rules/ontario.js';
import { bcRules } from './rules/bc.js';
import { albertaRules } from './rules/alberta.js';

const PROVINCE_RULES = {
  ontario: ontarioRules,
  bc: bcRules,
  alberta: albertaRules,
};

/**
 * Scan a lease text against all rules for the selected province.
 * @param {string} text - Raw lease text
 * @param {string} province - Province key ('ontario' | 'bc' | 'alberta')
 * @returns {ScanResult}
 */
export function scanLease(text, province) {
  const ruleSet = PROVINCE_RULES[province];
  if (!ruleSet) throw new Error(`Unknown province: ${province}`);

  const flags = [];

  for (const rule of ruleSet.rules) {
    const matches = findMatches(text, rule);
    if (matches.length > 0) {
      flags.push({ ...rule, matches });
    }
  }

  // Sort: high → medium → low, then bill60 last within each group
  flags.sort((a, b) => {
    const severityOrder = { high: 0, medium: 1, low: 2 };
    const sev = severityOrder[a.severity] - severityOrder[b.severity];
    if (sev !== 0) return sev;
    return (a.isBill60 ? 1 : 0) - (b.isBill60 ? 1 : 0);
  });

  const highCount = flags.filter((f) => f.severity === 'high').length;
  const medCount = flags.filter((f) => f.severity === 'medium').length;
  const lowCount = flags.filter((f) => f.severity === 'low').length;

  return {
    province: ruleSet.province,
    legislation: ruleSet.legislation,
    legalAidUrl: ruleSet.legalAidUrl,
    scannedAt: new Date().toISOString(),
    wordCount: countWords(text),
    summary: {
      total: flags.length,
      high: highCount,
      medium: medCount,
      low: lowCount,
      verdict: getVerdict(highCount, medCount),
      verdictText: getVerdictText(highCount, medCount),
    },
    flags,
  };
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function findMatches(text, rule) {
  const results = [];
  const seen = new Set(); // de-dupe by approximate position

  for (const pattern of rule.patterns) {
    // Reset lastIndex for global patterns
    const re = new RegExp(pattern.source, pattern.flags.includes('g') ? pattern.flags : pattern.flags + 'g');
    let match;
    while ((match = re.exec(text)) !== null) {
      const bucket = Math.floor(match.index / 100); // coarse de-dupe
      if (seen.has(bucket)) continue;
      seen.add(bucket);

      results.push({
        matchedText: match[0],
        context: extractContext(text, match.index, match[0].length),
        position: match.index,
      });

      // Cap at 3 examples per rule to avoid noise
      if (results.length >= 3) break;
    }
    if (results.length >= 3) break;
  }

  return results;
}

/**
 * Extract a readable snippet around a match, trimmed to sentence boundaries.
 */
function extractContext(text, matchIndex, matchLength, radius = 280) {
  const rawStart = Math.max(0, matchIndex - radius);
  const rawEnd = Math.min(text.length, matchIndex + matchLength + radius);

  let snippet = text.substring(rawStart, rawEnd);

  // Trim to the nearest sentence start / end for cleaner display
  if (rawStart > 0) {
    const firstPeriod = snippet.search(/[.!?]\s/);
    if (firstPeriod !== -1 && firstPeriod < radius / 2) {
      snippet = snippet.substring(firstPeriod + 2);
    }
    snippet = '\u2026' + snippet.trimStart();
  }

  if (rawEnd < text.length) {
    const lastPeriod = snippet.lastIndexOf('. ');
    if (lastPeriod !== -1 && lastPeriod > snippet.length - radius / 2) {
      snippet = snippet.substring(0, lastPeriod + 1);
    }
    snippet = snippet.trimEnd() + '\u2026';
  }

  return snippet.replace(/\s+/g, ' ').trim();
}

function countWords(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function getVerdict(high, medium) {
  if (high >= 4) return 'serious';
  if (high >= 2 || medium >= 4) return 'concerns';
  if (high >= 1 || medium >= 1) return 'minor';
  return 'clean';
}

function getVerdictText(high, medium) {
  if (high >= 4)
    return 'This lease has serious legal issues. Do not sign without consulting a tenant rights organization.';
  if (high >= 2 || medium >= 4)
    return 'This lease contains significant concerns that should be addressed before signing.';
  if (high >= 1 || medium >= 1)
    return 'This lease has some clauses worth reviewing. Most are addressable before signing.';
  return 'No major red flags detected. Always read the full lease carefully before signing.';
}
