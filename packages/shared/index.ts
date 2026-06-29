export interface CognitiveMetrics {
  latencyMs: number;
  contextAccuracy: number;
  tokenUsage: number;
}

export const calculateImprovement = (baseline: number, current: number): number => {
  return ((baseline - current) / baseline) * 100;
};
