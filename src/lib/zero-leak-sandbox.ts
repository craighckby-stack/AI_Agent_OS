/**
 * ZERO-LEAK SANDBOX ENGINE
 * Role: Implements WeakMap-based execution context sandboxing to prevent memory leaks.
 * Connected to: Concept/consensus-weighting-spec.md
 */

export interface ExecutionContext {
  id: string;
  startTime: number;
  logs: string[];
  state: Record<string, any>;
  metadata: Record<string, any>;
}

export class ZeroLeakSandbox<AgentKey extends object> {
  private contexts = new WeakMap<AgentKey, ExecutionContext>();
  private activeCount = 0;

  /**
   * Registers a new agent instance and initializes its execution context.
   */
  public register(agent: AgentKey, id: string, initialState: Record<string, any> = {}): void {
    if (this.contexts.has(agent)) {
      throw new Error(`Agent context already registered for ID: ${id}`);
    }

    const context: ExecutionContext = {
      id,
      startTime: Date.now(),
      logs: [],
      state: initialState,
      metadata: {
        registeredAt: new Date().toISOString(),
        threadId: Math.random().toString(36).substring(2, 15),
      },
    };

    this.contexts.set(agent, context);
    this.activeCount++;
  }

  /**
   * Retrieves the execution context for a given agent.
   */
  public getContext(agent: AgentKey): ExecutionContext {
    const context = this.contexts.get(agent);
    if (!context) {
      throw new Error("Agent context not found or has been garbage collected.");
    }
    return context;
  }

  /**
   * Appends a log entry to the agent's context.
   */
  public log(agent: AgentKey, message: string): void {
    const context = this.getContext(agent);
    context.logs.push(`[${new Date().toISOString()}] ${message}`);
  }

  /**
   * Updates the state of the agent's context.
   */
  public updateState(agent: AgentKey, updates: Record<string, any>): void {
    const context = this.getContext(agent);
    context.state = { ...context.state, ...updates };
  }

  /**
   * Explicitly removes an agent's context (optional, since WeakMap garbage collects automatically).
   */
  public decommission(agent: AgentKey): void {
    if (this.contexts.delete(agent)) {
      this.activeCount = Math.max(0, this.activeCount - 1);
    }
  }

  /**
   * Returns the count of active contexts registered in this session.
   * Note: This only tracks manually registered/decommissioned counts,
   * as WeakMap does not expose actual garbage collection state.
   */
  public getActiveCount(): number {
    return this.activeCount;
  }
}