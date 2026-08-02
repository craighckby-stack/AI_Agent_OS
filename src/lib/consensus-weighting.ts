/**
 * CONSENSUS WEIGHTING ENGINE
 * Role: Implements dynamic consensus weighting, entropy penalties, and historical accuracy tracking.
 * Connected to: Concept/consensus-weighting-spec.md
 */

export interface AgentDecision {
  agentId: string;
  decision: string;
  confidence: number; // c_i in [0, 1]
}

export interface AgentHistory {
  historicalAccuracy: number; // H_i in [0, 1]
  lastUpdated: number;
}

export interface ConsensusConfig {
  alpha: number; // Historical discount factor (typically 0.9)
  beta: number;  // Entropy penalty scaling factor
}

export interface ConsensusResult {
  consensusDecision: string;
  weights: Record<string, number>;
  adjustedWeights: Record<string, number>;
  entropies: Record<string, number>;
  telemetry: {
    durationMs: number;
    timestamp: string;
    totalAgents: number;
  };
}

export class ConsensusWeightingEngine {
  private historyMap: Map<string, AgentHistory> = new Map();
  private config: ConsensusConfig;

  constructor(config: Partial<ConsensusConfig> = {}) {
    this.config = {
      alpha: config.alpha ?? 0.9,
      beta: config.beta ?? 0.1,
    };
  }

  public getHistory(agentId: string): AgentHistory {
    if (!this.historyMap.has(agentId)) {
      this.historyMap.set(agentId, { historicalAccuracy: 1.0, lastUpdated: Date.now() });
    }
    return this.historyMap.get(agentId)!;
  }

  public updateHistory(agentId: string, success: boolean): void {
    const history = this.getHistory(agentId);
    const S = success ? 1.0 : 0.0;
    const newAccuracy = this.config.alpha * history.historicalAccuracy + (1 - this.config.alpha) * S;
    this.historyMap.set(agentId, {
      historicalAccuracy: Math.max(0, Math.min(1, newAccuracy)),
      lastUpdated: Date.now(),
    });
  }

  public computeConsensus(decisions: AgentDecision[]): ConsensusResult {
    const startTime = performance.now();
    const n = decisions.length;
    if (n === 0) {
      throw new Error("Cannot compute consensus with zero decisions.");
    }

    const weights: Record<string, number> = {};
    const adjustedWeights: Record<string, number> = {};
    const entropies: Record<string, number> = {};

    // 1. Compute base weights: W_i = (H_i * c_i) / sum(H_j * c_j)
    let sumProduct = 0;
    const agentProducts: Record<string, number> = {};

    for (const d of decisions) {
      const history = this.getHistory(d.agentId);
      const product = history.historicalAccuracy * d.confidence;
      agentProducts[d.agentId] = product;
      sumProduct += product;
    }

    // Avoid division by zero if all products are zero
    const denominator = sumProduct === 0 ? 1 : sumProduct;

    for (const d of decisions) {
      weights[d.agentId] = agentProducts[d.agentId] / denominator;
    }

    // 2. Compute entropy penalty and adjusted weights
    for (const d of decisions) {
      const c = Math.max(1e-15, Math.min(1 - 1e-15, d.confidence)); // Avoid ln(0) or ln(1)
      const entropy = -(c * Math.log(c) + (1 - c) * Math.log(1 - c));
      entropies[d.agentId] = entropy;

      const baseWeight = weights[d.agentId];
      const adjusted = baseWeight * (1 - this.config.beta * entropy);
      adjustedWeights[d.agentId] = Math.max(0, adjusted);
    }

    // Normalize adjusted weights
    let sumAdjusted = 0;
    for (const id in adjustedWeights) {
      sumAdjusted += adjustedWeights[id];
    }
    const adjustedDenominator = sumAdjusted === 0 ? 1 : sumAdjusted;
    for (const id in adjustedWeights) {
      adjustedWeights[id] = adjustedWeights[id] / adjustedDenominator;
    }

    // 3. Select consensus decision: D* = argmax sum(W_i_adjusted)
    const decisionScores: Record<string, number> = {};
    for (const d of decisions) {
      const weight = adjustedWeights[d.agentId];
      decisionScores[d.decision] = (decisionScores[d.decision] || 0) + weight;
    }

    let consensusDecision = "";
    let maxScore = -1;
    for (const decision in decisionScores) {
      if (decisionScores[decision] > maxScore) {
        maxScore = decisionScores[decision];
        consensusDecision = decision;
      }
    }

    const durationMs = performance.now() - startTime;

    return {
      consensusDecision,
      weights,
      adjustedWeights,
      entropies,
      telemetry: {
        durationMs: Math.round(durationMs * 1000) / 1000,
        timestamp: new Date().toISOString(),
        totalAgents: n,
      },
    };
  }
}