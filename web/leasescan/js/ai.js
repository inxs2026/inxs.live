// LeaseScan — Chrome Built-in AI (Prompt API) Integration
// Uses window.ai.languageModel (Gemini Nano, Chrome 127+)
// Falls back gracefully — the rules engine always runs first.

/**
 * Check whether Chrome's built-in AI is available in this browser.
 * @returns {Promise<boolean>}
 */
export async function isAIAvailable() {
  if (typeof window === 'undefined') return false;
  if (!window.ai?.languageModel) return false;
  try {
    const caps = await window.ai.languageModel.capabilities();
    return caps.available !== 'no';
  } catch {
    return false;
  }
}

/**
 * Use Chrome's built-in AI to enhance the scan with additional findings
 * that the rules engine may have missed.
 *
 * @param {string} leaseText - The raw lease text
 * @param {import('./scanner.js').ScanResult} scanResult - Already-computed rule-based results
 * @returns {Promise<string|null>} Plain-English additional findings, or null if AI unavailable
 */
export async function aiEnhance(leaseText, scanResult) {
  if (!(await isAIAvailable())) return null;

  try {
    const session = await window.ai.languageModel.create({
      systemPrompt: buildSystemPrompt(scanResult.province),
    });

    const alreadyFound = scanResult.flags.map((f) => f.title).join('; ');
    const truncated = leaseText.length > 10000 ? leaseText.substring(0, 10000) + '…' : leaseText;

    const prompt = `I have already flagged the following issues in this ${scanResult.province} lease: ${alreadyFound}.

Please identify up to 5 ADDITIONAL unusual, unfair, or potentially illegal clauses that I may have missed.
Focus on clauses that are non-standard, surprising, or that tenants often overlook.
For each finding, give: (1) a short title, (2) one sentence explaining why it is concerning, (3) the relevant law if you know it.
Format as a numbered list. If you find nothing additional, say "No additional concerns found."

LEASE TEXT:
${truncated}`;

    const response = await session.prompt(prompt);
    await session.destroy();
    return response.trim() || null;
  } catch (err) {
    console.warn('[LeaseScan] AI enhancement failed:', err);
    return null;
  }
}

// ── Private ────────────────────────────────────────────────────────────────────

function buildSystemPrompt(province) {
  const provinceMap = {
    Ontario: 'Ontario (Residential Tenancies Act, 2006, and Bill 60 2025 amendments)',
    'British Columbia': 'British Columbia (Residential Tenancy Act, RSBC 2002)',
    Alberta: 'Alberta (Residential Tenancies Act, RSA 2000)',
  };
  const law = provinceMap[province] ?? province;

  return `You are an expert tenant rights paralegal specializing in Canadian residential tenancy law, specifically ${law}.
Your job is to review lease text and identify clauses that are illegal, unenforceable, unusual, or unfair to tenants.
Always cite specific legislation by section number when possible.
Be concise, plain-spoken, and actionable. Do not give general legal disclaimers.
Only flag genuine concerns — not standard boilerplate clauses that are normal in residential leases.`;
}
