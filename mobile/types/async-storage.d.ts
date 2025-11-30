declare module '@react-native-async-storage/async-storage' {
  export interface AsyncStorageStatic {
    /**
     * Fetches key and passes the result to callback, along with an Error if there is any.
     */
    getItem(key: string, callback?: (error?: Error, result?: string | null) => void): Promise<string | null>;

    /**
     * Sets value for key and calls callback on completion, along with an Error if there is any.
     */
    setItem(key: string, value: string, callback?: (error?: Error) => void): Promise<void>;

    /**
     * Removes an item for a key and invokes a callback upon completion.
     */
    removeItem(key: string, callback?: (error?: Error) => void): Promise<void>;

    /**
     * Merges existing value with input value, assuming they are stringified json. Returns a Promise object.
     */
    mergeItem(key: string, value: string, callback?: (error?: Error) => void): Promise<void>;

    /**
     * Erases all AsyncStorage for all clients, libraries, etc.
     */
    clear(callback?: (error?: Error) => void): Promise<void>;

    /**
     * Gets all keys known to the app, for all callers, libraries, etc.
     */
    getAllKeys(callback?: (error?: Error, keys?: readonly string[]) => void): Promise<readonly string[]>;

    /**
     * multiGet invokes callback with key-value array pairs found in storage.
     */
    multiGet(
      keys: readonly string[],
      callback?: (errors?: readonly Error[], result?: readonly [string, string | null][]) => void
    ): Promise<readonly [string, string | null][]>;

    /**
     * multiSet and multiMerge take arrays of key-value array pairs that match the output of multiGet.
     */
    multiSet(
      keyValuePairs: readonly [string, string][],
      callback?: (errors?: readonly Error[]) => void
    ): Promise<void>;

    /**
     * Delete all the keys in the keys array.
     */
    multiRemove(keys: readonly string[], callback?: (errors?: readonly Error[]) => void): Promise<void>;

    /**
     * Batch operation to merge in existing and new values for a given set of keys.
     */
    multiMerge(
      keyValuePairs: readonly [string, string][],
      callback?: (errors?: readonly Error[]) => void
    ): Promise<void>;

    /**
     * This allows you to batch the fetching of items given an array of key inputs.
     */
    flushGetRequests(): void;
  }

  const AsyncStorage: AsyncStorageStatic;
  export default AsyncStorage;
}
