/**
 * Custom type declarations for react-autocomplete
 * The @types/react-autocomplete package has incompatible types with React 18+
 * This custom declaration provides compatible types for modern React versions.
 */
declare module 'react-autocomplete' {
  import * as React from 'react';

  export interface AutocompleteProps<T = any> {
    value?: string;
    onChange?: (event: React.ChangeEvent<HTMLInputElement>, value: string) => void;
    onSelect?: (value: string, item: T) => void;
    getItemValue?: (item: T) => string;
    items?: T[];
    renderItem?: (item: T, isHighlighted: boolean, styles?: React.CSSProperties) => React.ReactNode;
    renderMenu?: (items: React.ReactNode[], value: string, style: React.CSSProperties) => React.ReactNode;
    inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
    wrapperProps?: React.HTMLAttributes<HTMLDivElement>;
    wrapperStyle?: React.CSSProperties;
    menuStyle?: React.CSSProperties;
    autoHighlight?: boolean;
    selectOnBlur?: boolean;
    open?: boolean;
    debug?: boolean;
    // Custom props used in this codebase
    onSubmit?: () => void;
    onFocus?: (e: React.FocusEvent<HTMLInputElement>) => void;
    onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
    [key: string]: any;
  }

  export interface AutocompleteState {
    isOpen: boolean;
    highlightedIndex: number | null;
  }

  export default class Autocomplete extends React.Component<AutocompleteProps, AutocompleteState> {
    isOpen(): boolean;
    getFilteredItems(props: AutocompleteProps): any[];
    refs: {
      input: HTMLInputElement;
    };
  }
}
