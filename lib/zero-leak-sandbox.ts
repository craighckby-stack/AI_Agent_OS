/**
 * @file zero-leak-sandbox.ts
 * @description WeakMap-backed execution isolation to prevent memory leaks during dynamic module loading.
 */

export class ZeroLeakSandbox {
  // WeakMap ensures that once the context object is dereferenced, its metadata is garbage collected
  private activeContexts: WeakMap<object, Record<string, any>> = new WeakMap();

  public createContext(owner: object, initialMetadata: Record<string, any> = {}): void {
    this.activeContexts.set(owner, {
      ...initialMetadata,
      createdAt: Date.now(),
    });
  }

  public getContext(owner: object): Record<string, any> | undefined {
    return this.activeContexts.get(owner);
  } 

  public updateContext(owner: object, updates: Record<string, any>): void {
    const current = this.activeContexts.get(owner);
    if (current) {
      this.activeContexts.set(owner, { ...current, ...updates });
    }
  }
}
