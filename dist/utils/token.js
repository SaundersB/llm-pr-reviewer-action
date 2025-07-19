"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.countTokens = countTokens;
function countTokens(text) {
    // Rough token estimation: 1 token per 4 characters
    return Math.ceil(text.length / 4);
}
