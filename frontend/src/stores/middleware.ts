import { type StateCreator } from 'zustand'
import { devtools, persist, type PersistOptions } from 'zustand/middleware'

/**
 * Composes devtools + persist middleware for any Zustand store.
 * Usage:
 *   create<MyState>()(withPersist('my-store', initializer))
 */
export function withPersist<T extends object>(
  name: string,
  initializer: StateCreator<T, [['zustand/devtools', never], ['zustand/persist', unknown]]>,
  persistOptions?: Partial<PersistOptions<T>>,
): StateCreator<T, [], [['zustand/devtools', never], ['zustand/persist', unknown]]> {
  return devtools(
    persist(initializer, { name, ...persistOptions }),
    { name },
  )
}
