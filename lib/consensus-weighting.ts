/**
 * @file consensus-weighting.ts
 * @description Dynamic consensus weighting for multi-agent validation and fallback.
 */

export interface AgentProposal {
  agentId: string;
  confidence: number; // 0.0 to 1.0
  value: any;
}

export class ConsensusWeightingEngine {
  /**
   * Resolves consensus among multiple agent proposals based on dynamic confidence weighting.
   */
  public static resolveConsensus<T>(proposals: AgentProposal[]): T | null {
    if (proposals.length === 0) return null;

    const weights: Map<any, number> = new Map();

    for (const proposal of proposals) {
      const currentWeight = weights.get(proposal.value) || 0;
      weights.set(proposal.value, currentWeight + proposal.confidence);
    }

    let bestValue: T | null = null;
    let maxWeight = -1;

    for (const [value, weight] of weights.entries()) {
      if (weight > maxWeight) {
        maxWeight = weight;
        bestValue = value;
      }
    }

    return bestValue;
  }
}
