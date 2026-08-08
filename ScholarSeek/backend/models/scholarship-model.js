const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const scholarshipSchema = new Schema({
    name: String,
    sourceUrl: { type: String, unique: true },   // dedup key, matches the scraper
    region: String,
    eligibilityRaw: String,
    minCPI: Number,
    awardRaw: String,
    awardAmountINR: Number,
    awardCategory: String,
    deadlineRaw: String,
    deadline: Date,
    description: String,
    applyLink: String,
    contactEmail: String,
    contactPhone: String,
    scrapedAt: Date,
})

const Scholarship = mongoose.model("Scholarship", scholarshipSchema, "scholarships")

module.exports = Scholarship