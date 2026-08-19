// Words too common to count as a meaningful course/field match
const STOPWORDS = new Set(['and', 'the', 'of', 'in', 'for', 'a', 'an', 'to', 'students', 'related', 'fields', 'field'])

function tokenize(text) {
    if (!text) return []
    return text
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter(word => word.length > 2 && !STOPWORDS.has(word))
}

// --- TF-IDF helpers -------------------------------------------------------
// Replaces plain token-overlap with weighted similarity so common words
// (e.g. "engineering") don't count as much as rare, distinctive ones
// (e.g. "biotechnology"), and near-miss wording still scores partial credit
// instead of an all-or-nothing 25/10/0.

function termFrequency(tokens) {
    const tf = new Map()
    tokens.forEach(t => tf.set(t, (tf.get(t) || 0) + 1))
    // normalize by doc length so long descriptions don't auto-win
    tf.forEach((count, term) => tf.set(term, count / tokens.length))
    return tf
}

// idf across the whole scholarship corpus: rare words get a higher weight
function buildIdf(allDocsTokens) {
    const df = new Map()
    allDocsTokens.forEach(tokens => {
        new Set(tokens).forEach(t => df.set(t, (df.get(t) || 0) + 1))
    })
    const idf = new Map()
    const N = allDocsTokens.length || 1
    df.forEach((count, term) => idf.set(term, Math.log((N + 1) / (count + 1)) + 1))
    return idf
}

function tfidfVector(tokens, idf) {
    const tf = termFrequency(tokens)
    const vec = new Map()
    tf.forEach((freq, term) => vec.set(term, freq * (idf.get(term) || 0)))
    return vec
}

function cosineSimilarity(vecA, vecB) {
    let dot = 0, magA = 0, magB = 0
    vecA.forEach((val, term) => {
        magA += val * val
        if (vecB.has(term)) dot += val * vecB.get(term)
    })
    vecB.forEach(val => { magB += val * val })
    if (magA === 0 || magB === 0) return 0
    return dot / (Math.sqrt(magA) * Math.sqrt(magB))
}

// Returns null if the scholarship should be excluded entirely (hard filters),
// otherwise a score breakdown so the frontend can show *why* it matched.
// `idf` is precomputed once per matchScholarships() call over the whole
// scholarship list, then reused for every student x scholarship comparison.
function scoreScholarship(student, scholarship, idf) {
    // Hard filter 1: don't recommend scholarships that are already closed
    if ((scholarship.deadlineRaw || '').trim().toLowerCase() === 'closed') {
        return null
    }

    // Hard filter 2: if there's a real CPI requirement and the student
    // doesn't meet it, this scholarship genuinely isn't open to them
    const studentCpi = parseFloat(student.cpi)
    const hasCpiRequirement = typeof scholarship.minCPI === 'number'
    if (hasCpiRequirement && !isNaN(studentCpi) && studentCpi < scholarship.minCPI) {
        return null
    }

    // Course / field match — now TF-IDF cosine similarity instead of
    // raw token overlap, so "Computing" vs "Computer Science" gets partial
    // credit instead of scoring 0, and common words like "engineering"
    // matter less than distinctive ones like "biotechnology".
    let courseScore = 0
    const courseTokens = tokenize(student.course)
    const eligibilityTokens = [
        ...tokenize(scholarship.eligibilityRaw),
        ...tokenize(scholarship.description),
    ]
    if (eligibilityTokens.length > 0 && courseTokens.length > 0) {
        const queryVec = tfidfVector(courseTokens, idf)
        const docVec = tfidfVector(eligibilityTokens, idf)
        const similarity = cosineSimilarity(queryVec, docVec) // 0..1
        courseScore = Math.round(similarity * 25)
    } else if (!scholarship.eligibilityRaw) {
        courseScore = 10  // no eligibility text at all - can't rule it out, small neutral credit
    }

    let regionScore = 0
    if (scholarship.region && student.region) {
        const schRegion = scholarship.region.toLowerCase()
        const stuRegion = student.region.toLowerCase()
        if (schRegion.includes(stuRegion) || stuRegion.includes(schRegion) || schRegion === 'abroad') {
            regionScore = 20
        }
    }

    let cpiScore = hasCpiRequirement ? 15 : 10  // met a real requirement, or no requirement to worry about

    let urgencyScore = 5  // default/neutral - covers "Always Open" and unparseable-but-not-closed dates
    if (scholarship.deadline) {
        const daysLeft = (new Date(scholarship.deadline) - new Date()) / (1000 * 60 * 60 * 24)
        if (daysLeft > 0) {
            // closer deadlines score higher, capped at 15, floor of 2 for anything far out
            urgencyScore = Math.max(2, Math.min(15, Math.round(15 - daysLeft / 10)))
        }
    }

    // Amount is on wildly different scales (thousands to lakhs), so bucket
    // it into tiers rather than using the raw number directly - a flat
    // linear score would let one huge outlier dominate every other factor.
    let amountScore = 3  // baseline for non-monetary or unrecognized award text
    if (typeof scholarship.awardAmountINR === 'number') {
        const amt = scholarship.awardAmountINR
        if (amt >= 500000) amountScore = 15
        else if (amt >= 100000) amountScore = 12
        else if (amt >= 25000) amountScore = 8
        else if (amt > 0) amountScore = 5
    }

    const total = courseScore + regionScore + cpiScore + urgencyScore + amountScore

    return {
        total,
        breakdown: { courseScore, regionScore, cpiScore, urgencyScore, amountScore },
    }
}

function matchScholarships(student, scholarships) {
    // Build the IDF table once, over every scholarship's eligibility +
    // description text, so rare/distinctive terms are weighted correctly.
    const allDocsTokens = scholarships.map(s => [
        ...tokenize(s.eligibilityRaw),
        ...tokenize(s.description),
    ])
    const idf = buildIdf(allDocsTokens)

    return scholarships
        .map(s => {
            const result = scoreScholarship(student, s, idf)
            if (!result) return null
            return { ...s.toObject ? s.toObject() : s, matchScore: result.total, matchBreakdown: result.breakdown }
        })
        .filter(Boolean)
        .sort((a, b) => b.matchScore - a.matchScore)
}

module.exports = { scoreScholarship, matchScholarships, tokenize }