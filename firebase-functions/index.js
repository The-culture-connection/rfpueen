// Firebase Functions for RFP Queen - Optimized Matching & Calculations
// Deploy with: firebase deploy --only functions

const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

const COLLECTION_MAP = {
    "Contracts": ["SAM"],
    "Grants": ["grants.gov", "grantwatch"],
    "RFPs": ["PND_RFPs", "rfpmart"],
    "Bids": ["bid"]
};

/**
 * Calculate urgency bucket based on deadline
 */
function bucketOf(deadline) {
    if (!deadline) return "ongoing";
    const deadlineDate = deadline.toDate ? deadline.toDate() : new Date(deadline);
    const now = new Date();
    const daysUntil = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24));
    
    if (daysUntil <= 30) return "urgent";
    if (daysUntil <= 92) return "soon";
    return "ongoing";
}

/**
 * Calculate match score for an opportunity
 */
function calculateMatchScore(opportunity, profile) {
    let score = 0.0;
    
    const searchText = [
        opportunity.title || '',
        opportunity.description || '',
        opportunity.summary || '',
        opportunity.agency || '',
        opportunity.department || ''
    ].join(' ').toLowerCase();
    
    const interestsMain = profile.interestsMain || [];
    const interestsSub = profile.interestsSub || [];
    const grantsByInterest = profile.grantsByInterest || [];
    
    const allKeywords = [
        ...interestsMain.map(k => k.toLowerCase()),
        ...interestsSub.map(k => k.toLowerCase()),
        ...grantsByInterest.map(k => k.toLowerCase())
    ];
    
    // Remove duplicates
    const uniqueKeywords = [...new Set(allKeywords)];
    
    if (uniqueKeywords.length === 0) return 0.0;
    
    // Count keyword matches
    let keywordMatches = 0;
    uniqueKeywords.forEach(keyword => {
        if (!keyword) return;
        const regex = new RegExp(`\\b${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
        const matches = searchText.match(regex);
        if (matches) keywordMatches += matches.length;
    });
    
    score += keywordMatches * 10;
    
    // Boost for main interests
    interestsMain.forEach(keyword => {
        if (keyword && searchText.includes(keyword.toLowerCase())) {
            score += 5;
        }
    });
    
    // Urgency boost
    const deadline = opportunity.closeDate || opportunity.deadline;
    const bucket = bucketOf(deadline);
    if (bucket === "urgent") score += 5;
    else if (bucket === "soon") score += 2;
    
    return score;
}

/**
 * Calculate win rate with reasoning
 */
function calculateWinRate(opportunity, profile, matchScore) {
    let baseRate = Math.min(100, (matchScore / 200) * 100);
    
    const searchText = [
        opportunity.title || '',
        opportunity.description || '',
        opportunity.summary || ''
    ].join(' ').toLowerCase();
    
    const interestsMain = profile.interestsMain || [];
    const interestsSub = profile.interestsSub || [];
    
    const mainMatches = interestsMain.filter(k => k && searchText.includes(k.toLowerCase())).length;
    const subMatches = interestsSub.filter(k => k && searchText.includes(k.toLowerCase())).length;
    
    let keywordFactor = 0;
    if (mainMatches > 0) {
        keywordFactor += 15;
    }
    if (subMatches > 0) {
        keywordFactor += 10;
    }
    
    const deadline = opportunity.closeDate || opportunity.deadline;
    const bucket = bucketOf(deadline);
    let urgencyFactor = 0;
    if (bucket === "urgent") urgencyFactor = 5;
    else if (bucket === "soon") urgencyFactor = 3;
    else urgencyFactor = 2;
    
    const applicationUrl = opportunity.applicationUrl || opportunity.applyUrl || opportunity.formUrl;
    const formFactor = applicationUrl ? 10 : -5;
    
    let scoreFactor = 0;
    if (matchScore >= 50) scoreFactor = 15;
    else if (matchScore >= 20) scoreFactor = 10;
    else if (matchScore > 0) scoreFactor = 5;
    else scoreFactor = -10;
    
    const winRate = Math.max(0, Math.min(100, baseRate + keywordFactor + urgencyFactor + formFactor + scoreFactor));
    
    const reasoningParts = [];
    if (mainMatches > 0) reasoningParts.push(`Matches ${mainMatches} main interest(s)`);
    if (subMatches > 0) reasoningParts.push(`Matches ${subMatches} sub-interest(s)`);
    if (bucket === "urgent") reasoningParts.push("Urgent deadline (within 30 days)");
    else if (bucket === "soon") reasoningParts.push("Approaching deadline (within 92 days)");
    else reasoningParts.push("Ongoing opportunity");
    if (applicationUrl) reasoningParts.push("Direct application form available");
    else reasoningParts.push("Application form not directly available");
    if (matchScore >= 50) reasoningParts.push("Strong keyword match");
    else if (matchScore >= 20) reasoningParts.push("Moderate keyword match");
    else if (matchScore > 0) reasoningParts.push("Weak keyword match");
    else reasoningParts.push("No keyword matches found");
    
    let reasoning = "Win rate calculated based on: " + reasoningParts.join("; ") + ".";
    
    if (winRate >= 70) reasoning += " High probability of success - strong match.";
    else if (winRate >= 50) reasoning += " Moderate probability of success - good match.";
    else if (winRate >= 30) reasoning += " Lower probability - weak match.";
    else reasoning += " Low probability - poor match.";
    
    return {
        winRate: Math.round(winRate * 10) / 10,
        reasoning: reasoning,
        factors: {
            baseRate: Math.round(baseRate * 10) / 10,
            keywordFactor,
            urgencyFactor,
            formFactor,
            scoreFactor
        }
    };
}

/**
 * Match opportunities HTTP Cloud Function
 */
exports.matchOpportunities = functions.https.onRequest(async (req, res) => {
    // Enable CORS
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(204).send('');
        return;
    }
    
    if (req.method !== 'POST') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        const { fundingTypes, interestsMain, interestsSub, grantsByInterest, userId } = req.body;
        
        if (!fundingTypes || fundingTypes.length === 0) {
            res.status(400).json({ error: 'No funding types provided' });
            return;
        }
        
        const profile = {
            fundingTypes,
            interestsMain: interestsMain || [],
            interestsSub: interestsSub || [],
            grantsByInterest: grantsByInterest || []
        };
        
        // Get collections to search
        const collectionsToSearch = new Set();
        fundingTypes.forEach(ft => {
            const cols = COLLECTION_MAP[ft] || [];
            cols.forEach(c => collectionsToSearch.add(c));
        });
        
        // Fetch opportunities from Firestore
        const db = admin.firestore();
        const allOpportunities = [];
        
        for (const collectionName of collectionsToSearch) {
            try {
                const snapshot = await db.collection(collectionName).get();
                snapshot.forEach(doc => {
                    const data = doc.data();
                    const score = calculateMatchScore(data, profile);
                    if (score > 0) {
                        allOpportunities.push({
                            id: doc.id,
                            collection: collectionName,
                            score: score,
                            urgency_bucket: bucketOf(data.closeDate || data.deadline),
                            ...data
                        });
                    }
                });
            } catch (error) {
                console.error(`Error fetching ${collectionName}:`, error);
            }
        }
        
        // Sort by score
        allOpportunities.sort((a, b) => b.score - a.score);
        
        // Filter out applied/saved if userId provided
        let filtered = allOpportunities;
        if (userId) {
            const [appliedSnap, savedSnap] = await Promise.all([
                db.collection('profiles').doc(userId).collection('Applied').get(),
                db.collection('profiles').doc(userId).collection('Saved').get()
            ]);
            
            const appliedIds = new Set(appliedSnap.docs.map(d => d.id));
            const savedIds = new Set(savedSnap.docs.map(d => d.id));
            
            filtered = allOpportunities.filter(o => 
                !appliedIds.has(o.id) && !savedIds.has(o.id)
            );
        }
        
        // Calculate win rates
        filtered.forEach(opp => {
            const winRateData = calculateWinRate(opp, profile, opp.score);
            opp.win_rate = winRateData.winRate;
            opp.win_rate_reasoning = winRateData.reasoning;
        });
        
        res.json({
            opportunities: filtered.slice(0, 50),
            total: filtered.length
        });
        
    } catch (error) {
        console.error('Error matching opportunities:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Calculate win rate HTTP Cloud Function
 */
exports.calculateWinRate = functions.https.onRequest(async (req, res) => {
    res.set('Access-Control-Allow-Origin', '*');
    res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(204).send('');
        return;
    }
    
    if (req.method !== 'POST') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    try {
        const { opportunity, profile, matchScore } = req.body;
        
        const winRateData = calculateWinRate(opportunity, profile, matchScore || 0);
        
        res.json(winRateData);
    } catch (error) {
        console.error('Error calculating win rate:', error);
        res.status(500).json({ error: error.message });
    }
});
