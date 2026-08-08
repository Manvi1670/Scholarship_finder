// Words too common to count as a meaningful course/field match
const STOPWORDS = new Set(['and', 'the', 'of', 'in', 'for', 'a', 'an', 'to', 'students', 'related', 'fields', 'field'])

function tokenize(text) {
    if (!text) return []
    return text
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter(word => word.length > 2 && !STOPWORDS.has(word))
}

// Returns null if the scholarship should be excluded entirely (hard filters),
// otherwise a score breakdown so the frontend can show *why* it matched.
function scoreScholarship(student, scholarship) {
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

    let courseScore = 0
    const courseTokens = tokenize(student.course)
    const eligibilityTokens = new Set([
        ...tokenize(scholarship.eligibilityRaw),
        ...tokenize(scholarship.description),
    ])
    const overlap = courseTokens.filter(t => eligibilityTokens.has(t))
    if (overlap.length > 0) {
        courseScore = 25
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
    return scholarships
        .map(s => {
            const result = scoreScholarship(student, s)
            if (!result) return null
            return { ...s.toObject ? s.toObject() : s, matchScore: result.total, matchBreakdown: result.breakdown }
        })
        .filter(Boolean)
        .sort((a, b) => b.matchScore - a.matchScore)
}

module.exports = { scoreScholarship, matchScholarships, tokenize }